# Unified marketplace implementation status

**English** · [简体中文](marketplace-implementation-status.zh-CN.md)

This page records implementation evidence for the marketplace plan. A branch commit or push does not claim merge, deployment, or production installation acceptance.

## Migration baseline

The two legacy schema-v2 host catalogs are replaced by one schema-v3 product registry and generated compatibility projections. Product-facing registry fields enter through Issue Templates; a maintainer decision is recorded with an Issue status label, then the Action atomically commits the verbatim fields and projections without an admission PR. Publisher releases can describe one or two explicit host targets in one generated manifest. The site consumes the full validated snapshot, while both hosts consume fixed host/channel projections and filter version and platform locally. Package verification, authorization, lifecycle, and installed data remain host-owned. Legacy projections retire only after supported host versions use the API for a documented compatibility window.

Minted Directory Astro is pinned at `f71c8ae3fcff741285107415701fb6d1390f55b6` under MIT. Ever Works at `7d99ece8f06a99988721b83a9dbb878d7bfad7b8` informed information hierarchy only; no AGPL source was copied. See `THIRD_PARTY_NOTICES.md`.

## Progress

- [x] P0 baseline, dirty-tree isolation, live release inventory, consumer paths, upstream commits and licenses.
- [x] P1 unified registration/release contracts, transition checks, generated host projections, and admission automation.
- [x] P2 artifact-derived manifest tooling, templates, positive and negative tests, with no package execution in central CI.
- [x] P3 bounded snapshot build, the latest 20 stable/prerelease publisher updates, separation of publisher activity from validated installable releases, last-known-good recovery, withdrawal precedence, six host/channel static API files, build verification, and client-side filtering tests.
- [x] P4 Astro discovery, verbatim submitted publisher records and links, release history, exact surface/capability keys with host-standard descriptions, a reserved ratings/reviews position, first-admission and record-update entry points, and links to the canonical public documentation, plus desktop and 390×844 mobile inspection. Installation, publishing, security, and API guidance lives only at `docs.zerodenet.org/marketplace/`; the marketplace repository does not keep a second public copy. Product fields are not translated, rewritten, or inferred; protocol-description dictionaries contain no product-specific overrides. The signed-in publisher confirms the GitHub Issue, a maintainer decides with an Issue status label, and the Action commits an accepted record directly. Unverified artifacts never produce download actions.
- [ ] P5 consumer code and focused tests are complete; deployed API plus real signed install/upgrade/data-preservation E2E remains.
- [ ] P6 scheduled/change-triggered builds, review artifacts, Pages base-path support, and automatic GitHub Pages publication of the site, snapshot, six host/channel APIs, and schemas are configured. Enabling Pages, merging to `main`, accepting the first live deployment, configuring `plugins.zerodenet.org`, and exercising cache refresh and rollback remain.

The current delivery stops at feature branches and does not represent a merge or deployment. The first release requires no Cloudflare credentials: select GitHub Actions once in the repository Pages settings, merge, verify the Pages URL, and then configure `plugins.zerodenet.org` as the custom domain. Pages publishes the static site, unified snapshot, `/api/plugins.json`, six host/channel JSON files, and schemas together. Both hosts retain a read-only fallback to the generated schema-v2 catalogs without weakening local package verification.
