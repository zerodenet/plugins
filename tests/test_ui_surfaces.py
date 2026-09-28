import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_snapshot import build
from marketplace_schema import validate_product, validate_release_manifest


class ManagementSurfaceTest(unittest.TestCase):
    def setUp(self):
        self.product = json.loads((ROOT / "templates/product-registration.json").read_text())
        target = copy.deepcopy(self.product["targets"][1])
        target.update({
            "surfaces": ["znet-sink.ui.management.v1"],
            "host_version": {"min": "0.0.2"},
            "artifacts": [{
                "os": "any", "arch": "any", "size": 10, "sha256": "2" * 64,
                "url": self.product["repository"] + "/releases/download/v1.0.0/plugin.zspkg",
                "signature": {"algorithm": "ed25519", "value": "signed"},
            }],
        })
        self.manifest = {
            "schema_version": 1, "product_id": self.product["id"],
            "repository": self.product["repository"], "publisher": self.product["publisher"],
            "source": {"tag": "v1.0.0", "commit": "1" * 40},
            "release": {
                "version": "1.0.0", "channel": "stable", "published_at": "2026-09-28T00:00:00Z",
                "notes_url": self.product["repository"] + "/releases/tag/v1.0.0", "targets": [target],
            },
        }

    def test_management_and_added_permissions_are_discoverable_without_review(self):
        self.manifest["release"]["targets"][0]["capabilities"].append("plugin.logs.write")
        validate_release_manifest(self.manifest, self.product)
        snapshot = build({"schema_version": 3, "products": [self.product]}, None,
                         {self.product["id"]: [self.manifest]})
        target = snapshot["products"][0]["targets"][1]
        release = target["releases"][0]
        self.assertEqual(release["surfaces"], ["znet-sink.ui.management.v1"])
        self.assertIn("plugin.logs.write", release["capabilities"])
        self.assertIn("plugin.logs.write", target["capabilities"])
        self.assertIn("znet-sink.ui.management.v1", target["surfaces"])
        self.assertEqual(self.product["targets"][1]["surfaces"], [])

    def test_future_surface_is_metadata_and_host_decides_support(self):
        self.manifest["release"]["targets"][0]["surfaces"] = ["znet-sink.ui.future.v2"]
        validate_release_manifest(self.manifest, self.product)
        for invalid in (["bad surface"], ["admin", "admin"], [""]):
            with self.subTest(invalid=invalid):
                product = copy.deepcopy(self.product)
                product["targets"][1]["surfaces"] = invalid
                with self.assertRaisesRegex(ValueError, "invalid UI surface declaration"):
                    validate_product(product)


if __name__ == "__main__":
    unittest.main()
