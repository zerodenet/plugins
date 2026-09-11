# Repository guidelines

**English** · [简体中文](AGENTS.zh-CN.md)

Read README.md, CONTRIBUTING.md, and docs/governance.md before editing. This repository is a curated admission and discovery directory with one maintained branch, main. Plugin source, release history, packages, compatibility metadata, and release notes belong to independent publisher repositories.

Preserve plugin IDs and existing listings. Directory entries contain only stable identity, publisher key, repository-metadata and release-source pointers, host scope, and reviewed capability/UI ceilings. Never add routine Stable, RC, or Dev release records here, execute submitted packages, or invent publisher evidence. Repository/key changes, source-contract changes, capability expansion, and withdrawals require focused review.

Hosts own online release discovery, channel/version selection, verification, installation, upgrade, downgrade, removal, local state, and audit. Offline import remains a separate administrator-trust path.

Run python3 -m unittest discover -s tests, python3 scripts/validate.py, and git diff --check. Maintain English and Chinese guides together and keep generated artifacts and secrets untracked.
