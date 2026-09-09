# Development model

**English** · [简体中文](development.zh-CN.md)

## Choose a branch

Platform documentation and shared proposals belong on `main`. ZBoard implementation work starts from `zboard`; client implementation work starts from `znet-sink`. A pull request uses the same host branch as its merge target.

The [ZBoard development guide](https://github.com/zerodenet/plugins/blob/zboard/docs/development.md) provides the OAuth toolchain, build, and test commands. The [client integration scope](https://github.com/zerodenet/plugins/blob/znet-sink/docs/client-integration.md) records the contracts needed before client plugin development begins.

## Source ownership

Host branches use `<host>/<plugin>/` for plugin source and keep their own dependency files, manifests, packaging scripts, and checks. Stable plugin IDs and public module paths survive repository layout changes. The host applications and their SDKs remain in their own repositories.

Shared architecture and project policies are maintained here. Synchronize changes as isolated documentation commits or file updates. Review the diff when applying shared changes; merging an entire host branch would also transfer its implementation.

## Validation

Changes to `main` are reviewed for accurate product status, working links, and consistent English and Chinese documentation. Host branches define the checks appropriate to their implementation. Test new capabilities at the host boundary before consuming them in a plugin.

See [Contributing](../CONTRIBUTING.md) for branch selection and review, and [Architecture](governance.md) for capability and lifecycle requirements.
