# ZeroDeNet Plugin Marketplace

**English** · [简体中文](README.zh-CN.md)

The centralized plugin registry and discovery service for [ZBoard](https://github.com/zerodenet/zboard), [ZNet Sink](https://github.com/zerodenet/znet-sink), and future ZeroDeNet hosts. Collection does not represent marketplace approval, security endorsement, or permission authorization.

## Browse and query

[catalogs/plugins.json](catalogs/plugins.json) is the authoritative product registry. Publishers submit an immutable release `marketplace-entry.json` through the registration or record-update form. Automation checks source control, identities and metadata consistency, then records the complete publisher `listing` verbatim without a maintainer approval label or admission PR.

Publishers own Stable, RC and Dev releases and packages in their repositories. The market derives the site, unified snapshot and six host/channel static API files from public releases. Permission or UI expansion does not exclude a release or require another registration request. Hosts independently verify signatures, compatibility and the package, display requested permissions, obtain user confirmation and enforce runtime authorization.

The production domain is `plugins.zerodenet.org`, served through Cloudflare Pages with GitHub Pages as a fallback. [ZBoard](catalogs/zboard.json) and [ZNet Sink](catalogs/znet-sink.json) schema-v2 catalogs remain generated compatibility projections.

## Register once

1. Maintain a stable product/package identity, publisher signing identity, license and source repository.
2. Publish signed packages and their immutable `marketplace-entry.json` in a public GitHub Release; Stable, RC and Dev are supported.
3. Submit the [registration form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) from the source owner or a collaborator whose write permission can be verified by automation.

For names, links, repository/key changes, host/package registration or withdrawal, use the [record-update form](https://github.com/zerodenet/plugins/issues/new?template=update-plugin.yml). Source transfers require control of both repositories. Permission changes belong in each release and need no market approval. Ordinary releases require no directory update. Product copy is never translated, rewritten or inferred.

Offline import, private plugins and local testing remain host-owned. The market never executes publisher packages.

## References

See [registry format](docs/registry-format.md), [automation](docs/automation.md), [development](docs/development.md), [architecture](docs/governance.md), and the [documentation site](https://docs.zerodenet.org/marketplace/).
