"""Validate one listing release and derive a durable product registration."""
import copy
import hashlib
import re

from github_api import decode_json, segment
from marketplace_schema import require, validate_product, validate_registry, validate_release_manifest, validate_transition

PRE = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
TAG = rf"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-{PRE}(?:\.{PRE})*)?"
METADATA_URL = re.compile(
    r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/releases/download/(" + TAG + r")/marketplace-entry\.json")


def submission(body):
    urls = {match.group(0) for match in METADATA_URL.finditer(body or "")}
    require(len(urls) == 1,
            "Provide exactly one listing marketplace-entry.json URL / 请提供唯一的资料发行元数据链接")
    match = METADATA_URL.fullmatch(urls.pop())
    return match[1], match[2]


def listing_product(github, repository, tag):
    release = github.api(f"/repos/{repository}/releases/tags/{segment(tag)}")
    require(not release["draft"] and not release["prerelease"] and release["tag_name"] == tag and "-" not in tag,
            "marketplace listing changes require one published stable release")
    assets = list(github.pages(f"/repos/{repository}/releases/{release['id']}/assets"))
    records = [asset for asset in assets if asset["name"] == "marketplace-entry.json"]
    require(len(records) == 1, "listing release needs one marketplace-entry.json asset")
    record = records[0]
    expected_url = f"https://github.com/{repository}/releases/download/{tag}/marketplace-entry.json"
    require(record["browser_download_url"] == expected_url, "metadata asset repository or tag mismatch")
    raw = github.asset(expected_url, record["size"])
    require(record.get("digest") == "sha256:" + hashlib.sha256(raw).hexdigest(),
            "metadata digest does not match GitHub release asset")
    document = decode_json(raw)
    validate_release_manifest(document)
    require("listing" in document, "listing manifest must include a complete product listing")
    product = document["listing"]
    validate_product(product)
    require(product["repository"] == f"https://github.com/{repository}", "listing belongs to another repository")
    require(document["source"]["tag"] == tag and document["release"]["channel"] == "stable",
            "listing release must be stable and match its tag")
    ref = github.api(f"/repos/{repository}/git/ref/tags/{segment(tag)}")["object"]
    for _ in range(4):
        if ref["type"] != "tag":
            break
        ref = github.api(f"/repos/{repository}/git/tags/{ref['sha']}")["object"]
    require(ref["type"] == "commit" and ref["sha"] == document["source"]["commit"],
            "tag does not resolve to the declared source commit")
    by_url = {asset["browser_download_url"]: asset for asset in assets}
    for target in document["release"]["targets"]:
        for artifact in target["artifacts"]:
            asset = by_url.get(artifact["url"])
            require(asset is not None and asset["size"] == artifact["size"]
                    and asset.get("digest") == "sha256:" + artifact["sha256"],
                    "package must match a GitHub asset size and digest in this release")
    return product


def append_product(registry, product):
    validate_registry(registry)
    validate_product(product)
    result = copy.deepcopy(registry)
    old = next((item for item in result["products"] if item["id"] == product["id"]), None)
    if old is None:
        result["products"].append(copy.deepcopy(product))
    else:
        require(old == product,
                "product already exists; trust, source, target, or capability changes need the marketplace update form")
    validate_registry(result)
    return result


def replace_product(registry, product):
    validate_registry(registry)
    validate_product(product)
    result = copy.deepcopy(registry)
    matches = [index for index, item in enumerate(result["products"]) if item["id"] == product["id"]]
    require(len(matches) == 1, "product is not registered; use the first-time admission template")
    result["products"][matches[0]] = copy.deepcopy(product)
    validate_transition(registry, result)
    return result
