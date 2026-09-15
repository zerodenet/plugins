#!/usr/bin/env python3
"""Turn first-time product applications into reviewed unified-registry proposals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re

from github_api import GitHub, GitHubError, decode_json, segment
from marketplace_schema import require
from release_metadata import append_product, listing_product, replace_product, submission

ROOT = Path(__file__).resolve().parents[1]
STATES = {"status:needs-info", "status:in-review", "status:accepted", "status:closed"}
HOST_LABELS = {"host:zboard", "host:znet-sink"}
APPLICATION_LABELS = {"submission": "plugin:submission", "update": "plugin:update"}


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

    def propose(self, product, issue, kind):
        base = self.github.api(self.prefix + "/git/ref/heads/main")["object"]["sha"]
        registry, blob = self.registry(base)
        updated = replace_product(registry, product) if kind == "update" else append_product(registry, product)
        if registry == updated:
            return None
        branch = f"automation/products/{product['id']}-{issue['number']}"
        owner = self.repository.split("/")[0]
        proposals = self.github.api(self.prefix + "/pulls?state=all&head=" + segment(owner + ":" + branch))
        if proposals:
            return proposals[0]
        encoded = base64.b64encode((json.dumps(updated, indent=2, ensure_ascii=False) + "\n").encode()).decode()
        try:
            self.github.api(self.prefix + "/git/refs", "POST", {"ref": "refs/heads/" + branch, "sha": base})
        except GitHubError as error:
            if error.status != 422:
                raise
        previous, previous_blob = self.registry(branch)
        if previous != updated:
            require(previous_blob == blob, "automation branch no longer matches main")
            self.github.api(self.prefix + "/contents/catalogs/plugins.json", "PUT", {
                "message": f"registry: list {product['id']}", "branch": branch,
                "sha": blob, "content": encoded,
                "author": {"name": "github-actions[bot]", "email": "41898282+github-actions[bot]@users.noreply.github.com"},
            })
        digest = hashlib.sha256((issue.get("body") or "").encode()).hexdigest()
        hosts = ", ".join(target["host"] for target in product["targets"])
        operation = "Update" if kind == "update" else "Admit"
        body = (
            f"{operation} {product['id']} in the unified marketplace for {hosts}.\n\n"
            "All product-facing fields in this proposal are copied verbatim from the submitted immutable listing. "
            "The marketplace does not translate, rewrite, or infer product metadata.\n\n"
            "Review covers product identity, publisher/key ownership, release source, host package identities, "
            "capability ceilings, license, security contact, package signature, and actual host evidence. "
            "Routine releases remain in the publisher repository.\n\n"
            "审核产品身份、发布者与密钥归属、发行源、宿主包身份、能力上限、许可证、安全联系、包签名及实际宿主证据。"
            "日常版本继续由开发者仓库维护。所有面向用户的产品字段均从本次固定清单原样复制，市场不翻译、不改写、不推断。\n\n"
            f"Submission: #{issue['number']}\n<!-- marketplace-submission:{issue['number']}:{digest} -->\n")
        return self.github.api(self.prefix + "/pulls", "POST", {
            "title": f"registry: {'update' if kind == 'update' else 'list'} {product['id']}",
            "head": branch, "base": "main", "body": body,
        })

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
            proposal = self.propose(product, issue, kind)
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
        if proposal is None:
            self.status(number, "status:accepted", [application_label, *hosts])
            message = "The submitted product record is now current. / 已按提交的原始资料更新产品登记。" if kind == "update" else "This product is listed. Future versions are discovered from its repository. / 产品已入驻，后续版本由统一快照从开发者仓库发现。"
            self.comment(number, message)
            self.github.api(f"{self.prefix}/issues/{number}", "PATCH", {"state": "closed", "state_reason": "completed"})
        else:
            state = "status:in-review" if proposal["state"] == "open" else "status:closed"
            self.status(number, state, [application_label, *hosts])
            self.comment(number, f"Marketplace admission proposal / 市场入驻 PR：{proposal['html_url']}")

    def reconcile(self):
        for issue in self.github.pages(self.prefix + "/issues?state=open"):
            if is_submission(issue):
                self.intake(issue)

    @staticmethod
    def is_submission(issue):
        return is_submission(issue)

    def closed_pr(self, pr):
        if pr["head"]["repo"] is None or pr["head"]["repo"]["full_name"] != self.repository \
                or not pr["head"]["ref"].startswith("automation/products/"):
            return
        self.status(pr["number"], "status:accepted" if pr.get("merged") else "status:closed")
        match = re.search(r"<!-- marketplace-submission:(\d+):([a-f0-9]{64}) -->", pr.get("body") or "")
        if match:
            issue = self.github.api(f"{self.prefix}/issues/{match[1]}")
            if hashlib.sha256((issue.get("body") or "").encode()).hexdigest() == match[2]:
                if pr.get("merged"):
                    self.intake(issue)
                else:
                    self.status(issue["number"], "status:closed")


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
            if not any(label["name"] == "status:accepted" for label in issue["labels"]):
                market.status(issue["number"], "status:closed")
        else:
            market.intake(issue)
    elif event_name == "pull_request_target":
        market.closed_pr(event["pull_request"])
    else:
        market.reconcile()


if __name__ == "__main__":
    main()
