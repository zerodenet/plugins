# Unified marketplace contracts

**English** · [简体中文](registry-format.zh-CN.md)

## Product registry

`catalogs/plugins.json` is schema version 3 and the sole maintained directory. Automation records complete publisher listings from public immutable release assets after technical validation, without human admission review. Stable product ID, publisher key, repository, release-source pointer and host/package IDs identify the source. Names, descriptions and links are recorded verbatim.

`surfaces` and `capabilities` are declarations, not marketplace ceilings or grants. New version declarations do not need registration updates. The market validates unique identifier arrays without a frozen UI allowlist; hosts decide which APIs and surfaces they support. `withdrawn: true` is explicit removal. Identities cannot be silently reassigned.

[JSON schemas](../schemas/) describe the structures. `scripts/marketplace_schema.py` additionally checks identities, namespace syntax, transitions and immutable artifact locations. `catalogs/zboard.json` and `catalogs/znet-sink.json` are generated schema-v2 compatibility projections, not independently edited sources.

## Publisher release manifest

Each GitHub Release provides `marketplace-entry.json` schema version 1: product/repository/publisher identity, source tag and full commit, release version/channel/time/notes and host targets. Each target declares durable package ID, host-version range, its own surfaces/capabilities, and immutable artifacts with OS, architecture, size, SHA-256 and signature metadata. A release must retain source and package identity; permissions need not be subsets of the initial listing.

The package generator reads signed `.zbplugin` and `.zspkg` files and never executes them. Hosts independently verify package signatures and require user confirmation for permissions according to host policy.

## Derived snapshot

The schema-v1 snapshot joins current registry metadata, at most 20 publisher release-feed items and valid per-target releases. Only target `releases` participate in installation selection. Permission expansion remains discoverable. Target-level declaration arrays summarize the union of registered and discoverable release declarations for older consumer compatibility; they do not authorize any selected package. Release-level arrays remain exact.

Snapshots and six host/channel static APIs share one content hash. Publisher outages retain last usable releases with a stale marker; explicit withdrawal wins. Generated snapshots, packages and site output remain untracked.
