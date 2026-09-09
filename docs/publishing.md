# Publishing plugins

**English** · [简体中文](publishing.zh-CN.md)

This guide defines the release process for maintained plugins. Public distribution status is listed in the [project README](../README.md); the shared catalog format is described in the [marketplace proposal](marketplace-design.md).

## Prepare a release

Select a reviewed source commit on `zboard` with passing checks. Record:

| Release information | Required detail |
| --- | --- |
| Identity | Plugin ID, publisher, semantic version, and source commit |
| Compatibility | Host version range, SDK/API and UI bridge versions, supported platforms |
| Changes | User-visible behavior, configuration changes, data migrations, and recovery instructions |
| Validation | Automated checks, host lifecycle tests, target-platform execution, and provider integration results |
| Build provenance | Toolchain versions and host packager commit |

Review the manifest's recommended and tested host versions against the actual host build used for validation. For authentication plugins, record whether a real provider authorization flow was tested. Cross-compilation and protocol fixtures cover different checks from deployed execution.

Use tags scoped to a host and plugin, such as `zboard/oauth/v0.2.0`. A published version and its artifacts are immutable; publish a new version for a correction. Build from committed source with locked dependencies and no local workspace replacement.

## Sign packages

Keep release keys in a protected signing environment. Pull request checks must run without access to those keys. Publisher IDs and public keys need a trusted distribution channel and a documented rotation procedure.

From `zboard/oauth/`:

```sh
python3 scripts/package.py --zboard /path/to/zboard --key /secure/publisher.key --key-id your-publisher --platform linux-amd64
```

The packager assembles the UI and target runtime, hashes the content files, and signs the manifest. Inspect the resulting file list and verify its signature and package SHA-256 before publication. Publish the checksum and validation notes with the release.

Development packages use `--dev-key` and the fixed publisher ID `oauth-local-dev`. Keep these packages in test environments. Platform code signing and notarization are separate from the plugin's Ed25519 signature.

## Publish a catalog

1. Publish immutable package artifacts at their final download locations.
2. Generate catalog entries from the exact published bytes and their SHA-256 digests.
3. Sign the catalog with its trusted catalog key.
4. Verify installation from a host using the published catalog and download paths.

The current ZBoard downloader requires public HTTPS on port 443 and rejects query parameters, redirects, private destinations, and environment proxies. Choose direct artifact URLs that satisfy those rules. GitHub release asset URLs may redirect and therefore require a compatible distribution endpoint.

### ZBoard catalog v1

| Constraint | Value |
| --- | --- |
| Schema | `schema_version: 1` |
| Entries | At most 200; one entry per plugin ID |
| Expiration | Future UTC timestamp, at most 31 days from validation |
| Package | Signed `.zbplugin` matching the catalog identity and digest |

The current OAuth packager builds one platform per invocation. For v1 distribution, choose explicit platform-specific catalogs or provide a separately validated package containing multiple platform runtimes. Repeating the same plugin ID in one catalog is invalid. Multi-platform assembly and catalog publishing are not automated by the current script.

Maintain catalog availability and renew its signature before expiry. An expired catalog prevents new catalog-based installations.

## Withdraw a release

For a compromised key or defective artifact, stop advertising affected versions and publish the affected digests, impact, and recovery instructions. Coordinate remediation with host maintainers. Removing a listing does not automatically stop installed plugins or erase their data; host-supported actions determine how existing installations are handled.
