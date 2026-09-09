# ZNet Sink Plugins

**English** · [简体中文](README.zh-CN.md)

The client plugin branch of [ZeroDeNet Plugins](https://github.com/zerodenet/plugins/tree/main), dedicated to extensions for [ZNet Sink](https://github.com/zerodenet/znet-sink).

## Status

This branch establishes the client integration scope and contribution process. The client plugin API, runtime, and package format are still under design. There are no installable client plugins or runtime checks in this branch yet.

## Scope

Client plugins will extend ZNet Sink through APIs owned by the client. Configuration changes, system permissions, connection management, and kernel control remain subject to the client's services and policies. Marketplace participation follows the shared distribution model while runtime compatibility is determined by the client.

Read [Client integration](docs/client-integration.md) for the contracts needed before implementation.

## Development

Use `znet-sink` as the base and merge target for client plugin changes. Once the host contract is implemented, plugin source belongs under `znet-sink/<plugin>/`, together with its configuration guide, dependencies, build process, and tests.

```sh
git clone --branch znet-sink https://github.com/zerodenet/plugins.git
cd plugins
```

Until implementation begins, validation covers documentation links, English/Chinese consistency, and agreement with the host design. Runtime and packaging checks will be introduced with the code they validate.

## Project resources

- [Client documentation](docs/README.md)
- [Contributing](CONTRIBUTING.md) and [project governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Platform overview](https://github.com/zerodenet/plugins/tree/main)
- [ZBoard plugin collection](https://github.com/zerodenet/plugins/tree/zboard)

## License

[Mozilla Public License 2.0](LICENSE). Third-party dependencies retain their respective licenses.
