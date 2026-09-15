#!/usr/bin/env python3
"""Build marketplace-entry.json from signed host packages without executing them."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import zipfile

from marketplace_schema import validate_release_manifest


def read_zboard(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) > 514 or len(set(name.lower() for name in names)) != len(names):
            raise ValueError("unsafe or duplicate ZBoard package paths")
        manifest = json.loads(archive.read("manifest.json"))
        signature = json.loads(archive.read("signature.json"))
    return {
        "host": "zboard",
        "package_id": manifest["id"],
        "version": manifest["version"],
        "surfaces": manifest.get("surfaces", []),
        "capabilities": manifest.get("capabilities", []),
        "signature": signature["signature"],
    }


def read_znet_sink(path):
    envelope = json.loads(path.read_text())
    if envelope.get("format") != "znet-sink.plugin-package.v1":
        raise ValueError("unsupported ZNet Sink package")
    payload = json.loads(base64.b64decode(envelope["payload"], validate=True))
    if payload.get("host") != "znet-sink" or not payload.get("components"):
        raise ValueError("invalid ZNet Sink package identity")
    capabilities = set()
    for component in payload["components"]:
        manifest = component["manifest"]
        if manifest["plugin_id"] != payload["plugin_id"] or manifest["version"] != payload["version"]:
            raise ValueError("ZNet Sink component identity differs from package")
        capabilities.update(permission["capability"] for permission in manifest.get("required", []))
        capabilities.update(permission["capability"] for permission in manifest.get("optional", []))
    return {
        "host": "znet-sink",
        "package_id": payload["plugin_id"],
        "version": payload["version"],
        "surfaces": [],
        "capabilities": sorted(capabilities),
        "signature": envelope["signature"],
    }


def inspect(path):
    if path.suffix == ".zbplugin":
        return read_zboard(path)
    if path.suffix == ".zspkg":
        return read_znet_sink(path)
    raise ValueError("package extension must be .zbplugin or .zspkg")


def build(spec, root):
    grouped = {}
    version = None
    for record in spec["artifacts"]:
        path = (root / record["path"]).resolve()
        package = inspect(path)
        if version is None:
            version = package["version"]
        if package["version"] != version:
            raise ValueError("all packages in one release must use the same version")
        target = grouped.setdefault(package["host"], {
            "host": package["host"], "package_id": package["package_id"],
            "host_version": spec["host_versions"][package["host"]],
            "surfaces": package["surfaces"], "capabilities": package["capabilities"], "artifacts": [],
        })
        if target["package_id"] != package["package_id"] or target["surfaces"] != package["surfaces"] \
                or target["capabilities"] != package["capabilities"]:
            raise ValueError("packages for one target must declare identical identity and boundaries")
        data = path.read_bytes()
        target["artifacts"].append({
            "os": record["os"], "arch": record["arch"], "url": record["url"],
            "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "signature": {"algorithm": "ed25519", "value": package["signature"]},
        })
    if version is None:
        raise ValueError("at least one signed package is required")
    document = {
        "schema_version": 1,
        "product_id": spec["product_id"],
        "repository": spec["repository"],
        "publisher": spec["publisher"],
        "source": {"tag": "v" + version, "commit": spec["source_commit"]},
        "release": {
            "version": version, "channel": spec["channel"], "published_at": spec["published_at"],
            "notes_url": spec["notes_url"], "targets": [grouped[key] for key in sorted(grouped)],
        },
    }
    if "listing" in spec:
        document["listing"] = spec["listing"]
    validate_release_manifest(document)
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="release build specification")
    parser.add_argument("--output", type=Path, default=Path("marketplace-entry.json"))
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text())
    document = build(spec, args.spec.parent)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
