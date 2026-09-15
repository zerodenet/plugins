#!/usr/bin/env python3
"""Validate marketplace Issues and apply maintainer label decisions."""
import base64
import json
import os
from pathlib import Path
import re

from github_api import GitHub, GitHubError, decode_json, segment
from marketplace_schema import HOSTS, project_host, require
from release_metadata import append_product, listing_product, replace_product, submission

ROOT = Path(__file__).resolve().parents[1]
STATES = {"status:needs-info", "status:in-review", "status:accepted", "status:closed"}
HOST_LABELS = {"host:zboard", "host:znet-sink"}
APPLICATION_LABELS = {"submission": "plugin:submission", "update": "plugin:update"}
ACCEPTED = "status:accepted"
CLOSED = "status:closed"
PUBLICATION_WORKFLOW = "publish-marketplace.yml"


def application_kind(issue):
    if issue.get("pull_request"):
        return None
    labels = {label["name"] for label in issue["labels"]}
    if "plugin:update" in labels or issue["title"].startswith("[Plugin update]"):
        return "update"
    if "plugin:submission" in labels or issue["title"].startswith("[Plugin]"):
        return "submission"
    return None


def is_submission(issue):
    return application_kind(issue) is not None


def label_names(issue):
    return {label["name"] for label in issue.get("labels", [])}


def management_action(event):
    """Return a human maintainer decision carried by one management label event."""
    if event.get("action") != "labeled" or event.get("sender", {}).get("type") != "User":
        return None
    name = event.get("label", {}).get("name")
    return name if name in {ACCEPTED, CLOSED} else None


def catalog_documents(registry):
    """Render the authoritative registry and migration-only host projections together."""
    documents = {"catalogs/plugins.json": registry}
    for host in sorted(HOSTS):
        documents[f"catalogs/{host}.json"] = project_host(registry, host)
    return documents


def render_json(document):
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


class Marketplace:
    def __init__(self, github, repository):
        require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository), "invalid market repository")
        self.github, self.repository = github, repository
        self.prefix = f"/repos/{repository}"

    def labels(self):
        existing = {label["name"]: label for label in self.github.pages(self.prefix + "/labels")}
        for label in json.loads((ROOT / ".github/labels.json").read_text()):
            old = existing.get(label["name"])
            if old is None:
                self.github.api(self.prefix + "/labels", "POST", label)
            elif any(old.get(field) != label[field] for field in ("color", "description")):
                self.github.api(self.prefix + "/labels/" + segment(label["name"]), "PATCH", label)

    def status(self, number, state, extra=()):
        path = f"{self.prefix}/issues/{number}"
        current = self.github.api(path)
        names = {label["name"] for label in current["labels"]}
        desired_hosts = set(extra) & HOST_LABELS
        stale_hosts = (names & HOST_LABELS) - desired_hosts if desired_hosts else set()
        for label in sorted(((names & STATES) - {state}) | stale_hosts):
            self.github.api(path + "/labels/" + segment(label), "DELETE")
        add = ({state} | set(extra)) - names
        if add:
            self.github.api(path + "/labels", "POST", {"labels": sorted(add)})

    def comment(self, number, message):
        marker = "<!-- marketplace-automation -->"
        path = f"{self.prefix}/issues/{number}/comments"
        body = marker + "\n" + message
        for comment in self.github.pages(path):
            if comment["user"]["login"] == "github-actions[bot]" and comment["body"].startswith(marker):
                if comment["body"] != body:
                    self.github.api(f"{self.prefix}/issues/comments/{comment['id']}", "PATCH", {"body": body})
                return
        self.github.api(path, "POST", {"body": body})

    def registry(self, ref="main"):
        record = self.github.api(f"{self.prefix}/contents/catalogs/plugins.json?ref={segment(ref)}")
        require(record.get("encoding") == "base64", "registry is not a GitHub text blob")
        return decode_json(base64.b64decode(record["content"])), record["sha"]

    def fresh_approval(self, issue):
        fresh = self.github.api(f"{self.prefix}/issues/{issue['number']}")
        require(fresh.get("body") == issue.get("body") and fresh.get("state") == "open",
                "application changed while admission was running; review it again")
        require(application_kind(fresh) == application_kind(issue),
                "application type changed while admission was running; review it again")
        require(ACCEPTED in label_names(fresh), "maintainer approval label was removed")
        return fresh

    def apply(self, product, issue, kind):
        """Create one atomic main-branch commit without opening an admission PR."""
        base = self.github.api(self.prefix + "/git/ref/heads/main")["object"]["sha"]
        registry, _ = self.registry(base)
        updated = replace_product(registry, product) if kind == "update" else append_product(registry, product)
        if registry == updated:
            return None
        self.fresh_approval(issue)
        base_commit = self.github.api(f"{self.prefix}/git/commits/{base}")
        entries = []
        for path, document in catalog_documents(updated).items():
            blob = self.github.api(self.prefix + "/git/blobs", "POST", {
                "content": render_json(document), "encoding": "utf-8",
            })
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        tree = self.github.api(self.prefix + "/git/trees", "POST", {
            "base_tree": base_commit["tree"]["sha"], "tree": entries,
        })
        verb = "update" if kind == "update" else "list"
        commit = self.github.api(self.prefix + "/git/commits", "POST", {
            "message": f"registry: {verb} {product['id']} (issue #{issue['number']})",
            "tree": tree["sha"], "parents": [base],
            "author": {
                "name": "github-actions[bot]",
                "email": "41898282+github-actions[bot]@users.noreply.github.com",
            },
        })
        self.fresh_approval(issue)
        current = self.github.api(self.prefix + "/git/ref/heads/main")["object"]["sha"]
        require(current == base, "registry changed while admission was running; apply the approval label again")
        self.github.api(self.prefix + "/git/refs/heads/main", "PATCH", {
            "sha": commit["sha"], "force": False,
        })
        return commit

    def dispatch_publication(self):
        """Publish the new main revision through an explicit workflow dispatch."""
        self.github.api(
            f"{self.prefix}/actions/workflows/{PUBLICATION_WORKFLOW}/dispatches",
            "POST",
            {"ref": "main"},
        )

    def intake(self, issue, approve=False):
        if issue.get("pull_request") or issue["state"] != "open":
            return
        number = issue["number"]
        kind = application_kind(issue)
        if kind is None:
            return
        application_label = APPLICATION_LABELS[kind]
        try:
            repository, tag = submission(issue.get("body"))
            product = listing_product(self.github, repository, tag)
            fresh = self.github.api(f"{self.prefix}/issues/{number}")
            if fresh.get("body") != issue.get("body") or fresh["state"] != "open":
                return
            commit = self.apply(product, issue, kind) if approve else False
        except GitHubError as error:
            if error.status != 404:
                raise
            self.status(number, "status:needs-info", [application_label])
            self.comment(number, "The submitted listing release is unavailable. / 请确认提交的资料发行已公开。")
            return
        except (ValueError, KeyError, TypeError) as error:
            self.status(number, "status:needs-info", [application_label])
            self.comment(number, "Application needs attention / 请修正提交资料：\n\n" + str(error))
            return
        hosts = ["host:" + target["host"] for target in product["targets"]]
        if approve:
            self.status(number, "status:accepted", [application_label, *hosts])
            if commit is None:
                message = "The submitted product record is already current. / 当前产品登记已与提交资料一致。"
            else:
                url = f"https://github.com/{self.repository}/commit/{commit['sha']}"
                message = (
                    "Maintainer approval applied this record directly from the reviewed Issue. "
                    f"/ 管理员已通过当前 Issue 完成登记：{url}"
                )
            self.comment(number, message)
            self.github.api(f"{self.prefix}/issues/{number}", "PATCH", {"state": "closed", "state_reason": "completed"})
            return commit
        else:
            self.status(number, "status:in-review", [application_label, *hosts])
            self.comment(number, (
                "Metadata validated. A maintainer must review publisher ownership, package signatures, "
                "capability ceilings, and real host evidence, then apply `status:accepted`. "
                "/ 元数据校验通过；管理员完成归属、签名、能力边界和真实宿主证据审核后，请添加 `status:accepted`。"
            ))

    def close_application(self, issue):
        kind = application_kind(issue)
        if kind is None or issue.get("state") != "open":
            return
        hosts = sorted(label_names(issue) & HOST_LABELS)
        self.status(issue["number"], CLOSED, [APPLICATION_LABELS[kind], *hosts])
        self.comment(issue["number"], "Application closed by a maintainer. / 管理员已关闭当前申请。")
        self.github.api(f"{self.prefix}/issues/{issue['number']}", "PATCH", {
            "state": "closed", "state_reason": "not_planned",
        })

    def reconcile(self):
        for issue in self.github.pages(self.prefix + "/issues?state=open"):
            if is_submission(issue):
                self.intake(issue)

def main():
    github = GitHub()
    require(github.token, "GH_TOKEN is required")
    market = Marketplace(github, os.environ["GITHUB_REPOSITORY"])
    event = decode_json(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
    market.labels()
    event_name = os.environ["GITHUB_EVENT_NAME"]
    if event_name == "issues":
        issue = github.api(f"{market.prefix}/issues/{event['issue']['number']}")
        if not is_submission(issue):
            return
        if issue["state"] == "closed":
            if ACCEPTED not in label_names(issue):
                market.status(issue["number"], CLOSED)
        else:
            action = management_action(event)
            if action == CLOSED:
                market.close_application(issue)
            elif action == ACCEPTED:
                commit = market.intake(issue, approve=True)
                if commit is not None:
                    market.dispatch_publication()
            else:
                market.intake(issue)
    else:
        market.reconcile()


if __name__ == "__main__":
    main()
