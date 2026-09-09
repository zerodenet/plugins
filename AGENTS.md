# Repository guidelines

**English** · [简体中文](AGENTS.zh-CN.md)

## Project scope

Read `README.md`, `CONTRIBUTING.md`, and `docs/governance.md` before changing the repository. Read `docs/publishing.md` when working on releases.

Plugin source lives under `<host>/<plugin>/`; each plugin owns its manifest, dependencies, and tests. Host implementations and public SDKs remain in their respective repositories. Preserve plugin IDs, publisher identity, and existing history. Do not initialize nested Git repositories.

## Architecture

Market metadata does not grant host capabilities. Each host owns permission checks, core business state, private storage, and lifecycle transactions. Plugins consume dedicated, versioned host APIs. Do not introduce direct database access, arbitrary host commands, administrator tokens, or node credentials.

A shared marketplace does not imply a shared runtime. Keep ZBoard APIs out of the client and Zero kernel. New capabilities require a host contract and validation before plugin integration.

## Documentation

English is the default; maintain a corresponding `.zh-CN.md` page for public documentation. Include reciprocal language links and keep translated navigation in the selected language. Update both versions when behavior, commands, or requirements change.

Write documentation for users and contributors. Keep local migration notes, workstation paths, author-account setup, and task reports outside public guides. Preserve technical limits in the relevant reference or architecture page. Mark proposed contracts as drafts.

## Validation

Run `sh scripts/check.sh` from the root. For documentation changes, also check links, language pairs, and command examples. For packaging changes, build with an explicitly selected host checkout and inspect the package manifest, signature, and file list.

Use `--zboard` or `ZBOARD_DIR` to locate the host packager. Keep `.local/`, keys, databases, generated packages, and local Go workspaces untracked. Development keys are for test hosts only.

## Delivery

Inspect staged files and verify the effective Git author and committer before committing. Use repository-local settings for checkout-specific identity requirements; do not change global identity. Follow the PR process and keep shared history linear.

Report automated, host integration, target-platform, and live-provider validation separately. Verify publication before claiming a catalog or release is available. Source changes do not implicitly publish a plugin release.
