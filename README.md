# ZeroDeNet Plugins

**English** · [简体中文](README.zh-CN.md)

Plugins for the ZeroDeNet ecosystem. This repository hosts official plugin source code, developer documentation, and the design of a shared marketplace for [ZBoard](https://github.com/zerodenet/zboard) and [ZNet Sink](https://github.com/zerodenet/znet-sink).

[![Plugin checks](https://github.com/zerodenet/plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/zerodenet/plugins/actions/workflows/ci.yml)
[![License: MPL-2.0](https://img.shields.io/badge/License-MPL--2.0-blue.svg)](LICENSE)

## Plugins

| Plugin | Host | Description |
| --- | --- | --- |
| [OAuth](zboard/oauth/README.md) | ZBoard | Sign in and register with GitHub, Google, or a custom OAuth2 / OpenID Connect provider. |

The OAuth plugin is available for source builds and integration testing. Signed releases and a public catalog are planned. ZNet Sink support is planned; its plugin runtime and host API are not yet available.

## Getting started

To install a plugin, start with its README for host requirements and configuration, then follow the [installation guide](docs/usage.md). During development, packages can be built locally with the host's signing tools.

For local development, clone the repository and run the checks:

```sh
git clone https://github.com/zerodenet/plugins.git
cd plugins
sh scripts/check.sh
```

The current checks require Go 1.26.8 and Node.js 18 or later. Packaging also requires Python 3 and a ZBoard checkout containing the plugin packager. See [Development](docs/development.md) for setup and build commands.

## Architecture

Plugins provide integrations and interfaces through APIs exposed by their host application. Each host handles installation, permissions, configuration, private data, and upgrades. Business rules—including account registration and credential management—remain in the host's core services.

The shared marketplace will organize releases by plugin, host, and platform. Hosts retain their own APIs and package compatibility rules. See [Architecture](docs/governance.md) and the [marketplace proposal](docs/marketplace-design.md) for the contracts behind this model.

## Documentation

| Guide | For |
| --- | --- |
| [Installation and operation](docs/usage.md) | Administrators installing and maintaining plugins |
| [Development](docs/development.md) | Developers building and testing plugins |
| [Architecture](docs/governance.md) | Authors designing host integrations |
| [Publishing](docs/publishing.md) | Maintainers preparing releases |
| [Marketplace proposal](docs/marketplace-design.md) | Contributors working on shared distribution |

[Browse all documentation →](docs/README.md)

## Contributing

Bug reports, documentation improvements, translations, and plugin contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the review process and [GOVERNANCE.md](GOVERNANCE.md) for how project decisions are made.

Report reproducible bugs through [GitHub Issues](https://github.com/zerodenet/plugins/issues). For vulnerabilities, follow the [security reporting policy](SECURITY.md).

## License

[Mozilla Public License 2.0](LICENSE). Third-party dependencies are distributed under their respective licenses.
