# Marketplace development

**English** · [简体中文](development.zh-CN.md)

Use Python 3.10+, Node.js 22, and pnpm 9.9. The checked-in dependency lock is based on Minted Directory Astro commit `f71c8ae3fcff741285107415701fb6d1390f55b6`; see [third-party notices](../THIRD_PARTY_NOTICES.md).

Run the complete local gate:

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check

`pnpm build` deliberately uses `tests/fixtures/releases.json`, which is marked as test data, and therefore produces a reproducible source-only local snapshot. A production build runs `scripts/build_snapshot.py` without `--fixture` and then `pnpm build:site`, producing the site, complete snapshot, and six host/channel static API files.

Edit only `catalogs/plugins.json`, then regenerate compatibility projections with `python3 scripts/generate_catalogs.py`. Generated snapshots, site output, packages, private keys, and credentials remain untracked. Host installers and plugin source stay in their owning repositories.
