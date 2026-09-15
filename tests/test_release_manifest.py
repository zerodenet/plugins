import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_release_manifest import build


class ReleaseManifestTest(unittest.TestCase):
    def packages(self, root, sink_version="1.0.0"):
        board = root / "plugin.zbplugin"
        with zipfile.ZipFile(board, "w") as archive:
            archive.writestr("manifest.json", json.dumps({
                "id": "org.example.bridge.zboard", "version": "1.0.0", "surfaces": ["admin"],
                "capabilities": ["zboard.config.v1"],
            }))
            archive.writestr("signature.json", json.dumps({"signature": base64.b64encode(b"s" * 64).decode()}))
        payload = {
            "schema_version": 1, "host": "znet-sink", "plugin_id": "org.example.bridge.sink", "version": sink_version,
            "components": [{"manifest": {
                "plugin_id": "org.example.bridge.sink", "version": sink_version,
                "required": [{"capability": "network.request", "scope": "https://example.com"}], "optional": [],
            }, "source": "export default 1"}],
        }
        sink = root / "plugin.zspkg"
        sink.write_text(json.dumps({
            "format": "znet-sink.plugin-package.v1", "payload": base64.b64encode(json.dumps(payload).encode()).decode(),
            "signature": base64.b64encode(b"t" * 64).decode(),
        }))
        return board, sink

    def spec(self, board, sink):
        return {
            "product_id": "org.example.bridge", "repository": "https://github.com/example/bridge-plugin",
            "publisher": {"id": "example", "public_key": base64.b64encode(b"k" * 32).decode()},
            "source_commit": "1" * 40, "channel": "stable", "published_at": "2026-09-15T00:00:00Z",
            "notes_url": "https://github.com/example/bridge-plugin/releases/tag/v1.0.0",
            "host_versions": {"zboard": {"min": "0.0.2"}, "znet-sink": {"min": "0.0.2"}},
            "artifacts": [
                {"path": board.name, "url": "https://github.com/example/bridge-plugin/releases/download/v1.0.0/plugin.zbplugin", "os": "linux", "arch": "amd64"},
                {"path": sink.name, "url": "https://github.com/example/bridge-plugin/releases/download/v1.0.0/plugin.zspkg", "os": "any", "arch": "any"},
            ],
        }

    def test_generator_reads_signed_package_identity_and_computes_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            board, sink = self.packages(root)
            document = build(self.spec(board, sink), root)
            self.assertEqual({item["host"] for item in document["release"]["targets"]}, {"zboard", "znet-sink"})
            self.assertTrue(all(len(item["artifacts"][0]["sha256"]) == 64 for item in document["release"]["targets"]))
            self.assertEqual(document["release"]["targets"][1]["capabilities"], ["network.request"])

    def test_generator_rejects_mixed_package_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            board, sink = self.packages(root, "1.1.0")
            with self.assertRaisesRegex(ValueError, "same version"):
                build(self.spec(board, sink), root)


if __name__ == "__main__":
    unittest.main()
