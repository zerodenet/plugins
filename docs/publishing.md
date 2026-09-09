# Publishing and review

**English** · [简体中文](publishing.zh-CN.md)

Plugin release and marketplace inclusion are separate operations. A publisher builds only the plugin being released. The market reviews metadata and does not rebuild third-party code.

## Publisher workflow

Develop and test in the independent repository. Choose a `vX.Y.Z` release, sign platform packages with a production publisher key and publish them with source commit, checksums, byte sizes and compatibility declarations. Retain the private key outside source control. Public releases must never use CI development keys.

[OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth) provides tag-triggered checks, five-platform packaging and a generated `marketplace-entry.json`. Its release environment settings are documented in that repository. Other publishers may use their own tooling if their artifacts conform to the host package contract.

## Marketplace workflow

Submit the release using the issue form or PR template. Update only the relevant entry in `catalogs/zboard.json` or `catalogs/znet-sink.json`, retaining previous releases. The entry template contains illustrative values that must all be replaced.

CI validates repository metadata and never executes submitted packages. Maintainers independently verify publisher/key ownership, release-to-source correspondence, package signatures, digests and host test evidence. A green source-validation check alone is insufficient for an installable listing.


An issue containing the release metadata URL is validated automatically and linked to a generated review PR. After first inclusion, scheduled checks propose new stable releases without a cross-repository publisher token. Labels track validation, review and inclusion; they do not authorize a merge. See [marketplace automation](automation.md) for setup and failure handling.

## Signed installation feeds

The source catalogs are not directly installable. A distribution publisher must select host- and platform-compatible reviewed artifacts, create the host's signed catalog, serve it over an accepted HTTPS download path and renew it before expiry. Catalog signing uses a market key distinct from plugin publisher keys.

ZBoard currently accepts its signed catalog v1 and direct HTTPS package downloads without redirects. GitHub Release asset URLs redirect; an existing host therefore needs offline import or a compatible direct-download mirror until redirect handling is implemented. No production signed feed or catalog-renewal workflow is published by this repository yet. Do not point `plugins.catalog_url` at the source JSON files.

[The distribution proposal](marketplace-design.md) covers shared feeds and compatibility exports. Its unimplemented portions are not requirements imposed on existing hosts.
