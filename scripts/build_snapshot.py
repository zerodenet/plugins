#!/usr/bin/env python3
"""Build the bounded, derived marketplace snapshot used by the site and API."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from marketplace_schema import CHANNELS, HOSTS, validate_registry, validate_release_manifest

ROOT = Path(__file__).resolve().parents[1]
MAX_API_BYTES = 4 * 1024 * 1024
MAX_MANIFEST_BYTES = 512 * 1024
MAX_RELEASES = 100
MAX_RELEASE_FEED = 20
MAX_RELEASE_BODY = 4000


class GitHub:
    def __init__(self, token=""):
        self.token = token

    def read(self, url, limit, authenticated=False):
        parsed = urlsplit(url)
        if not self._allowed(parsed):
            raise ValueError("untrusted GitHub URL")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "zerodenet-marketplace-builder/1"}
        if authenticated and self.token:
            headers["Authorization"] = "Bearer " + self.token
        owner = self

        class SafeRedirect(HTTPRedirectHandler):
            def redirect_request(self, request, fp, code, message, headers, newurl):
                if not owner._allowed(urlsplit(newurl)):
                    raise ValueError("untrusted GitHub redirect")
                return super().redirect_request(request, fp, code, message, headers, newurl)

        with build_opener(SafeRedirect()).open(Request(url, headers=headers), timeout=10) as response:
            data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("upstream response exceeds limit")
        return data

    @staticmethod
    def _allowed(parsed):
        hostname = parsed.hostname or ""
        return parsed.scheme == "https" and not parsed.username and not parsed.password \
            and parsed.port in (None, 443) and (hostname in {"api.github.com", "github.com"}
                                                  or hostname.endswith(".githubusercontent.com"))

    def releases(self, repository):
        path = urlsplit(repository).path.strip("/")
        data = self.read(f"https://api.github.com/repos/{path}/releases?per_page={MAX_RELEASES}", MAX_API_BYTES, True)
        releases = json.loads(data)
        if not isinstance(releases, list) or len(releases) > MAX_RELEASES:
            raise ValueError("invalid GitHub releases response")
        return releases

    def manifest(self, product, release):
        asset_name = product["release_source"]["metadata_asset"]
        assets = [item for item in release.get("assets", []) if item.get("name") == asset_name]
        if len(assets) != 1 or assets[0].get("size", 0) > MAX_MANIFEST_BYTES:
            raise ValueError("release manifest is missing, ambiguous, or too large")
        expected = product["repository"].removeprefix("https://github.com/")
        prefix = f"/{expected}/releases/download/{quote(release['tag_name'], safe='')}/"
        url = assets[0].get("browser_download_url", "")
        parsed = urlsplit(url)
        if parsed.hostname != "github.com" or not parsed.path.startswith(prefix) or "/" in parsed.path[len(prefix):]:
            raise ValueError("release manifest URL differs from registered repository and tag")
        return json.loads(self.read(url, MAX_MANIFEST_BYTES))


def semver_tuple(value):
    core = value.split("-", 1)[0]
    return tuple(int(item) for item in core.split("."))


def channel(version, prerelease=False):
    lowered = version.lower()
    if "-rc" in lowered:
        return "rc"
    if "-" in version or prerelease:
        return "dev"
    return "stable"


def release_body(value):
    body = value if isinstance(value, str) else ""
    return body[:MAX_RELEASE_BODY], len(body) > MAX_RELEASE_BODY


def publisher_release(product, release, validated=False):
    tag = str(release.get("tag_name") or "").strip()
    published_at = release.get("published_at") or release.get("created_at")
    if not tag or not published_at:
        raise ValueError("publisher release lacks tag or publication time")
    name = release.get("name") if isinstance(release.get("name"), str) and release["name"] else tag
    body, body_truncated = release_body(release.get("body"))
    return {
        "tag": tag,
        "name": name,
        "channel": channel(tag.removeprefix("v"), bool(release.get("prerelease"))),
        "prerelease": bool(release.get("prerelease")),
        "published_at": published_at,
        "url": product["repository"] + "/releases/tag/" + quote(tag, safe=""),
        "body": body,
        "body_truncated": body_truncated,
        "assets_count": min(len(release.get("assets") or []), 1000),
        "validated": validated,
    }


def normalized_release_feed(items):
    normalized = []
    for item in items[:MAX_RELEASE_FEED]:
        normalized.append({
            "tag": item["tag"], "name": item["name"], "channel": item["channel"],
            "prerelease": item["prerelease"], "published_at": item["published_at"], "url": item["url"],
            "body": item.get("body", ""), "body_truncated": bool(item.get("body_truncated", False)),
            "assets_count": item["assets_count"], "validated": bool(item.get("validated", False)),
        })
    return normalized


def version_range(raw):
    match = re.fullmatch(r">=\s*(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)\s+<\s*(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)", raw or "")
    if not match:
        raise ValueError("legacy host range must use >=min <max")
    return {"min": match[1], "max_exclusive": match[2]}


def split_platform(value):
    if value == "any":
        return "any", "any"
    aliases = {"macos": "darwin", "x86_64": "amd64", "aarch64": "arm64"}
    parts = value.rsplit("-", 1)
    if len(parts) != 2:
        raise ValueError("invalid legacy platform")
    return aliases.get(parts[0], parts[0]), aliases.get(parts[1], parts[1])


def normalize_new(product, document):
    validate_release_manifest(document, product)
    return document["release"]


def normalize_legacy(product, document, github_release):
    if document.get("repository") != product["repository"] or document.get("publisher") != product["publisher"]:
        raise ValueError("legacy release trust identity differs from registration")
    tag = github_release["tag_name"]
    records = [item for item in document.get("releases", []) if item.get("version") == tag]
    if len(records) != 1:
        raise ValueError("legacy manifest does not uniquely describe this release")
    record = records[0]
    host_keys = [host for host in HOSTS if host in record.get("requires", {})]
    if len(host_keys) != 1:
        raise ValueError("legacy release must identify one host")
    host = host_keys[0]
    registration = next((item for item in product["targets"] if item["host"] == host), None)
    if registration is None or document.get("id") != registration["package_id"]:
        raise ValueError("legacy release target is not registered")
    if not set(record.get("surfaces", [])) <= set(registration["surfaces"]) \
            or not set(record.get("capabilities", [])) <= set(registration["capabilities"]):
        raise ValueError("legacy release exceeds its registered boundary")
    artifacts = []
    for artifact in record.get("artifacts", []):
        operating_system, architecture = split_platform(artifact["platform"])
        artifacts.append({
            "os": operating_system, "arch": architecture, "url": artifact["url"],
            "size": artifact["size"], "sha256": artifact["sha256"], "signature": None,
        })
    if not artifacts:
        raise ValueError("legacy release has no artifacts")
    version = tag.removeprefix("v")
    return {
        "version": version,
        "channel": channel(version, github_release.get("prerelease", False)),
        "published_at": github_release.get("published_at") or github_release.get("created_at"),
        "notes_url": github_release["html_url"],
        "targets": [{
            "host": host, "package_id": registration["package_id"],
            "host_version": version_range(record["requires"][host]),
            "surfaces": record.get("surfaces", []), "capabilities": record.get("capabilities", []),
            "artifacts": artifacts,
        }],
    }


def release_for(product, document, github_release):
    if document.get("schema_version") == 1 and "release" in document:
        result = normalize_new(product, document)
        if "v" + result["version"] != github_release["tag_name"]:
            raise ValueError("manifest version differs from GitHub release")
        return result
    return normalize_legacy(product, document, github_release)


def base_product(product):
    result = {key: product[key] for key in (
        "id", "name", "description", "categories", "license", "maintainers", "repository", "publisher",
        "release_source")}
    for key in ("homepage", "documentation", "security", "icon", "screenshots"):
        if key in product:
            result[key] = product[key]
    result["targets"] = [{**target, "releases": []} for target in product["targets"]]
    result["release_feed"] = []
    return result


def attach_releases(product, releases, release_feed=None):
    result = base_product(product)
    validated_tags = {"v" + release["version"] for release in releases}
    result["release_feed"] = [
        {**item, "validated": item["tag"] in validated_tags}
        for item in normalized_release_feed(release_feed or [])
    ]
    by_host = {target["host"]: target for target in result["targets"]}
    for release in releases:
        for target in release["targets"]:
            if target["host"] not in by_host:
                continue
            by_host[target["host"]]["releases"].append({
                "version": release["version"], "channel": release["channel"],
                "published_at": release["published_at"], "notes_url": release["notes_url"],
                "host_version": target["host_version"], "surfaces": target["surfaces"],
                "capabilities": target["capabilities"], "artifacts": target["artifacts"],
            })
    for target in result["targets"]:
        target["releases"].sort(key=lambda item: (semver_tuple(item["version"]), item["published_at"]), reverse=True)
    return result


def fixtures(path):
    if path is None:
        return None
    value = json.loads(path.read_text())
    if value.get("fixture") is not True or not isinstance(value.get("products"), dict):
        raise ValueError("release fixture must be explicitly marked fixture: true")
    return value["products"]


def previous_products(path):
    if path is None or not path.exists():
        return {}
    value = json.loads(path.read_text())
    if value.get("schema_version") != 1:
        raise ValueError("previous snapshot schema is unsupported")
    return {item["id"]: item for item in value.get("products", [])}


def build(registry, client, fixture_data=None, previous=None, generated_at=None):
    validate_registry(registry)
    old = previous or {}
    stale = []
    products = []
    for product in registry["products"]:
        if product.get("withdrawn"):
            continue
        try:
            normalized = []
            release_feed = []
            if fixture_data is not None:
                for record in fixture_data.get(product["id"], []):
                    current = normalize_new(product, record)
                    normalized.append(current)
                    release_feed.append({
                        "tag": "v" + current["version"], "name": "v" + current["version"],
                        "channel": current["channel"], "prerelease": current["channel"] != "stable",
                        "published_at": current["published_at"], "url": current["notes_url"],
                        "body": "", "body_truncated": False,
                        "assets_count": sum(len(target["artifacts"]) for target in current["targets"]),
                        "validated": True,
                    })
            elif client is not None:
                candidates = 0
                for release in client.releases(product["repository"]):
                    if release.get("draft") or not release.get("published_at"):
                        continue
                    candidates += 1
                    try:
                        release_feed.append(publisher_release(product, release))
                    except (ValueError, KeyError, TypeError):
                        pass
                    try:
                        normalized.append(release_for(product, client.manifest(product, release), release))
                    except (ValueError, KeyError, TypeError, OSError):
                        continue
                if candidates and not normalized:
                    retained = base_product(product)
                    old_targets = {item["host"]: item for item in old.get(product["id"], {}).get("targets", [])}
                    for target in retained["targets"]:
                        target["releases"] = old_targets.get(target["host"], {}).get("releases", [])
                    retained["release_feed"] = normalized_release_feed(release_feed) \
                        or normalized_release_feed(old.get(product["id"], {}).get("release_feed", []))
                    products.append(retained)
                    stale.append(product["id"])
                    continue
            products.append(attach_releases(product, normalized, release_feed))
        except (ValueError, KeyError, TypeError, OSError):
            if product["id"] in old:
                retained = base_product(product)
                old_targets = {item["host"]: item for item in old[product["id"]].get("targets", [])}
                for target in retained["targets"]:
                    target["releases"] = old_targets.get(target["host"], {}).get("releases", [])
                retained["release_feed"] = normalized_release_feed(old[product["id"]].get("release_feed", []))
                products.append(retained)
                stale.append(product["id"])
            else:
                products.append(base_product(product))
                stale.append(product["id"])
    products.sort(key=lambda item: item["id"])
    content_hash = hashlib.sha256(json.dumps(products, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema_version": 1,
        "snapshot_version": "sha256:" + content_hash,
        "generated_at": generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sources": {"registry_schema": registry["schema_version"], "stale_products": stale},
        "products": products,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "catalogs/plugins.json")
    parser.add_argument("--output", type=Path, default=ROOT / ".generated/marketplace-snapshot.json")
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--generated-at")
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text())
    fixture_data = fixtures(args.fixture)
    client = None if fixture_data is not None else GitHub(os.environ.get("GITHUB_TOKEN", ""))
    snapshot = build(registry, client, fixture_data, previous_products(args.previous), args.generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    print(f"{args.output}: {len(snapshot['products'])} products, {len(snapshot['sources']['stale_products'])} stale")


if __name__ == "__main__":
    main()
