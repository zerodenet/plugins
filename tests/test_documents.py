import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentsTest(unittest.TestCase):
    def test_versioned_schema_documents_are_valid_json(self):
        expected = {
            "product-registry.schema.json": "https://plugins.zerodenet.org/schemas/product-registry.schema.json",
            "release-manifest.schema.json": "https://plugins.zerodenet.org/schemas/release-manifest.schema.json",
            "marketplace-snapshot.schema.json": "https://plugins.zerodenet.org/schemas/marketplace-snapshot.schema.json",
        }
        for name, identifier in expected.items():
            self.assertEqual(json.loads((ROOT / "schemas" / name).read_text())["$id"], identifier)

    def test_local_markdown_links_resolve(self):
        missing = []
        for document in [*ROOT.glob("*.md"), *ROOT.joinpath("docs").glob("*.md"), ROOT / "schemas" / "README.md"]:
            for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", document.read_text()):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                path = target.split("#", 1)[0]
                if path and not (document.parent / path).resolve().exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])

    def test_site_has_no_product_specific_presentation_overrides(self):
        self.assertFalse((ROOT / "src/lib/presentation.ts").exists())
        source = "\n".join(path.read_text() for path in (ROOT / "src").rglob("*.astro"))
        self.assertNotIn("productDescription", source)
        self.assertNotIn("categoryName", source)
        self.assertNotIn("capabilityName", source)
        self.assertNotIn("zboard.oauth", source)
        self.assertNotIn("higanbana986", source)
        self.assertIn("{product.description}", source)
        self.assertIn("{capability}", source)
        self.assertNotIn("prerelease:", source)
        self.assertNotIn("assets_count:", source)
        self.assertNotIn("package_id:", source)

    def test_host_contract_labels_are_separate_from_product_metadata(self):
        source = (ROOT / "src/lib/host-contracts.ts").read_text()
        self.assertIn("zboard.ui.page.v1", source)
        self.assertIn("展示插件页面", source)
        self.assertNotIn("zboard.oauth", source)
        self.assertNotIn("OAuth for ZBoard", source)


if __name__ == "__main__":
    unittest.main()
