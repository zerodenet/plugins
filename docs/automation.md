# Marketplace automation

**English** · [简体中文](automation.zh-CN.md)

The market proposes catalog changes from published GitHub releases. It does not rebuild plugins, execute their packages, sign releases on behalf of publishers, or merge its own proposals.

## Submissions

Publish `marketplace-entry.json` alongside the signed packages, then include its immutable GitHub Release asset URL in the submission form. Existing issues containing that URL are also supported. The workflow checks the release and opens a catalog PR. Correcting the issue reruns validation; one bot comment is maintained instead of adding repeated status messages.

The metadata must describe exactly one release. Its repository, version and source commit must match the publishing repository and tag, including annotated tags. Every artifact URL, SHA-256 and size must match an asset in that release. Downloads are restricted to GitHub HTTPS release hosting; metadata is limited to 256 KiB. No contributor code is checked out or executed by the privileged workflow.

These checks establish consistency with GitHub's release records. Maintainers still verify publisher/key ownership, package signatures, requested capabilities, migration behavior and actual host test evidence before merging. A submitted public key does not grant trust. Merge catalog PRs by squash or rebase to keep `main` linear.

## Labels

Definitions live in [.github/labels.json](../.github/labels.json). The workflow creates missing labels and updates their colors and descriptions, preserving unrelated labels.

| Label | Meaning |
| --- | --- |
| `plugin:submission` | Initial listing or submitted release |
| `plugin:update` | Release update found by the scheduled check |
| `host:zboard`, `host:znet-sink` | Host inferred from validated metadata |
| `status:needs-info` | Missing or invalid submission metadata |
| `status:in-review` | Catalog PR awaits review |
| `status:accepted` | Proposal merged or release already present on `main` |
| `status:closed` | Submission or proposal closed without inclusion |

Labels describe workflow state. Applying `status:accepted` manually cannot write to a catalog or approve an installation. Edits are read again before preparing a PR. A merge closes a linked submission only if its recorded body still matches, or a subsequent reconciliation verifies that its release is already recorded.

## Upstream updates

Every six hours, the workflow checks the latest stable GitHub Release for each plugin with an already recorded release and publisher key. Source-only listings are excluded. New releases create separate PRs and append to the existing history. Plugin ID, host, repository and publisher-key changes are rejected. A changed artifact for an existing version is rejected as well.

A deterministic branch identifies each plugin/version proposal. Repeated runs reuse the existing PR, including closed proposals; rejected updates are not silently reopened. Reopen the proposal manually after resolving review feedback. When several upstream versions appear between scans, the latest stable release is proposed; intermediate versions can be submitted individually.

The workflow also runs after a main-branch push and can be started from **Actions → Marketplace synchronization → Run workflow**. Commits are made as `github-actions[bot]`. The OAuth repository needs no cross-repository token: publishing its release metadata is sufficient for subsequent scheduled discovery after first inclusion.

## Repository setup

Enable **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**. The workflow requests only repository contents, issues and pull-request write permissions; it never approves PRs. Organization policy may control this setting. A permission failure fails the Action rather than labeling a publisher's valid submission as incorrect.

GitHub may require a maintainer to approve checks on PRs created with `GITHUB_TOKEN`; check the PR's workflow banner. See [GitHub's workflow trigger rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow). No personal access token is required by this implementation.

## Installation feeds

Merging a PR updates `catalogs/zboard.json` or `catalogs/znet-sink.json`. These remain source catalogs. Publishing and renewing a signed host installation feed is a separate distribution operation with a separate market signing key; this workflow does not turn source JSON into an installable feed.
