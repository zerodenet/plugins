# Contributing

**English** · [简体中文](CONTRIBUTING.zh-CN.md)

Contributions can include bug fixes, new integrations, tests, documentation, and translations.

## Before you start

For a small fix, open a pull request describing the problem and the change. For a new plugin, host API, or marketplace format, open an issue first so maintainers can discuss scope and compatibility before implementation.

Bug reports should include plugin and host versions, operating system, reproduction steps, and expected and observed behavior. Provide a minimal configuration with credentials and personal data removed. Use [SECURITY.md](SECURITY.md) for vulnerabilities.

## Development workflow

Fork the repository, or use a branch if you have write access. Select the base branch and PR target by scope:

| Scope | Base and merge target |
| --- | --- |
| Platform overview, shared policies, and marketplace proposals | `main` |
| ZBoard plugins, host guides, and build checks | `zboard` |
| ZNet Sink plugins and client integrations | `znet-sink` |

For example, when editing ZBoard plugin documentation:

```sh
git switch zboard
git pull --ff-only
git switch -c docs/installation-guide
```

Keep each pull request focused on one change. Follow the existing style, update affected documentation, and add tests for changed behavior. See [Development](docs/development.md) for local setup.

Run the checks provided by the relevant branch before submitting. The `zboard` branch uses `sh scripts/check.sh`; documentation changes require link, language-pair, and example checks. Run `git diff --check` on every branch.

Use your own Git author identity. Commit source files and dependency lockfiles; keep credentials, local workspaces, runtime data, and generated packages outside version control.

## Adding a plugin

Keep official plugin source on its host branch, using the `<host>/<plugin>/` layout. OAuth currently lives at `zboard/oauth/` on `zboard`. Include:

- A README with the use case, supported host versions, setup instructions, and limitations.
- A manifest with a stable plugin ID, required capabilities, and entry points.
- Locked dependencies, a build procedure, and tests integrated into the root check script and CI.
- Configuration and data compatibility notes, including required host-managed migrations.

Discuss missing capabilities in the host repository before building the integration. [Architecture](docs/governance.md) defines the boundary between plugins and core services. External plugins may retain their own repositories; marketplace submission will follow the distribution contract once adopted.

## Documentation and translations

English is the default documentation language. Simplified Chinese translations use the same filename with a `.zh-CN.md` suffix. Each page links to its counterpart; translated pages link to other translated pages where available.

Update both versions in the same pull request. Keep commands, configuration keys, identifiers, version constraints, and technical meaning aligned. Write for the intended reader: project introductions belong in READMEs, procedures in guides, and field definitions in references. Workstation details and development-session notes belong outside public documentation.

## Review and merge

Describe the user-visible result, compatibility impact, and validation performed. Distinguish automated tests from host integration and live provider testing. Maintainers may request a smaller change or more coverage where public contracts are affected.

After review and passing checks, maintainers merge into the appropriate target using squash or rebase to keep each long-lived branch linear. Host branches are not merged wholesale into `main`. Synchronize shared documentation by file or isolated commit so that code or implementation deletions do not cross branch boundaries. Releases follow the separate [publishing process](docs/publishing.md). See [Project governance](GOVERNANCE.md) for decisions and community expectations.
