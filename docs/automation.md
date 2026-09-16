# Marketplace automation

**English** · [简体中文](automation.zh-CN.md)

Admission and publication are separate workflows.

`marketplace.yml` handles first admission and updates to existing records. It runs reviewed `main` code, validates one stable `marketplace-entry.json`, checks GitHub tag/source and asset records, and marks the application Issue `status:in-review`. A maintainer reviews publisher/key ownership, package signatures, every host target and capability ceiling, and actual execution evidence on that Issue. Applying `status:accepted` is the approval decision: the Action validates the immutable release again, creates one atomic commit on `main` containing the verbatim `listing` and both generated host compatibility projections, and explicitly dispatches the Pages publication workflow. The `workflow_dispatch` avoids relying on a `push` event suppressed for commits made with `GITHUB_TOKEN`. Applying `status:closed` closes the application without admission. Admission does not create a separate branch or pull request. Names, descriptions, categories, links, and all other product fields are not translated, rewritten, or inferred. Contributor packages are never executed.

GitHub restricts label management to repository collaborators with the required repository role. The workflow accepts only a human `labeled` event for the two decision labels; edits, reopen events, bot labels, pushes, and manual reconciliation can validate an application but cannot approve it. If the Issue body changes, the approval label is removed and a maintainer must review and apply it again. The commit checks that both the Issue and `main` stayed unchanged before moving the branch ref, so concurrent changes fail closed.

`publish-marketplace.yml` runs when the registry/site changes, every three hours, or manually. It validates the registry, obtains bounded publisher release metadata at build time, reuses the last valid per-product data during temporary upstream failures, and builds repository-path and root-path outputs from the same snapshot for GitHub Pages and Cloudflare Pages. The site, marketplace snapshot, API, and schemas retain one snapshot version within the run.

Cloudflare Direct Upload uses the organization-level `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, and the plugin-repository-scoped `CLOUDFLARE_PLUGINS_PROJECT`; the project name is `zero-plugins`. The token only needs Cloudflare Pages edit access for the target account. GitHub Pages continues to publish the `/plugins/` path as an independent fallback.

The production domain `plugins.zerodenet.org` is attached to the Cloudflare Pages project. Hosts read `/api/plugins/{host}/{channel}.json` and filter version and platform locally; existing schema-v2 URLs remain a migration-only read fallback. A future Worker is an optional enhancement, not a prerequisite for a usable marketplace.

GitHub credentials exist only in the build job. Visitor browsing never fans out to publisher repositories. Admission commits are made only after the Issue label decision, and ordinary marketplace publication remains a separate workflow. A registry withdrawal is applied before stale fallback.
