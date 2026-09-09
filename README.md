# ZBoard Plugins

**English** · [简体中文](README.zh-CN.md)

The ZBoard plugin collection for [ZeroDeNet Plugins](https://github.com/zerodenet/plugins/tree/main). This branch maintains plugin source, configuration guides, packaging, and tests for ZBoard.

[![Plugin checks](https://github.com/zerodenet/plugins/actions/workflows/ci.yml/badge.svg?branch=zboard)](https://github.com/zerodenet/plugins/actions/workflows/ci.yml?query=branch%3Azboard)

## Plugins

| Plugin | Description |
| --- | --- |
| [OAuth](zboard/oauth/README.md) | GitHub, Google, and custom OAuth2 / OpenID Connect sign-in and registration |

OAuth is available for source builds and integration testing. Signed releases and a public catalog are planned. Each plugin's README describes its host API requirements and validation status.

## Development

```sh
git clone --branch zboard https://github.com/zerodenet/plugins.git
cd plugins
sh scripts/check.sh
```

Checks require Go 1.26.8 and Node.js 18 or later. Packaging also requires Python 3 and a compatible ZBoard checkout with the plugin packager. See [Development](docs/development.md) for the full setup.

Source remains under `zboard/<plugin>/`. The OAuth module is `github.com/zerodenet/plugins/zboard/oauth`, and the plugin ID is `zboard.oauth`.

## Documentation

- [Installation and operation](docs/usage.md)
- [OAuth setup](zboard/oauth/README.md) and [configuration reference](zboard/oauth/docs/configuration.md)
- [Development](docs/development.md) and [publishing](docs/publishing.md)
- [Plugin architecture](docs/governance.md)

## Contributions

Create implementation branches from `zboard` and target pull requests at `zboard`. CI validates this collection on pushes and pull requests to that branch. Shared platform documentation belongs on [main](https://github.com/zerodenet/plugins/tree/main); client plugins belong on [znet-sink](https://github.com/zerodenet/plugins/tree/znet-sink).

Read [Contributing](CONTRIBUTING.md), [Project governance](GOVERNANCE.md), and [Security](SECURITY.md) before submitting changes or reports.

## License

[Mozilla Public License 2.0](LICENSE). Third-party dependencies retain their respective licenses.
