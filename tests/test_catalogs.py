import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketplace_schema import project_host, validate_registry, validate_release_manifest, validate_transition


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.product = json.loads((ROOT / "templates/product-registration.json").read_text())
        self.registry = {"schema_version": 3, "products": [self.product]}

    def test_single_product_can_register_two_distinct_host_packages(self):
        validate_registry(self.registry)
        self.assertEqual({item["host"] for item in self.product["targets"]}, {"zboard", "znet-sink"})
        self.assertNotEqual(self.product["targets"][0]["package_id"], self.product["targets"][1]["package_id"])
        self.assertEqual(project_host(self.registry, "zboard")["plugins"][0]["id"], "org.example.bridge.zboard")

    def test_registry_rejects_identity_trust_and_host_boundary_errors(self):
        mutations = [
            lambda p: p["publisher"].update(public_key="not-a-key"),
            lambda p: p["release_source"].update(type="branch-file"),
            lambda p: p["targets"].append(copy.deepcopy(p["targets"][0])),
            lambda p: p["targets"][1].update(capabilities=["zboard.config.v1"]),
            lambda p: p.update(repository="https://127.0.0.1/plugin"),
            lambda p: p.update(categories=["Not normalized"]),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                registry = copy.deepcopy(self.registry)
                mutate(registry["products"][0])
                with self.assertRaises(ValueError):
                    validate_registry(registry)

    def test_registry_rejects_duplicate_product_and_host_package_ids(self):
        duplicate = copy.deepcopy(self.product)
        self.registry["products"].append(duplicate)
        with self.assertRaises(ValueError):
            validate_registry(self.registry)
        self.registry["products"][1]["id"] = "org.example.other"
        with self.assertRaises(ValueError):
            validate_registry(self.registry)

    def test_transition_preserves_product_and_package_identities(self):
        current = copy.deepcopy(self.registry)
        current["products"][0]["description"] = "Updated description"
        validate_transition(self.registry, current)
        current["products"][0]["targets"][0]["package_id"] = "org.example.changed"
        with self.assertRaises(ValueError):
            validate_transition(self.registry, current)
        with self.assertRaises(ValueError):
            validate_transition(self.registry, {"schema_version": 3, "products": []})

    def test_release_cannot_replace_key_or_exceed_registered_capabilities(self):
        manifest = {
            "schema_version": 1,
            "product_id": self.product["id"],
            "repository": self.product["repository"],
            "publisher": self.product["publisher"],
            "source": {"tag": "v1.0.0", "commit": "1" * 40},
            "release": {
                "version": "1.0.0", "channel": "stable", "published_at": "2026-09-15T00:00:00Z",
                "notes_url": "https://github.com/example/bridge-plugin/releases/tag/v1.0.0",
                "targets": [{
                    **copy.deepcopy(self.product["targets"][1]),
                    "host_version": {"min": "0.0.2", "max_exclusive": "0.1.0"},
                    "artifacts": [{
                        "os": "any", "arch": "any",
                        "url": "https://github.com/example/bridge-plugin/releases/download/v1.0.0/plugin.zspkg",
                        "size": 10, "sha256": "2" * 64,
                        "signature": {"algorithm": "ed25519", "value": "signed"},
                    }],
                }],
            },
        }
        validate_release_manifest(manifest, self.product)
        bad = copy.deepcopy(manifest)
        bad["publisher"]["public_key"] = "eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHg="
        with self.assertRaises(ValueError):
            validate_release_manifest(bad, self.product)
        bad = copy.deepcopy(manifest)
        bad["release"]["targets"][0]["capabilities"].append("network.unreviewed")
        with self.assertRaises(ValueError):
            validate_release_manifest(bad, self.product)


if __name__ == "__main__":
    unittest.main()
