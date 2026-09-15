# Unified marketplace contracts

**English** · [简体中文](registry-format.zh-CN.md)

The marketplace has three explicit layers. None replaces host-side package verification.

## Product registry

`catalogs/plugins.json` is schema version 3 and is the sole authoritative directory source. First admission and record updates submit an immutable release listing through an Issue Template. After a maintainer applies `status:accepted` on that Issue, the Action commits its `listing` verbatim together with the generated host projections; no admission PR is created. Names, descriptions, categories, and links must not be edited directly or overridden by site code. A product has a stable `id`, original publisher metadata, repository, admitted publisher key, release-source pointer, and one or two `targets`.

Reviewable JSON Schema files live in [`schemas/`](../schemas/). `scripts/marketplace_schema.py` is the executable strict boundary and additionally checks cross-document identities, host namespaces, transitions, and immutable artifact locations.

Each target declares `host`, its durable `package_id`, and reviewed `surfaces` and `capabilities` ceilings. A single-host author declares only one target. Product IDs and `(host, package_id)` pairs are unique and cannot be silently reassigned. `withdrawn: true` is the explicit removal signal.

`catalogs/zboard.json` and `catalogs/znet-sink.json` are generated schema-v2 compatibility projections. Run `python3 scripts/generate_catalogs.py`; do not edit them independently.

## Publisher release manifest

Every GitHub Release contains one `marketplace-entry.json`. Schema version 1 records `product_id`, registered repository and publisher, source tag and full commit, and exactly one release with:

- canonical SemVer, `stable`, `rc`, or `dev` channel, publication time, and release-notes URL;
- one or two host targets with package ID, inclusive minimum and optional exclusive maximum host version, surfaces, and capabilities;
- immutable GitHub Release artifacts with OS, architecture, byte size, SHA-256, and package signature.

The release must use registered identities and stay inside every target ceiling. The generator reads signed `.zbplugin` and `.zspkg` packages, checks their embedded identities, and computes size and digest; it never executes them.

## Derived snapshot

`.generated/marketplace-snapshot.json` is schema version 1. It joins current registry information, the publisher's public release feed, and validated releases, and supplies `snapshot_version`, `generated_at`, source freshness, products, targets, releases, compatibility, and artifacts. `release_feed` retains at most 20 recent stable or prerelease updates and marks whether each passed marketplace-manifest validation; only target-level `releases` participate in host installation selection. It is derived build output, not another human-maintained registry.

If one publisher is temporarily unavailable, a build may retain that product's last valid releases and mark it stale. A current registry withdrawal always wins and cannot be restored from stale data.
