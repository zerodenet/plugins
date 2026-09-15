import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from release_metadata import append_product, listing_product, replace_product, submission
from marketplace_sync import Marketplace, application_kind, catalog_documents, management_action


class ReleaseAPI:
    def __init__(self):
        self.product = json.loads((ROOT / "templates/product-registration.json").read_text())
        self.repository = self.product["repository"].removeprefix("https://github.com/")
        self.tag = "v1.0.0"
        self.commit = "1" * 40
        target = copy.deepcopy(self.product["targets"][1])
        self.artifact = {
            "os": "any", "arch": "any",
            "url": f"https://github.com/{self.repository}/releases/download/{self.tag}/plugin.zspkg",
            "size": 10, "sha256": "2" * 64,
            "signature": {"algorithm": "ed25519", "value": "signed"},
        }
        self.document = {
            "schema_version": 1, "product_id": self.product["id"], "repository": self.product["repository"],
            "publisher": self.product["publisher"], "source": {"tag": self.tag, "commit": self.commit},
            "release": {
                "version": "1.0.0", "channel": "stable", "published_at": "2026-09-15T00:00:00Z",
                "notes_url": f"https://github.com/{self.repository}/releases/tag/{self.tag}",
                "targets": [{**target, "host_version": {"min": "0.0.2"}, "artifacts": [self.artifact]}],
            },
            "listing": self.product,
        }
        self.draft = False
        self.prerelease = False
        self.refresh()

    def refresh(self):
        self.raw = json.dumps(self.document).encode()
        self.metadata = {
            "name": "marketplace-entry.json",
            "browser_download_url": f"https://github.com/{self.repository}/releases/download/{self.tag}/marketplace-entry.json",
            "size": len(self.raw), "digest": "sha256:" + hashlib.sha256(self.raw).hexdigest(),
        }
        self.assets = [self.metadata, {
            "name": "plugin.zspkg", "browser_download_url": self.artifact["url"],
            "size": self.artifact["size"], "digest": "sha256:" + self.artifact["sha256"],
        }]

    def api(self, path):
        if "/releases/tags/" in path:
            return {"id": 1, "tag_name": self.tag, "draft": self.draft, "prerelease": self.prerelease}
        if "/git/ref/tags/" in path:
            return {"object": {"type": "commit", "sha": self.commit}}
        raise AssertionError(path)

    def pages(self, _):
        return iter(self.assets)

    def asset(self, url, size):
        self.download = (url, size)
        return self.raw


class AdmissionGitHub:
    def __init__(self, product, issue):
        self.base = "a" * 40
        self.registry = {"schema_version": 3, "products": []}
        self.product = product
        self.issue = issue
        self.calls = []
        self.blobs = {}

    def api(self, path, method="GET", data=None):
        self.calls.append((path, method, data))
        prefix = "/repos/example/market"
        if path == prefix + "/git/ref/heads/main" and method == "GET":
            return {"object": {"sha": self.base}}
        if path == prefix + f"/contents/catalogs/plugins.json?ref={self.base}":
            raw = json.dumps(self.registry).encode()
            return {"encoding": "base64", "content": base64.b64encode(raw).decode(), "sha": "registry-blob"}
        if path == prefix + "/issues/7":
            return copy.deepcopy(self.issue)
        if path == prefix + f"/git/commits/{self.base}":
            return {"tree": {"sha": "base-tree"}}
        if path == prefix + "/git/blobs" and method == "POST":
            sha = f"blob-{len(self.blobs)}"
            self.blobs[sha] = data["content"]
            return {"sha": sha}
        if path == prefix + "/git/trees" and method == "POST":
            self.tree = data
            return {"sha": "new-tree"}
        if path == prefix + "/git/commits" and method == "POST":
            self.commit = data
            return {"sha": "new-commit"}
        if path == prefix + "/git/refs/heads/main" and method == "PATCH":
            self.ref_update = data
            return {"object": {"sha": data["sha"]}}
        raise AssertionError((path, method, data))


class SyncTest(unittest.TestCase):
    def test_onboarding_derives_one_product_with_all_registered_targets(self):
        api = ReleaseAPI()
        product = listing_product(api, api.repository, api.tag)
        self.assertEqual(product, api.product)
        registry = append_product({"schema_version": 3, "products": []}, product)
        self.assertEqual(len(registry["products"][0]["targets"]), 2)

    def test_onboarding_rejects_unreviewable_release_or_trust_changes(self):
        for mutate in (
            lambda api: setattr(api, "draft", True),
            lambda api: setattr(api, "prerelease", True),
            lambda api: setattr(api, "commit", "f" * 40),
            lambda api: api.metadata.update(digest="sha256:" + "f" * 64),
            lambda api: api.assets[1].update(size=11),
            lambda api: api.document["publisher"].update(public_key="eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHg="),
            lambda api: api.document["release"]["targets"][0]["capabilities"].append("network.unreviewed"),
        ):
            with self.subTest(mutate=mutate):
                api = ReleaseAPI()
                mutate(api)
                if mutate.__code__.co_firstlineno >= 0:
                    api.raw = json.dumps(api.document).encode()
                with self.assertRaises((ValueError, KeyError)):
                    listing_product(api, api.repository, api.tag)

    def test_submission_requires_one_immutable_release_manifest(self):
        url = "https://github.com/example/bridge-plugin/releases/download/v1.0.0/marketplace-entry.json"
        self.assertEqual(submission(url), ("example/bridge-plugin", "v1.0.0"))
        with self.assertRaises(ValueError):
            submission(url + "\n" + url.replace("v1.0.0", "v1.0.1"))

    def test_update_replaces_the_submitted_record_without_rewriting_fields(self):
        api = ReleaseAPI()
        registry = {"schema_version": 3, "products": [copy.deepcopy(api.product)]}
        updated = copy.deepcopy(api.product)
        updated["name"] = "Publisher supplied name"
        updated["description"] = "Publisher supplied description"
        result = replace_product(registry, updated)
        self.assertEqual(result["products"][0], updated)
        with self.assertRaisesRegex(ValueError, "package identity"):
            changed_identity = copy.deepcopy(updated)
            changed_identity["targets"][0]["package_id"] = "org.example.replacement"
            replace_product(registry, changed_identity)

    def test_workflow_uses_reviewed_default_branch_code(self):
        workflow = (ROOT / ".github/workflows/marketplace.yml").read_text()
        self.assertIn("ref: main", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertNotIn("pull-requests: write", workflow)
        self.assertNotIn("github.event.issue.body", workflow)

    def test_issue_labels_select_admission_or_exact_record_update(self):
        admission = {"title": "[Plugin] example", "labels": [{"name": "plugin:submission"}]}
        update = {"title": "[Plugin update] example", "labels": [{"name": "plugin:update"}]}
        self.assertEqual(application_kind(admission), "submission")
        self.assertEqual(application_kind(update), "update")
        self.assertIsNone(application_kind({"title": "Question", "labels": []}))

    def test_only_human_decision_label_events_request_management_actions(self):
        event = {"action": "labeled", "label": {"name": "status:accepted"},
                 "sender": {"type": "User"}}
        self.assertEqual(management_action(event), "status:accepted")
        event["label"]["name"] = "status:closed"
        self.assertEqual(management_action(event), "status:closed")
        event["sender"]["type"] = "Bot"
        self.assertIsNone(management_action(event))
        event["sender"]["type"] = "User"
        event["action"] = "edited"
        self.assertIsNone(management_action(event))

    def test_approval_atomically_commits_registry_and_both_host_projections(self):
        product = json.loads((ROOT / "templates/product-registration.json").read_text())
        issue = {
            "number": 7,
            "title": "[Plugin] example",
            "body": "reviewed body",
            "state": "open",
            "labels": [{"name": "plugin:submission"}, {"name": "status:accepted"}],
        }
        github = AdmissionGitHub(product, issue)
        commit = Marketplace(github, "example/market").apply(product, issue, "submission")

        self.assertEqual(commit["sha"], "new-commit")
        self.assertEqual(github.ref_update, {"sha": "new-commit", "force": False})
        self.assertEqual(github.tree["base_tree"], "base-tree")
        paths = {entry["path"] for entry in github.tree["tree"]}
        self.assertEqual(paths, set(catalog_documents({"schema_version": 3, "products": [product]})))
        self.assertFalse(any("/pulls" in path for path, _, _ in github.calls))
        documents = {
            entry["path"]: json.loads(github.blobs[entry["sha"]])
            for entry in github.tree["tree"]
        }
        self.assertEqual(documents["catalogs/plugins.json"]["products"], [product])
        self.assertEqual(documents["catalogs/zboard.json"]["host"], "zboard")
        self.assertEqual(documents["catalogs/znet-sink.json"]["host"], "znet-sink")


if __name__ == "__main__":
    unittest.main()
