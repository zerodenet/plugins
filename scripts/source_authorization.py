"""Verify a narrowly scoped authorization published by the source repository."""
import base64
import binascii
import hashlib
import re

from github_api import GitHubError, decode_json, segment
from marketplace_schema import require

AUTHORIZATION_PATH = ".github/marketplace-authorizations.json"
MAX_AUTHORIZATION_BYTES = 16 * 1024
COMMIT = re.compile(r"[a-f0-9]{40}")
DIGEST = re.compile(r"[a-f0-9]{64}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def authorization_for_issue(marketplace, issue):
    actor_id = issue.get("user", {}).get("id")
    number = issue.get("number")
    body = issue.get("body")
    require(REPOSITORY.fullmatch(marketplace), "invalid marketplace repository")
    require(type(number) is int and number > 0 and type(actor_id) is int and actor_id > 0
            and isinstance(body, str), "source authorization requires an Issue ID, author ID and body")
    return {"marketplace": marketplace.lower(), "issue": number, "actor_id": actor_id,
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()}


def validate_document(document):
    require(isinstance(document, dict) and set(document) == {"schema_version", "authorizations"}
            and type(document["schema_version"]) is int and document["schema_version"] == 1,
            "invalid source authorization document")
    entries = document["authorizations"]
    require(isinstance(entries, list) and len(entries) <= 100, "invalid source authorization list")
    for entry in entries:
        require(isinstance(entry, dict)
                and set(entry) == {"marketplace", "issue", "actor_id", "body_sha256"},
                "invalid source authorization entry")
        require(isinstance(entry["marketplace"], str) and REPOSITORY.fullmatch(entry["marketplace"])
                and type(entry["issue"]) is int and entry["issue"] > 0
                and type(entry["actor_id"]) is int and entry["actor_id"] > 0
                and isinstance(entry["body_sha256"], str) and DIGEST.fullmatch(entry["body_sha256"]),
                "invalid source authorization binding")


def authorized_by_source(github, source, marketplace, issue):
    """Only the source's current default branch can authorize the exact request."""
    expected = authorization_for_issue(marketplace, issue)
    require(REPOSITORY.fullmatch(source), "invalid source repository")
    prefix = "/repos/" + source
    try:
        repository = github.public_api(prefix)
        branch = repository.get("default_branch")
        require(isinstance(branch, str) and 0 < len(branch) <= 255, "source default branch is unavailable")
        ref = github.public_api(prefix + "/git/ref/heads/" + segment(branch))
        target = ref.get("object", {})
        require(target.get("type") == "commit" and isinstance(target.get("sha"), str)
                and COMMIT.fullmatch(target["sha"]), "invalid source default-branch commit")
        record = github.public_api(prefix + "/contents/" + AUTHORIZATION_PATH + "?ref=" + target["sha"])
    except GitHubError as error:
        if error.status == 404:
            return False
        raise
    require(isinstance(record, dict) and record.get("type") == "file"
            and record.get("path") == AUTHORIZATION_PATH and record.get("encoding") == "base64"
            and type(record.get("size")) is int and 0 < record["size"] <= MAX_AUTHORIZATION_BYTES
            and isinstance(record.get("content"), str)
            and len(record["content"]) <= 2 * MAX_AUTHORIZATION_BYTES,
            "source authorization must be a bounded regular JSON file")
    try:
        raw = base64.b64decode("".join(record["content"].split()), validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("invalid source authorization encoding") from None
    require(len(raw) == record["size"], "source authorization size mismatch")
    document = decode_json(raw)
    validate_document(document)
    return any({**entry, "marketplace": entry["marketplace"].lower()} == expected
               for entry in document["authorizations"])


def main():
    import argparse
    import json
    from pathlib import Path
    from github_api import GitHub

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--marketplace", required=True, help="registry owner/repository")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--output", type=Path, default=Path(AUTHORIZATION_PATH))
    args = parser.parse_args()
    require(REPOSITORY.fullmatch(args.marketplace) and args.issue > 0, "invalid registration Issue")
    issue = GitHub(token="").public_api(f"/repos/{args.marketplace}/issues/{args.issue}")
    require(not issue.get("pull_request") and issue.get("state") == "open", "registration must be an open Issue")
    authorization = authorization_for_issue(args.marketplace, issue)
    require(not args.output.is_symlink(), "authorization output must not be a symlink")
    document = decode_json(args.output.read_bytes()) if args.output.exists() else {"schema_version": 1, "authorizations": []}
    validate_document(document)
    document["authorizations"] = [entry for entry in document["authorizations"]
                                  if not (entry["marketplace"].lower() == authorization["marketplace"]
                                          and entry["issue"] == authorization["issue"]
                                          and entry["actor_id"] == authorization["actor_id"])]
    document["authorizations"].append(authorization)
    validate_document(document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"{args.output}: commit this public authorization to the source repository's default branch")


if __name__ == "__main__":
    main()
