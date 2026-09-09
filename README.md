# ZeroDeNet Plugins

**English** · [简体中文](README.zh-CN.md)

The plugin platform for the ZeroDeNet ecosystem. This repository brings together the project documentation, host-specific plugin collections, and the design of a shared marketplace for [ZBoard](https://github.com/zerodenet/zboard) and [ZNet Sink](https://github.com/zerodenet/znet-sink).

## Repository branches

| Branch | Purpose |
| --- | --- |
| **main** | Platform overview, shared architecture, contribution policies, and marketplace proposals |
| [**zboard**](https://github.com/zerodenet/plugins/tree/zboard) | ZBoard plugins, configuration guides, builds, and tests |
| [**znet-sink**](https://github.com/zerodenet/plugins/tree/znet-sink) | Client plugin development and integration documentation |

This branch is the documentation entry point. Each host collection is maintained and released from its own branch. Contributions target the branch responsible for the change.

## Plugin collections

### ZBoard

The [OAuth plugin](https://github.com/zerodenet/plugins/tree/zboard/zboard/oauth) connects GitHub, Google, and custom OAuth2 / OpenID Connect providers to ZBoard's sign-in and registration flows. Source builds and integration tests are available on the `zboard` branch.

### ZNet Sink

The [client branch](https://github.com/zerodenet/plugins/tree/znet-sink) establishes the scope for client plugins. Its host API and plugin runtime are under design; no client plugin implementation is available yet.

Signed releases and a public marketplace catalog are planned. The [marketplace proposal](docs/marketplace-design.md) describes shared discovery and distribution across hosts.

## Architecture

Plugins extend their host through dedicated APIs. Each application owns permission checks, configuration, private data, installation, and upgrades. Core business rules remain in the application that owns them.

The marketplace organizes releases by plugin, host, and platform. Installation decisions and runtime behavior are governed by each host's contracts. Read [Plugin architecture](docs/governance.md) for those responsibilities.

## Documentation

- [Documentation index](docs/README.md)
- [Choosing and operating plugins](docs/usage.md)
- [Development model](docs/development.md)
- [Publishing model](docs/publishing.md)
- [Contribution guide](CONTRIBUTING.md) and [project governance](GOVERNANCE.md)

Host-specific setup, commands, and troubleshooting are maintained on the host branches.

## Community

Use [GitHub Issues](https://github.com/zerodenet/plugins/issues) for bug reports and design proposals. Include the host and plugin when reporting a problem. Follow [SECURITY.md](SECURITY.md) for vulnerability reports.

## License

[Mozilla Public License 2.0](LICENSE). Third-party dependencies retain their respective licenses.
