# Repository guidelines

## Scope and ownership

- This is the shared ZeroDeNet plugin repository. Plugin source lives under `<host>/<plugin>/`; each plugin owns its dependencies and tests.
- Read `README.md`, `CONTRIBUTING.md` and `docs/governance.md` before changes. For publishing, also read `docs/publishing.md`.
- Market metadata never grants host capabilities. Core business state, permissions, private storage and lifecycle transactions remain owned by each host.
- Do not add direct database access, arbitrary host commands, administrator tokens or node credentials to a plugin. Missing capabilities require a dedicated host contract first.
- Keep ZBoard plugin APIs out of the client and Zero kernel. Do not assume a shared market implies a shared runtime or package format.

## Working changes

- Preserve plugin IDs, publisher identity and historical commits. Do not initialize nested Git repositories.
- Keep `.local/`, keys, databases, build outputs and local Go workspaces untracked. Never copy a whole development directory into a release package.
- Resolve the host packager with explicit `--zboard` or `ZBOARD_DIR`; do not embed workstation paths or silently use an adjacent checkout.
- Follow existing code style and keep changes focused. Update documentation when paths, configuration or public behavior changes.

## Validation and delivery

- Run `sh scripts/check.sh` from the root. It checks the OAuth plugin's Go formatting, race tests, vet, build, real process protocol and browser bridge tests.
- For packaging changes, build a signed development package with an explicitly selected host checkout and inspect its manifest and file list. Development keys never become official publisher keys.
- Record target-platform and live-provider validation limits honestly. Do not claim a market URL or release exists before publication is verified.
- Before committing, inspect staged files and verify effective author and committer identity. For this maintainer's checkout, match the current ZBoard repository using repository-local Git configuration; never change global identity.
- Use PRs and linear history for subsequent changes after initialization. Do not rewrite shared history or publish a release as a side effect of a source-code change.
