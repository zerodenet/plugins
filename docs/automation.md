# Marketplace admission automation

**English** · [简体中文](automation.zh-CN.md)

Automation processes first-time admission applications. It does not poll publisher repositories for new versions and never opens one issue or pull request per release.

Applicants provide one immutable marketplace-entry.json from a stable onboarding release. The workflow verifies the repository and tag, source commit, GitHub-recorded asset sizes and digests, and derives a version-free directory entry. It never checks out contributor code or executes packages.

Maintainers review plugin purpose, publisher/key ownership, capability and surface ceilings, license, security contact, migration and uninstall behavior, and real host evidence before merging the admission PR. Once merged, the host discovers Stable, RC, and Dev releases directly from the admitted repository.

Routine releases and repository-owned basic-information changes produce no marketplace event. A new marketplace application or focused directory PR is required only for trust-boundary or source-contract changes. Labels describe application state; they do not publish plugin versions or authorize host capabilities.

The workflow runs for application issues, admission PR completion, main updates, and manual reconciliation. There is intentionally no scheduled release synchronization.
