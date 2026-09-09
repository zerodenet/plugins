# Installation and trust

**English** · [简体中文](usage.zh-CN.md)

Choose a plugin from the host's source catalog and read its repository documentation. Check supported host/API versions, target platform, required capabilities and publisher ownership before installing. A source listing with no releases cannot be installed.

For ZBoard, obtain the publisher public key through a trusted channel and configure host trust. Download a matching signed `.zbplugin` from the publisher, compare SHA-256 with the release metadata, and use offline import in plugin management. ZBoard validates and controls installation, configuration, enabling, upgrading and removal. See the plugin's installation guide for the exact procedure.

The source catalogs in this repository are unsigned editing records. They cannot be used as `plugins.catalog_url`; online installation needs a separately published signed host catalog and a download endpoint supported by that host. Current distribution limitations are described in [Publishing](publishing.md).

Catalog and package signatures establish origin and integrity. They do not grant permissions or make arbitrary native code safe to execute. ZBoard native plugins are trusted subprocesses, not an OS sandbox. Review the publisher and capability request before granting trust.

ZBoard owns account and registration policy, credentials and node publication. Disabling or uninstalling OAuth does not transfer ownership of user records to the plugin. Data retention and migration are controlled by the host lifecycle. ZNet Sink's host runtime and installation contract remain under development; an empty client catalog does not imply an available client plugin runtime.
