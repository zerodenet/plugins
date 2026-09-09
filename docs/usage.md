# Installation and operation

**English** · [简体中文](usage.zh-CN.md)

This guide covers plugins installed into ZBoard. Host-specific setup is documented with each plugin. ZNet Sink installation instructions will be added when its plugin runtime is available.

## Requirements

Choose a package matching the host application, host API version, operating system, and CPU architecture. A page contribution such as `admin` identifies where the UI appears; access to host operations is determined separately by capabilities and host policy.

Administrators configure trusted publisher public keys in ZBoard. Obtain a key through a trusted publisher channel before installing its packages. For local testing, the [development guide](development.md) explains how to generate a development package and key.

## Install a package

1. Add the publisher's public key to `plugins.trusted_publishers` in the host configuration. Restart the host after changing this configuration.
2. Open ZBoard's plugin management page and choose offline import.
3. Select the signed `.zbplugin` file and confirm the import. ZBoard validates the package and installs it in the disabled state.
4. Open the plugin's configuration page, save the required settings, and run its configuration check.
5. Enable the plugin and verify the feature from the relevant user interface.

Installation, configuration, enabling, and disabling are dynamic operations and do not require a host restart. A configuration check may only validate settings or provider metadata; use a real account to verify the full login flow for an authentication plugin.

### Online installation

A configured signed catalog lets administrators select packages from the host's marketplace page. `plugins.catalog_url` must point to the catalog document. Online installation uses the same package verification as offline import. Public distribution status is listed in the [project README](../README.md).

## Upgrade and restore

Back up the host database, plugin directory, and encryption keys together before an upgrade. Importing a new version of the same plugin invokes the host's upgrade process. The publisher must match the existing installation.

ZBoard prepares the candidate configuration, private data, and runtime before committing the change. A successful upgrade preserves the enabled or disabled state; a failed preparation keeps the previous version and committed data. Packages without a tested-host declaration for the current version require the plugin to be disabled before upgrade.

To restore a retained version, disable the plugin and select the version in its detail page. The host checks configuration and data compatibility. Restoring an older binary does not perform a downward data migration.

## Disable, uninstall, and remove data

| Operation | Result in ZBoard |
| --- | --- |
| Disable | Stops the runtime and revokes plugin UI/call sessions; keeps installation and data. |
| Uninstall | Stops the plugin and removes its program and pages; keeps configuration, private data, and operation history. |
| Clear retained data | Available after uninstall; clears plugin configuration and private data through the host. |

Core records such as accounts, identity bindings, orders, and credentials remain owned by ZBoard. Removing a plugin does not delete these records or undo completed business transactions.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Marketplace is empty | Whether a catalog is configured, reachable, correctly signed, and unexpired. |
| Import is rejected | Publisher trust, package digest, host/API compatibility, and target platform. |
| Plugin fails to start | Plugin operation history, host logs, configuration, and platform execution policy. |
| Settings cannot be saved | Refresh after a revision conflict and reapply the intended changes. |

For OAuth-specific issues, see the [configuration reference](../zboard/oauth/docs/configuration.md). Include plugin and host versions and sanitized logs when [reporting a bug](../CONTRIBUTING.md).
