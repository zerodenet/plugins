# Shared marketplace architecture

**English** · [简体中文](marketplace-design.zh-CN.md)

## Purpose

The marketplace is a curated directory and a convenient host entrypoint. It lets ZBoard, ZNet Sink, and future hosts browse admitted plugins and lets users understand, obtain, install, and manage them without copying developer-owned release history into a central repository.

Marketplace admission records that the host team reviewed the plugin's purpose and its stable trust boundary. It is not a repeated approval queue for every software version.

## Ownership

| Component | Owns |
| --- | --- |
| Marketplace directory | Admission, identity, repository, publisher key, metadata/release-source pointers, host scope, capability and UI ceilings, withdrawal |
| Plugin repository | Basic information, source, Stable/RC/Dev lifecycle, immutable release metadata, packages, digests, compatibility and release notes |
| Host | Browse/search UI, release discovery, channel and exact-version selection, signature and policy enforcement, install/upgrade/downgrade/uninstall, local state and audit |
| Offline import | Development testing, private distribution, local customization, and non-market plugins under explicit administrator trust |

## Online flow

1. The host reads its marketplace directory, then obtains basic information from each repository's `marketplace.json`.
2. On a plugin detail page, the host asks the registered release-source adapter for published versions and release notes.
3. The host accepts supported Stable, RC, and Dev tags and fetches the selected immutable metadata asset.
4. The host verifies repository and plugin identity, the admitted publisher key, capability and UI ceilings, target platform, package digest, package signature, and host compatibility.
5. The administrator installs, upgrades, downgrades, or pins an exact version. Stable is the default channel; RC and Dev are opt-in.

Release discovery is not authorization. A repository release can be displayed only when it follows the registered adapter, and it can be installed only when its signed package remains inside the admitted boundary.

## Updates and revocation

Routine plugin releases and basic-information changes never modify the directory. Repository relocation, publisher/key rotation, metadata/release-source contract changes, new host support, or broader capabilities/surfaces require marketplace review. The directory also owns suspension and withdrawal signals; hosts decide how those affect installed instances and offline operation.

The first implemented adapter is GitHub Releases with one marketplace-entry.json per release. Other adapters may be added later without turning the marketplace back into a version ledger.
