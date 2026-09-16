# ZeroDeNet Plugin Marketplace

**English** · [简体中文](README.zh-CN.md)

The unified plugin marketplace for [ZBoard](https://github.com/zerodenet/zboard), [ZNet Sink](https://github.com/zerodenet/znet-sink), and future ZeroDeNet hosts. Users discover one product, while each product explicitly declares the host packages it supports. Marketplace admission means the host team reviewed purpose, maintainer and signing identity, distribution source, and maximum requested integration boundary.

This repository is a product registry and the source of a derived marketplace snapshot, not a manually maintained release ledger. Publishers own their Stable, RC, and Dev lifecycle in their own repositories. The build validates publisher manifests into one snapshot; compatible hosts query it explicitly and independently verify packages with the admitted publisher key.

## Browse and query

The authoritative registry is [catalogs/plugins.json](catalogs/plugins.json). User-facing product fields are copied verbatim from an immutable listing submitted through an Issue Template; they are not edited directly. The Action validates the application and leaves it in review until a maintainer applies `status:accepted`, then atomically commits the unified registry and generated host projections to `main` without an admission PR. GitHub Actions aggregates and validates publisher releases, then publishes the Astro site, unified snapshot, host/channel static JSON API, and schemas to Cloudflare Pages while retaining GitHub Pages as a fallback; the production domain is `plugins.zerodenet.org`. ZBoard and ZNet Sink fetch their fixed host/channel files and select compatible host versions and platforms locally. No Cloudflare Worker is required for the first release. The current registered product is [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth).

The old [ZBoard](catalogs/zboard.json) and [ZNet Sink](catalogs/znet-sink.json) schema-v2 catalogs are generated compatibility projections during host migration, not independent sources.

Product entries store the publisher's original name, description, categories, links, stable identity, repository, publisher key, release-source adapter, and host targets with durable package IDs and reviewed ceilings. The site renders registered values directly and does not translate, rewrite, or infer missing fields. A build-time snapshot joins validated publisher releases for the site and API; hosts still verify packages locally.

## Apply once

1. Maintain the plugin in its own repository with a license, setup guide, security contact, and stable signing identity.
2. Publish one stable signed onboarding release with immutable packages and marketplace-entry.json.
3. Generate `marketplace-entry.json` from signed packages, then use the [admission form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml). Plugin admission is reviewed and decided on that Issue, not through a contributor-edited catalog or a separate admission PR.

After admission, publish new Stable, RC, and Dev versions only in the plugin repository. Every registration change uses the [record update template](https://github.com/zerodenet/plugins/issues/new?template=update-plugin.yml); after maintainer approval on that Issue, automation commits the new immutable listing verbatim. Site code must not add product-specific overrides or polished replacement copy.

Offline import remains independent of marketplace admission. It supports development testing, private or non-open-source plugins, local customization, and other self-managed distribution.

## Repository layout

The catalogs directory contains the unified product registry and generated projections; src contains the Astro site and static API routes; scripts contains admission, release-manifest, snapshot, and validation tooling; and schemas defines reviewable data boundaries. Repository docs are limited to implementation and maintenance contracts, automation, architecture, and delivery records.

User and publisher guidance for installation, publishing, security, and the API is maintained on the [ZeroDeNet documentation site](https://docs.zerodenet.org/marketplace/). Repository references include [registry format](docs/registry-format.md), [automation](docs/automation.md), [development](docs/development.md), and [architecture](docs/governance.md).
