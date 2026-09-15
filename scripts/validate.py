#!/usr/bin/env python3
"""Validate the unified registry and its legacy host projections."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from marketplace_schema import HOSTS, project_host, require, validate_registry, validate_transition

ROOT = Path(__file__).resolve().parents[1]


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field: " + key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(), object_pairs_hook=no_duplicates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="full Git SHA used to protect existing identities")
    args = parser.parse_args()
    try:
        registry = load(ROOT / "catalogs/plugins.json")
        validate_registry(registry)
        if args.base:
            if not re.fullmatch(r"[a-f0-9]{40}", args.base):
                raise ValueError("base must be a full Git SHA")
            subprocess.run(["git", "cat-file", "-e", args.base + "^{commit}"], cwd=ROOT, check=True, capture_output=True)
            unified = subprocess.check_output(
                ["git", "ls-tree", "--name-only", args.base, "--", "catalogs/plugins.json"], cwd=ROOT, text=True)
            if unified.strip():
                old = subprocess.check_output(["git", "show", args.base + ":catalogs/plugins.json"], cwd=ROOT, text=True)
                validate_transition(json.loads(old, object_pairs_hook=no_duplicates), registry)
            else:
                for host in sorted(HOSTS):
                    relative = f"catalogs/{host}.json"
                    raw = subprocess.check_output(["git", "show", args.base + ":" + relative], cwd=ROOT, text=True)
                    previous = json.loads(raw, object_pairs_hook=no_duplicates)
                    current = project_host(registry, host)
                    indexed = {item["id"]: item for item in current["plugins"]}
                    for old_entry in previous.get("plugins", []):
                        if indexed.get(old_entry["id"]) != old_entry:
                            raise ValueError("unified registry must preserve existing legacy listing: " + old_entry["id"])
        for host in sorted(HOSTS):
            path = ROOT / "catalogs" / (host + ".json")
            if load(path) != project_host(registry, host):
                raise ValueError(f"{path.relative_to(ROOT)} is not the generated compatibility projection")
            print(f"{path.relative_to(ROOT)}: valid projection")
        print("catalogs/plugins.json: valid registry")
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"catalog: {error}")


if __name__ == "__main__":
    main()
