# ZeroDeNet Plugin Marketplace

**English** · [简体中文](README.zh-CN.md)

The curated plugin directory for [ZBoard](https://github.com/zerodenet/zboard), [ZNet Sink](https://github.com/zerodenet/znet-sink), and future ZeroDeNet hosts. Marketplace admission means the host team reviewed the plugin's purpose, maintainer and signing identity, distribution source, and maximum requested integration boundary.

This repository is a directory, not a release ledger. Publishers own their Stable, RC, and Dev lifecycle in their own repositories. Compatible hosts discover those releases directly, verify packages with the admitted publisher key, and provide online installation, upgrade, downgrade, and channel selection.

## Browse plugins

| Host | Directory | Available projects |
| --- | --- | --- |
| ZBoard | [catalogs/zboard.json](catalogs/zboard.json) | [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth) |
| ZNet Sink | [catalogs/znet-sink.json](catalogs/znet-sink.json) | No admissions yet |

Directory entries store registration information: plugin ID, name, purpose, authors/maintainers, license, links, repository, publisher key, release-source adapter, supported UI surfaces, and the reviewed capability ceiling. Hosts display basic information from this directory and read versions, artifacts, compatibility declarations, and release notes from the registered repository's Releases.

## Apply once

1. Maintain the plugin in its own repository with a license, setup guide, security contact, and stable signing identity.
2. Publish one stable signed onboarding release with immutable packages and marketplace-entry.json.
3. Use the [admission form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) or propose [a directory entry](templates/plugin-entry.json).

After admission, publish new Stable, RC, and Dev versions only in the plugin repository; update registered basic information in this directory. Other directory updates include changes to the repository, publisher identity or key, release-source contract, supported host, UI surface ceiling, or capability ceiling.

Offline import remains independent of marketplace admission. It supports development testing, private or non-open-source plugins, local customization, and other self-managed distribution.

## Repository layout

The catalogs directory contains one curated directory per host; scripts contains admission and validation tooling; templates contains listing examples; and docs defines contracts, publishing policy, and host boundaries.

See [registry format](docs/registry-format.md), [publishing](docs/publishing.md), [automation](docs/automation.md), and [architecture](docs/governance.md). English is the reference language; Simplified Chinese guides are maintained alongside it.
