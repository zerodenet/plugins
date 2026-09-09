# ZeroDeNet Plugin Marketplace

**English** · [简体中文](README.zh-CN.md)

A public registry of independently maintained plugins for [ZBoard](https://github.com/zerodenet/zboard) and [ZNet Sink](https://github.com/zerodenet/znet-sink). Publishers build and release plugins in their own repositories. This repository records where releases come from, which hosts they support, and how their artifacts can be verified.

## Browse plugins

| Host | Registry | Available projects |
| --- | --- | --- |
| ZBoard | [catalogs/zboard.json](catalogs/zboard.json) | [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth) — source available; signed release pending |
| ZNet Sink | [catalogs/znet-sink.json](catalogs/znet-sink.json) | No submissions yet |

OAuth connects GitHub, Google and custom OAuth2 / OpenID Connect providers to ZBoard. Its source, tests, configuration guides and release workflows are maintained in its independent repository. ZBoard retains control of account creation, registration policy and sessions.

The JSON files above are reviewed source records. They are not signed installation feeds and must not be configured as ZBoard's `plugins.catalog_url`. A plugin with an empty `releases` array is a source listing, not an installable release. See [installation and trust](docs/usage.md).

## Submit a plugin

1. Maintain the plugin in a public source repository with a license, setup guide and security contact.
2. Publish an independently versioned, signed release with immutable packages, SHA-256 digests and platform information.
3. Use the [submission form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) or open a PR against `main` using [the entry template](templates/plugin-entry.json).

A release updates one plugin entry in its host catalog. Marketplace CI validates metadata without compiling plugins or running contributor packages. See [contributing](CONTRIBUTING.md) for the review requirements.

## Repository layout

```text
catalogs/       One source catalog per host
scripts/        Registry validation
templates/     Submission examples
.github/        Contribution forms and validation workflow
docs/           Registry format, publishing and host boundaries
```

All maintained registry data and policies live on `main`. Plugin source and binaries belong to their independent repositories. The market does not maintain product-specific source branches.

## Documentation

- [Registry format](docs/registry-format.md)
- [Publishing and review](docs/publishing.md)
- [Host responsibilities](docs/governance.md)
- [Development](docs/development.md)
- [Distribution proposal](docs/marketplace-design.md)
- [Governance](GOVERNANCE.md) · [Security](SECURITY.md)

English is the reference language; Simplified Chinese guides are maintained alongside it. Registry materials are licensed under [MPL-2.0](LICENSE). Each listed plugin retains its own license.
