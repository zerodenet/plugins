# Installation and trust

**English** · [简体中文](usage.zh-CN.md)

Choose an admitted plugin in the host marketplace. Its name, description, license, maintainers, and documentation links come from repository-owned `marketplace.json`; version lists, timestamps, and release notes come from that repository's Releases. The host lets an administrator select Stable, RC, Dev, or an exact version and verifies the selected package against the admitted publisher key and capability ceiling before installation.

Online discovery is not enough by itself. The host also validates plugin identity, version, platform, package digest and signature, host/API compatibility, and requested capabilities. Stable is the default channel; RC and Dev are explicit administrator choices.

Offline import is independent of marketplace admission. It supports development testing, private distribution, local customization, and non-market plugins. The administrator explicitly accepts their source and signing identity, while the host applies the same package, compatibility, and lifecycle checks.

ZBoard owns accounts, registration policy, credentials, orders, node publication, and committed business records. Plugins own their integration logic and contributed UI. Installing or removing a plugin does not transfer ownership of core data.
