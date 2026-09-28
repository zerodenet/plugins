# Marketplace automation

**English** · [简体中文](automation.zh-CN.md)

## Automatic registration

`marketplace.yml` runs default-branch code for first registration and record updates. Opened, edited or reopened publisher Issues are checked and registered automatically. Push/manual reconciliation retries open submissions. There is no `status:accepted` decision gate or permission review.

Automation checks the public immutable release listing, submitter repository control, tag/source identity, asset location, size and digest. Stable, RC and Dev are supported. It copies `listing` verbatim, commits the authoritative registry and both host projections atomically, marks `status:registered`, closes the Issue and explicitly dispatches publication. This avoids `GITHUB_TOKEN` suppression of subsequent push workflows. Incorrect/unavailable records receive `status:needs-info`. Human collaborators can use `status:closed` to close invalid submissions; ordinary automation labels do not recursively trigger registration.

The Issue body/author/type and `main` must remain unchanged before commit. Repository transfers require automatically verified control of both sources. Packages are never executed. Source control validation is an identity check, not a plugin purpose, permission or runtime audit.

## Publication

`publish-marketplace.yml` runs for relevant main changes, every three hours or manually. It obtains bounded publisher metadata, retains last usable data during upstream outages, and builds the same snapshot for GitHub Pages and Cloudflare Pages. Permission and UI expansion do not filter releases; hosts verify and authorize selected packages independently.

Cloudflare Direct Upload uses `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_PLUGINS_PROJECT` (default `zero-plugins`). The production domain is `plugins.zerodenet.org`; GitHub Pages retains `/plugins/` as fallback. Hosts query `/api/plugins/{host}/{channel}.json` and filter platform/version locally. Credentials stay in CI; browser requests do not fan out to publisher repositories. Explicit withdrawals win over stale fallback.
