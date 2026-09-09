# Development

**English** · [简体中文](development.zh-CN.md)

This guide applies to the `zboard` branch. Clone with `git clone --branch zboard https://github.com/zerodenet/plugins.git` and target implementation PRs at `zboard`. Platform documentation lives on [main](https://github.com/zerodenet/plugins/tree/main).

## Repository layout

```text
zboard/oauth/        OAuth plugin: Go service, UI, tests, and packaging
scripts/check.sh    Repository check entry point
.github/workflows/  Continuous integration
docs/               User guides, contributor guides, and proposals
```

Plugin source is organized as `<host>/<plugin>/`. Each plugin maintains its own dependency files, manifest, and tests. The OAuth module is `github.com/zerodenet/plugins/zboard/oauth`; its installation ID is `zboard.oauth`.

Host implementations and SDKs remain in their respective repositories. Use public SDK packages and pin dependency versions. Local filesystem replacements belong in an untracked development workspace.

## Prerequisites

| Tool | Requirement | Purpose |
| --- | --- | --- |
| Go | 1.26.8 toolchain | Build, race tests, and vet |
| Node.js | 18 or later | UI and message bridge tests |
| Python | 3 | Package assembly |
| ZBoard source | Checkout with `backend/tools/pluginpackager` and the compatible plugin API | Package signing and host integration |

The OAuth `go.mod` pins the SDK dependency. Choose a host implementing its multi-provider identity API, configuration projection, and registration flow. Host compatibility includes these APIs as well as the version constraint in the manifest.

## Run checks

From the repository root:

```sh
sh scripts/check.sh
```

The check script runs Go formatting checks, race tests, vet, a service build, a real gRPC plugin-process test, and UI/bridge tests. Its default `GOWORK=off` validates the dependencies recorded in `go.mod`.

For joint host and plugin development:

```sh
cd zboard/oauth
go work init . /absolute/path/to/zboard/backend
GOWORK="$PWD/go.work" ./scripts/check.sh
```

Run the default checks again before submitting a change. This confirms that a local SDK edit has not hidden a dependency incompatibility.

## Build a development package

Run from `zboard/oauth/`:

```sh
python3 scripts/package.py --zboard /absolute/path/to/zboard --dev-key --platform linux-amd64
```

`ZBOARD_DIR` can supply the host path instead of `--zboard`. The script uses the plugin's module for its binary and the host's module for the packager. It produces `dist/zboard.oauth-0.2.0-linux-amd64.zbplugin` and stores the development key under `.local/` with publisher ID `oauth-local-dev`.

Supported build targets are `linux-amd64`, `linux-arm64`, `darwin-amd64`, `darwin-arm64`, and `windows-amd64`. Omit `--platform` to use the local Go platform. Building a target verifies compilation; installation and execution must also be tested on that target.

Only test hosts should trust a development key. Production signing is described in [Publishing](publishing.md).

## Test an integration

Install the package into a test host and exercise configuration, enabling, disabling, upgrading, and uninstalling. For authentication, use a registered provider application and verify sign-in, registration policy, and account binding. Record the host commit, plugin version, platform, and any incomplete checks.

Tests for changed behavior should cover successful operations, rejected input, timeouts, and state after failure. Keep protocol fixtures and test credentials separate from packaged UI and runtime files.
