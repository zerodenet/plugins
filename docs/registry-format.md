# Directory format

**English** · [简体中文](registry-format.zh-CN.md)

Schema version 2 describes marketplace admission. It deliberately contains no plugin version, source commit, artifact, digest, compatibility range, or release history.

## Catalog

Each host file contains schema_version, host, and plugins. A plugin ID occurs once per host. The same project may apply separately to different hosts because capabilities never cross host boundaries.

## Plugin entry

| Field | Meaning |
| --- | --- |
| id | Stable plugin identity within one host |
| repository | Publisher-owned public source and release repository |
| publisher.id, publisher.public_key | Stable package-signing identity admitted by the host team |
| metadata_source | Basic-information source in the plugin repository; currently root `marketplace.json` |
| release_source | Host adapter used to discover publisher-owned releases |
| surfaces | Maximum admitted UI surfaces |
| capabilities | Maximum admitted host capabilities |

The host reads names, descriptions, licenses, maintainers, and links from the admitted repository's `marketplace.json`. The current release-source adapter is github-releases. It reads published GitHub Releases, finds the configured metadata_asset in each accepted Stable, RC, or Dev release, and exposes the Release title, body, timestamp, and source link.

## Trust boundary

The admitted public key, repository, release-source adapter, surfaces, and capabilities form the listing's trust boundary. Hosts must still verify the selected package signature, identity, version, digest, platform, and compatibility. A package requesting a surface or capability outside the listing is rejected even when its signature is valid.

Routine releases and basic-information changes do not modify this directory. Repository transfer, publisher or key rotation, metadata/release-source contract changes, new hosts, and broader surfaces or capabilities require a focused marketplace update. Security withdrawals are also directory operations.

Release metadata is owned by the plugin repository and should be immutable per published version. The marketplace does not copy it into its own history.
