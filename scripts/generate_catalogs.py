#!/usr/bin/env python3
"""Generate transitional per-host directories from the unified registry."""
import json
from pathlib import Path

from marketplace_schema import HOSTS, project_host

ROOT = Path(__file__).resolve().parents[1]
registry = json.loads((ROOT / "catalogs/plugins.json").read_text())
for host in sorted(HOSTS):
    path = ROOT / "catalogs" / f"{host}.json"
    path.write_text(json.dumps(project_host(registry, host), ensure_ascii=False, indent=2) + "\n")
    print(path.relative_to(ROOT))
