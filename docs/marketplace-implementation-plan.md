# Unified marketplace implementation plan

**English** · [简体中文](marketplace-implementation-plan.zh-CN.md)

Status: in progress. Use Astro and a pinned Minted Directory Astro baseline, with information hierarchy informed by Ever Works. Existing host catalogs remain generated compatibility projections until migration acceptance.

## Scope and contracts

One marketplace serves website discovery and fixed host/channel API paths for ZBoard and ZNet Sink. Central registration owns stable product identity, trusted publisher source, host package identities and reviewed ceilings. Publisher repositories own generated multi-target release manifests. A derived snapshot joins validated data for the site and API; it never replaces host-side package verification, authorization, lifecycle, rollback, or installed data.

`/api/plugins.json` publishes the complete discovery snapshot, while `/api/plugins/{host}/{channel}.json` publishes build-time host/channel projections. Each host filters host version, operating system, and architecture locally and never substitutes another host or incompatible artifact. Source-only products remain web-discoverable but absent from host channel files; last-known-good release data survives temporary upstream failure while withdrawal wins immediately.

The Astro site and static JSON API use one build output. GitHub Pages atomically publishes pages, the snapshot, host/channel files, and schemas; the first release has no Cloudflare Worker dependency. GitHub credentials remain build-only. A dynamic service is considered only for future authenticated writes, personalization, or genuinely server-side search. The first release excludes accounts, comments, favorites, ratings, payments, installation counts and an administration backend.

## Stages

1. P0: isolate dirty trees, inventory live identities/releases/consumers, and pin upstream commits and licenses.
2. P1: version product, release and snapshot schemas; enforce identity, host, capability, key and transition boundaries; update admission review.
3. P2: generate manifests from real signed packages and cover single/multi-target and tampering fixtures without executing submitted code.
4. P3: build bounded snapshots that separate public stable/prerelease activity from validated installable releases, plus host/channel static API projections with client-side compatibility filtering, cache and recovery tests.
5. P4: build search, host/category filters, cards, submitted publisher records and links, release history, exact registered surface/capability keys with host-standard descriptions, a reserved ratings/reviews position, and an on-site submission flow. Maintain public usage, publishing, security, data, and responsibility guidance only at `docs.zerodenet.org/marketplace/`, with clear links from the marketplace instead of a duplicate documentation copy. Render product fields verbatim without translations, rewrites, or inferred links, keep host-protocol descriptions separate and retain every raw key, keep GitHub for final identity confirmation and audit history, and never expose an install action without a validated artifact.
6. P5: migrate both consumers to fixed host/channel files with local compatibility filtering, local verification, and generated legacy fallbacks; accept real signed installs/upgrades separately.
7. P6: publish the static site, snapshot, six host/channel API files, and schemas automatically with GitHub Pages; accept the repository-path URL, then configure `plugins.zerodenet.org` and verify refresh, outage fallback, and rollback. Report code, commit, push, deployment, and E2E independently.

See [implementation status](marketplace-implementation-status.md) for actual evidence and remaining release gates.
