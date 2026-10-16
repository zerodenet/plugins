# Marketplace automation

**English** · [简体中文](automation.zh-CN.md)

Plugin submissions are reviewed in issues. Authors publish their own packages and submit a release URL; maintainers approve the issue with a label. The Action then updates the appropriate catalog on `main`. No catalog PR is required for a submission or release update.

## Submit and review

1. Publish `marketplace-entry.json` alongside the signed packages in a public GitHub Release, then use the [submission form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml).
2. The Action checks the metadata and applies the submission, host and review labels. A single bot comment records the review fingerprint. Invalid submissions receive `status:needs-info`; authors can edit the issue to resubmit.
3. A maintainer reviews publisher/key ownership, package signatures, capabilities, migration behavior and actual host test evidence. Add `status:approved` after these checks. The approving account must have repository write, maintain or admin permission; triage permission is insufficient.
4. The Action fetches and validates the release again, checks it against the review fingerprint, and commits only the affected host catalog. After success it replaces the approval label with `status:accepted` and closes the issue. The commit records the issue, approving account and review fingerprint.

The metadata must describe exactly one release. Its repository, version and source commit must match the publishing repository and tag, including annotated tags. Artifact URLs, SHA-256 digests and sizes must match the assets in that release. Metadata downloads are restricted to GitHub HTTPS release hosting and 256 KiB. The workflow checks out only reviewed `main` code; it does not build or execute submitted packages.

The fingerprint binds the issue body and validated release metadata. Editing or reopening a submission returns it to review. A changed release asset or a review snapshot newer than the approval also requires a new approval. Removing the approval label or closing the issue stops publication if observed before the catalog write. GitHub issue state and Git commits are separate API operations; changes after that write do not roll it back.

## Labels

Definitions live in [.github/labels.json](../.github/labels.json). The Action maintains their colors and descriptions while preserving unrelated labels.

| Label | Meaning |
| --- | --- |
| `plugin:submission` | Initial listing or submitted release |
| `plugin:update` | Release update found by the scheduled check |
| `host:zboard`, `host:znet-sink` | Host inferred from validated metadata |
| `status:needs-info` | Submission requires correction or a valid reviewer |
| `status:in-review` | Validated submission awaiting maintainer review |
| `status:approved` | Maintainer approval; triggers catalog publication |
| `status:accepted` | Release recorded on `main` |
| `status:closed` | Submission closed without inclusion |

`status:approved` is the review decision; `status:accepted` is the recorded result. Applying `status:accepted` manually does not publish anything. Neither label grants permissions inside a host or automatically trusts a publisher key.

## Upstream updates

Every six hours, the Action checks the latest stable GitHub Release for plugins with an already recorded release and publisher key. New versions create review issues and follow the same approval process. Source-only listings are excluded. Plugin ID, host, repository and publisher-key changes are rejected, as are modified artifacts for an existing version.

Existing author submissions and closed requests for the same repository/version prevent duplicate issues. Rejected requests are not reopened automatically. If multiple versions appear between scans, only the latest stable release is proposed; intermediate versions can be submitted individually.

A push to `main` or **Actions → Marketplace synchronization → Run workflow** also checks open submissions and upstream releases. These scans never treat a standing approval label as a fresh approval event. Publishing a release needs no publisher token with access to this marketplace.

## Permissions and recovery

The workflow requests `contents: write` and `issues: write`. It does not need PR permissions or the setting that allows Actions to create PRs. The catalog write uses `GITHUB_TOKEN` and must be permitted by repository and organization rules. If `main` requires every change to arrive through a PR, maintainers must first choose a repository policy or an authorized automation identity that permits this reviewed publishing path. The script does not change branch protection or bypass a denied write.

A denied write, API failure or conflicting catalog edit fails the Action and leaves the request open. Inspect the failed run, resolve the cause and rerun that approval run, or remove and reapply `status:approved`. Repeating a completed catalog write does not append the release again. If the submission or review snapshot changed, review it again and apply a fresh approval label.

Workflows are serialized with `queue: max` to retain up to 100 pending events; beyond that GitHub cancels additional queued runs. Reapply the approval label if its run was canceled. See [GitHub concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency). Catalog writes use the existing file SHA to avoid overwriting a concurrent edit.

The Action validates before writing because a `GITHUB_TOKEN` commit does not trigger another push workflow. Bot-created update issues are likewise validated within the same run. See [GitHub workflow triggers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

## Existing proposals and installation feeds

Older automation PRs are not consumed by this workflow. For a pending release, maintainers should review its submission issue and approve it there, then close any superseded PR. The workflow does not delete branches or close unrelated PRs.

Publication updates `catalogs/zboard.json` or `catalogs/znet-sink.json`. These remain source catalogs. Signed host installation feeds use a separate market key and distribution process. Catalog approval does not replace the host's package verification, trust decision or lifecycle controls.
