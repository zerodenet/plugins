# Repository guidelines

**English** · [简体中文](AGENTS.zh-CN.md)

## Branch ownership

Read `README.md`, `CONTRIBUTING.md`, and `docs/governance.md` before changes. `main` contains the platform overview and shared documentation only. Plugin source, packaging scripts, and runtime CI belong to the corresponding `zboard` or `znet-sink` branch. Check the current branch before editing.

Keep source under `<host>/<plugin>/` on the host branch. Preserve plugin IDs, publisher identity, public module paths, and historical commits. Host implementations and public SDKs remain in their respective repositories. Do not initialize nested Git repositories.

## Architecture

Each host owns capability checks, core business state, private storage, and lifecycle transactions. Plugins consume dedicated, versioned host APIs. Do not introduce database access, arbitrary host commands, administrator tokens, or node credentials. A shared marketplace does not imply a shared runtime or global permissions.

## Documentation

English is the default. Maintain matching `.zh-CN.md` pages, reciprocal language links, and consistent commands and configuration examples. Links to another branch must name that branch explicitly. Keep workstation information and task reports outside public guides. Mark proposals as drafts.

## Validation

On `main`, check documentation links, language pairs, examples, and the absence of tracked implementation files. On `zboard`, run `sh scripts/check.sh`; packaging changes also require a signed development package check. On `znet-sink`, validate the documentation until an implementation provides its own checks; do not claim client runtime coverage before it exists.

Use `--zboard` or `ZBOARD_DIR` for the host packager. Keep local workspaces, credentials, runtime data, and generated packages untracked. Development keys are for test hosts only.

## Delivery

Verify the Git author and committer against any checkout-specific user requirements. Use repository-local identity settings. Target PRs at the branch that owns the change and keep each long-lived history linear. Shared documents may be synchronized as isolated changes; do not merge host branches into `main` or apply a branch-layout removal to a host implementation.

Source changes do not publish a plugin release. Record automated, host, target-platform, and live-provider verification separately.
