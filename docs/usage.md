# Choosing and operating plugins

**English** · [简体中文](usage.zh-CN.md)

## Choose your host

A plugin is installed into a specific application. Select the host collection first, then check the plugin's supported host/API versions and operating system. Package availability and setup instructions are maintained with that collection.

- [ZBoard installation and operation](https://github.com/zerodenet/plugins/blob/zboard/docs/usage.md)
- [ZNet Sink integration status](https://github.com/zerodenet/plugins/blob/znet-sink/README.md)

The public marketplace is planned. Until signed catalogs and releases are published, development packages follow the build instructions on the host branch.

## Installation and trust

Host administrators select trusted publishers. The host verifies the package's origin, integrity, compatibility, and requested capabilities before installation. Online and offline installation must enforce the same host contract.

Configuration, enabling, disabling, and upgrades are managed through the host application. Follow the plugin's setup guide for provider credentials and any external service registration.

## Data and upgrades

The host owns plugin private storage, migrations, and retention policies. Before upgrading, follow its backup instructions and review the new version's compatibility requirements. Removing a plugin does not remove core business records such as accounts or completed transactions.

Refer to the host-specific operation guide for exact uninstall and data-removal behavior. Report problems with the host, plugin version, platform, and sanitized reproduction steps.
