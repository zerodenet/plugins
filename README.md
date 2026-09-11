# ZeroDeNet Plugin Marketplace

**English** · [简体中文](README.zh-CN.md)

The curated plugin directory for [ZBoard](https://github.com/zerodenet/zboard), [ZNet Sink](https://github.com/zerodenet/znet-sink), and future ZeroDeNet hosts. Marketplace admission means the host team reviewed the plugin's purpose, maintainer and signing identity, distribution source, and maximum requested integration boundary.

This repository is a directory, not a release ledger. Publishers own their Stable, RC, and Dev lifecycle in their own repositories. Compatible hosts discover those releases directly, verify packages with the admitted publisher key, and provide online installation, upgrade, downgrade, and channel selection.

## Browse plugins

| Host | Directory | Available projects |
| --- | --- | --- |
| ZBoard | [catalogs/zboard.json](catalogs/zboard.json) | [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth) |
| ZNet Sink | [catalogs/znet-sink.json](catalogs/znet-sink.json) | No admissions yet |

Directory entries contain only stable admission and source pointers: plugin ID, repository, publisher key, repository-metadata source, release-source adapter, supported UI surfaces, and the reviewed capability ceiling. Hosts read names, descriptions, licenses, maintainers, and links from the plugin repository's `marketplace.json`; versions, artifacts, digests, compatibility declarations, and release notes come from the plugin's Releases.

## Apply once

1. Maintain the plugin in its own repository with a license, setup guide, security contact, and stable signing identity.
2. Publish one stable signed onboarding release with immutable packages and marketplace-entry.json.
3. Use the [admission form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) or propose [a directory entry](templates/plugin-entry.json).

After admission, publish new Stable, RC, and Dev versions and basic-information updates only in the plugin repository. Return here only when changing the repository, publisher identity or key, metadata/release-source contract, supported host, UI surface ceiling, or capability ceiling.

Offline import remains independent of marketplace admission. It supports development testing, private or non-open-source plugins, local customization, and other self-managed distribution.

## Repository layout

The catalogs directory contains one curated directory per host; scripts contains admission and validation tooling; templates contains listing examples; and docs defines contracts, publishing policy, and host boundaries.

See [registry format](docs/registry-format.md), [publishing](docs/publishing.md), [automation](docs/automation.md), and [architecture](docs/governance.md). English is the reference language; Simplified Chinese guides are maintained alongside it.
