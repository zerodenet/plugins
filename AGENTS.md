# Repository guidelines

**English** · [简体中文](AGENTS.zh-CN.md)

Read `README.md`, `CONTRIBUTING.md` and `docs/governance.md` before editing. This is a metadata registry with one maintained branch, `main`. Source catalogs are `catalogs/zboard.json` and `catalogs/znet-sink.json`; plugin source, build pipelines and packages belong to independent repositories.

Preserve plugin IDs and existing releases. Do not copy plugin runtimes or SDKs here, execute submitted packages, trust a submitted key automatically, or insert invented release metadata. Source-only listings must have empty releases. Hosts own authorization, core state and lifecycle transactions.

Run `python3 -m unittest discover -s tests`, `python3 scripts/validate.py` and `git diff --check`. Add focused negative tests when changing validation. Maintain English and Chinese guides together and verify local Markdown links. Keep generated artifacts and secrets untracked.

Use the checkout's required Git author and committer identity. Keep `main` linear and preserve migrated source history in its destination repository. Do not claim a registry source document is a signed host catalog or that cross-compilation proves platform execution.
