#!/usr/bin/env python3
"""Automatically register publisher metadata after technical validation."""
import base64
import json
import os
from pathlib import Path
import re

from github_api import GitHub, GitHubError, decode_json, segment
from marketplace_schema import HOSTS, project_host, require
from release_metadata import append_product, listing_product, replace_product, submission

ROOT = Path(__file__).resolve().parents[1]
STATES = {"status:needs-info", "status:in-review", "status:accepted", "status:registered", "status:closed"}
HOST_LABELS = {"host:zboard", "host:znet-sink"}
APPLICATION_LABELS = {"submission": "plugin:submission", "update": "plugin:update"}
REGISTERED = "status:registered"
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
    """A collaborator may close an invalid record; no label approves registration."""
    if event.get("action") == "labeled" and event.get("sender", {}).get("type") == "User" \
            and event.get("label", {}).get("name") == CLOSED:
        return CLOSED
    return None


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

    def fresh_submission(self, issue):
        fresh = self.github.api(f"{self.prefix}/issues/{issue['number']}")
        require(fresh.get("body") == issue.get("body") and fresh.get("state") == "open",
                "submission changed while registration was running; retry")
        require(application_kind(fresh) == application_kind(issue),
                "submission type changed while registration was running; retry")
        require(fresh.get("user", {}).get("login") == issue.get("user", {}).get("login"),
                "submission author changed")
        return fresh

    def publisher_control(self, repository, issue):
        """Check source ownership automatically; never treat metadata prose as proof."""
        login = issue.get("user", {}).get("login", "")
        require(re.fullmatch(r"[A-Za-z0-9-]{1,39}", login), "missing publisher GitHub identity")
        owner = repository.removeprefix("https://github.com/").split("/")[0]
        if owner.lower() == login.lower():
            return
        source = repository.removeprefix("https://github.com/")
        try:
            permission = self.github.api(f"/repos/{source}/collaborators/{segment(login)}/permission")
        except GitHubError as error:
            if error.status not in (403, 404):
                raise
            raise ValueError("submit from the source repository owner or a verifiable write collaborator") from error
        require(permission.get("permission") in {"write", "maintain", "admin"},
                "submitter does not control the publisher repository")

    def apply(self, product, issue, kind):
        """Create one atomic main-branch commit without opening an admission PR."""
        base = self.github.api(self.prefix + "/git/ref/heads/main")["object"]["sha"]
        registry, _ = self.registry(base)
        self.publisher_control(product["repository"], issue)
        previous = next((item for item in registry["products"] if item["id"] == product["id"]), None)
        if previous is not None and previous["repository"] != product["repository"]:
            self.publisher_control(previous["repository"], issue)
        updated = replace_product(registry, product) if kind == "update" else append_product(registry, product)
        if registry == updated:
            return None
        self.fresh_submission(issue)
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
        self.fresh_submission(issue)
        current = self.github.api(self.prefix + "/git/ref/heads/main")["object"]["sha"]
        require(current == base, "registry changed while registration was running; retry")
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

    def intake(self, issue):
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
            commit = self.apply(product, issue, kind)
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
        self.status(number, REGISTERED, [application_label, *hosts])
        if commit is None:
            message = "The submitted product record is already current. / 当前产品登记已与提交资料一致。"
        else:
            url = f"https://github.com/{self.repository}/commit/{commit['sha']}"
            message = f"Metadata checks passed; automatically registered. / 元数据校验通过，已自动登记：{url}"
        self.comment(number, message)
        self.github.api(f"{self.prefix}/issues/{number}", "PATCH", {"state": "closed", "state_reason": "completed"})
        return commit

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
        changed = False
        for issue in self.github.pages(self.prefix + "/issues?state=open"):
            if is_submission(issue):
                changed = self.intake(issue) is not None or changed
        if changed:
            self.dispatch_publication()

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
            if REGISTERED not in label_names(issue) and "status:accepted" not in label_names(issue):
                market.status(issue["number"], CLOSED)
        else:
            action = management_action(event)
            if action == CLOSED:
                market.close_application(issue)
            elif event.get("action") in {"opened", "edited", "reopened"}:
                commit = market.intake(issue)
                if commit is not None:
                    market.dispatch_publication()
    else:
        market.reconcile()


if __name__ == "__main__":
    main()
