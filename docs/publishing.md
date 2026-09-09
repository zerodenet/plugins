# Publishing model

**English** · [简体中文](publishing.zh-CN.md)

Plugin releases are prepared from their host branch. `main` maintains the shared publishing contract and marketplace proposals; it contains no package build or release workflow.

## Release identity

A release records its plugin ID, publisher, semantic version, source branch and commit, compatible host/API versions, target platforms, and artifact digests. Tags include the host and plugin, such as `zboard/oauth/v0.2.0`, so collections can release independently.

Published artifact content is immutable. Corrections receive a new version. Validation notes distinguish automated checks, host lifecycle tests, target-platform execution, and live external-provider testing.

## Signing and distribution

Publishers sign packages in a protected environment and distribute public keys through a trusted channel. Catalog signing and package signing are separate roles, each verified by the host. Development credentials and runtime data remain outside published artifacts.

Publish packages at immutable locations, generate catalog entries from the exact bytes, sign the catalog, and verify installation from a supported host. The catalog and package must agree on identity, host compatibility, publisher, and digest.

## Host procedures

| Collection | Publishing procedure |
| --- | --- |
| ZBoard | [Signing, package validation, and catalog v1 requirements](https://github.com/zerodenet/plugins/blob/zboard/docs/publishing.md) |
| ZNet Sink | [Client integration requirements](https://github.com/zerodenet/plugins/blob/znet-sink/docs/client-integration.md); release tooling follows the host contract |

The [marketplace proposal](marketplace-design.md) covers shared distribution. No public catalog or official signed release is currently published.

## Maintenance

Maintain download availability, renew time-limited catalogs, and record withdrawals with affected digests and recovery guidance. Withdrawing a listing does not delete installed plugin data. Existing installations are handled through the host's supported lifecycle operations.
