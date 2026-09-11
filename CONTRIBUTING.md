# Contributing

**English** · [简体中文](CONTRIBUTING.zh-CN.md)

Contributions include new plugin admissions, listing corrections, trust-boundary changes, release-source adapters, and documentation. Plugin implementation and release changes belong in the plugin's own repository.

## Admission

Use the [application form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) or copy [the entry template](templates/plugin-entry.json) into the appropriate host directory. Provide repository-owned `marketplace.json`, the repository, license, maintainers, publisher key, metadata/release-source adapters, UI surface ceiling, and capability ceiling. Provide independently verifiable publisher/key ownership, one stable onboarding release, security maintenance, and actual host/platform evidence.

Automation verifies the onboarding release and proposes a version-free directory entry. Maintainers review purpose, repository control, publisher identity, requested maximum capabilities, migration and uninstall behavior, package signature, and real host evidence.

## Later releases

Do not add versions, artifacts, digests, compatibility declarations, or release notes to this repository. After admission, publishers release Stable, RC, and Dev versions in their own repositories. Hosts discover and enforce them against the admitted boundary.

Use a focused marketplace PR for repository transfer, publisher/key rotation, metadata/release-source contract changes, another host, broader capabilities or UI surfaces, suspension, or withdrawal. Routine `marketplace.json` information changes stay in the plugin repository.

## Validation

Run:

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    git diff --check

CI checks structure, host separation, public keys, adapters, capability ceilings, and durable listing identity. It never executes publisher packages. Keep English and Simplified Chinese documentation aligned and keep credentials, private keys, packages, and workstation data out of Git.
