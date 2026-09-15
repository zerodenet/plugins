import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_snapshot import GitHub, build
from urllib.parse import urlsplit


def fixture(product, host="znet-sink", version="1.0.0", release_channel="stable"):
    target = next(item for item in product["targets"] if item["host"] == host)
    extension = "zspkg" if host == "znet-sink" else "zbplugin"
    return {
        "schema_version": 1, "product_id": product["id"], "repository": product["repository"],
        "publisher": product["publisher"], "source": {"tag": "v" + version, "commit": "1" * 40},
        "release": {
            "version": version, "channel": release_channel, "published_at": "2026-09-15T00:00:00Z",
            "notes_url": product["repository"] + "/releases/tag/v" + version,
            "targets": [{
                **copy.deepcopy(target), "host_version": {"min": "0.0.2", "max_exclusive": "0.1.0"},
                "artifacts": [{
                    "os": "any", "arch": "any", "url": product["repository"] + f"/releases/download/v{version}/plugin.{extension}",
                    "size": 10, "sha256": "2" * 64, "signature": {"algorithm": "ed25519", "value": "signed"},
                }],
            }],
        },
    }


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        self.product = json.loads((ROOT / "templates/product-registration.json").read_text())
        self.registry = {"schema_version": 3, "products": [self.product]}

    def test_snapshot_joins_one_product_to_multiple_host_releases(self):
        records = [fixture(self.product, "zboard"), fixture(self.product, "znet-sink")]
        snapshot = build(self.registry, None, {self.product["id"]: records}, generated_at="2026-09-15T00:00:00Z")
        self.assertEqual(len(snapshot["products"]), 1)
        self.assertEqual(snapshot["products"][0]["release_source"], self.product["release_source"])
        self.assertTrue(all(len(target["releases"]) == 1 for target in snapshot["products"][0]["targets"]))
        self.assertEqual(snapshot["products"][0]["release_feed"][0]["tag"], "v1.0.0")
        self.assertTrue(snapshot["products"][0]["release_feed"][0]["validated"])
        self.assertEqual(snapshot["sources"]["stale_products"], [])

    def test_release_feed_includes_prereleases_without_making_them_stable(self):
        records = [fixture(self.product, version="1.1.0-rc.1", release_channel="rc")]
        product = build(self.registry, None, {self.product["id"]: records})["products"][0]
        self.assertEqual(product["release_feed"][0]["channel"], "rc")
        self.assertTrue(product["release_feed"][0]["prerelease"])

    def test_upstream_failure_retains_old_releases_but_withdrawal_wins(self):
        old = build(self.registry, None, {self.product["id"]: [fixture(self.product)]})
        class Failing:
            def releases(self, _):
                raise OSError("offline")
        retained = build(self.registry, Failing(), previous={self.product["id"]: old["products"][0]})
        self.assertEqual(len(retained["products"][0]["targets"][1]["releases"]), 1)
        self.assertEqual(retained["sources"]["stale_products"], [self.product["id"]])
        withdrawn = copy.deepcopy(self.registry)
        withdrawn["products"][0]["withdrawn"] = True
        self.assertEqual(build(withdrawn, Failing(), previous={self.product["id"]: old["products"][0]})["products"], [])

    def test_snapshot_hash_is_stable_across_build_times(self):
        first = build(self.registry, None, {}, generated_at="2026-09-15T00:00:00Z")
        second = build(self.registry, None, {}, generated_at="2026-09-16T00:00:00Z")
        self.assertEqual(first["snapshot_version"], second["snapshot_version"])

    def test_invalid_current_releases_use_last_known_good(self):
        old = build(self.registry, None, {self.product["id"]: [fixture(self.product)]})

        class Invalid:
            def releases(self, _):
                return [{"draft": False, "published_at": "2026-09-15T00:00:00Z"}]

            def manifest(self, *_):
                raise ValueError("invalid manifest")

        retained = build(self.registry, Invalid(), previous={self.product["id"]: old["products"][0]})
        self.assertEqual(len(retained["products"][0]["targets"][1]["releases"]), 1)
        self.assertEqual(retained["sources"]["stale_products"], [self.product["id"]])

    def test_unvalidated_publisher_release_is_visible_but_not_installable(self):
        old = build(self.registry, None, {self.product["id"]: [fixture(self.product)]})

        class PublisherOnly:
            def releases(self, _):
                return [{
                    "tag_name": "v1.1.0-dev.1", "name": "Developer preview",
                    "draft": False, "prerelease": True, "published_at": "2026-09-16T00:00:00Z",
                    "body": "New provider support.\n\nSee the migration notes.", "assets": [{"name": "plugin.zspkg"}],
                }]

            def manifest(self, *_):
                raise ValueError("invalid manifest")

        snapshot = build(self.registry, PublisherOnly(), previous={self.product["id"]: old["products"][0]})
        product = snapshot["products"][0]
        self.assertEqual(len(product["targets"][1]["releases"]), 1)
        self.assertEqual(product["release_feed"][0]["tag"], "v1.1.0-dev.1")
        self.assertFalse(product["release_feed"][0]["validated"])
        self.assertEqual(product["release_feed"][0]["body"], "New provider support.\n\nSee the migration notes.")
        self.assertFalse(product["release_feed"][0]["body_truncated"])
        self.assertEqual(snapshot["sources"]["stale_products"], [self.product["id"]])

    def test_github_redirect_allowlist_excludes_unrelated_hosts(self):
        self.assertTrue(GitHub._allowed(urlsplit("https://release-assets.githubusercontent.com/file")))
        self.assertFalse(GitHub._allowed(urlsplit("https://github.com.evil.example/file")))


if __name__ == "__main__":
    unittest.main()
