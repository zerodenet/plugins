# Contributing

**English** · [简体中文](CONTRIBUTING.zh-CN.md)

Contributions include new plugin admissions, listing corrections, trust-boundary changes, release-source adapters, and repository-level implementation documentation. Plugin implementation and release changes belong in the plugin's own repository; public user and publisher guidance belongs in the [ZeroDeNet documentation site](https://github.com/zerodenet/docs).

## Admission

Use the [application form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml). Do not edit `catalogs/plugins.json` or open an admission PR. Provide one stable product identity and only the host targets actually supported. Each target has its own durable package ID and capability/UI ceilings. Include independently verifiable publisher/key ownership, one stable onboarding release, security maintenance, and actual host/platform evidence.

Automation verifies the generated onboarding manifest and marks the Issue in review. Maintainers review purpose, repository control, publisher identity, every host/package identity and maximum capability, migration and uninstall behavior, package signature, and real host evidence on that Issue. Applying `status:accepted` records approval and triggers the Action to commit the product entry and generated host projections directly; `status:closed` closes it without admission.

## Later releases

Do not add versions, artifacts, digests, compatibility declarations, or release notes to this repository. After admission, publishers release Stable, RC, and Dev versions in their own repositories. Hosts discover and enforce them against the admitted boundary.

Use the marketplace record-update Issue for repository transfer, publisher/key rotation, release-source contract changes, another host, broader capabilities or UI surfaces, suspension, withdrawal, or registered basic-information changes. These changes require the same maintainer label decision. Routine releases require no directory update. Pull requests remain the contribution path for marketplace implementation and policy code, not plugin admission decisions.

## Validation

Run:

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check

CI checks the unified registry, generated host projections, package-manifest tooling, API behavior, site build, public keys, and durable identities. It never executes publisher packages. Keep repository-level English and Simplified Chinese references aligned; submit public documentation changes to the documentation site. Keep credentials, private keys, packages, generated snapshots, and workstation data out of Git.
