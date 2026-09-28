# Repository guidelines

**English** · [简体中文](AGENTS.zh-CN.md)

Read README.md, CONTRIBUTING.md, and docs/governance.md before editing. This repository is a centralized registration and discovery service with one maintained branch, main. `catalogs/plugins.json` is the only maintained product registry; per-host catalogs are generated compatibility projections. Plugin source, releases, packages, compatibility metadata, and release notes belong to publisher repositories.

Preserve product and host/package identities and existing listings. Directory capability and UI arrays are descriptive metadata, never approved ceilings. Do not require marketplace approval for registration, permission changes, UI changes, or routine releases. Automatically check source ownership, structure, identity, tag/source consistency, asset location, size and digest. Do not execute submitted packages or invent publisher evidence. Preserve source control checks for repository/key changes and explicit withdrawal handling.

Hosts own package signature verification, API/platform compatibility, installation, permission display and user confirmation, runtime authorization, lifecycle, local state, and audit. Collection is not a security endorsement or permission grant. Offline import remains a separate host trust path.

Run the validation commands below. Maintain English and Chinese references together and keep generated snapshots, site output, packages, and secrets untracked.

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check
