# Marketplace automation

**English** · [简体中文](automation.zh-CN.md)

Admission and publication are separate workflows.

`marketplace.yml` handles first admission and updates to existing records. It runs reviewed `main` code, validates one stable `marketplace-entry.json`, checks GitHub tag/source and asset records, and copies the complete `listing` verbatim to a dedicated branch before opening a review PR. Names, descriptions, categories, links, and all other product fields are not translated, rewritten, or inferred. Maintainers still review publisher/key ownership, package signatures, every host target and capability ceiling, and actual execution evidence. Contributor packages are never executed.

`publish-marketplace.yml` runs when the registry/site changes, every three hours, or manually. It validates the registry, obtains bounded publisher release metadata at build time, reuses the last valid per-product data during temporary upstream failures, builds the Astro site and host/channel static JSON API, uploads one review artifact, and atomically publishes the site, marketplace snapshot, API, and schemas through GitHub Pages.

Cloudflare credentials are not required in this phase. The repository needs one setup action: choose **GitHub Actions** under **Settings → Pages → Build and deployment → Source**. Relevant changes on `main` then publish automatically. The build uses the Pages-provided base path, so it also works at the repository URL before a custom domain is enabled.

`plugins.zerodenet.org` is the recommended marketplace-specific domain. Configure it in Pages and DNS after the first Pages deployment is accepted. Hosts read `/api/plugins/{host}/{channel}.json` and filter version and platform locally; existing schema-v2 URLs remain a migration-only read fallback. A future Worker is an optional enhancement, not a prerequisite for a usable marketplace.

GitHub credentials exist only in the build job. Visitor browsing never fans out to publisher repositories. A registry withdrawal is applied before stale fallback.
