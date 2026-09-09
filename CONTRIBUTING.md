# Contributing

**English** · [简体中文](CONTRIBUTING.zh-CN.md)

Contributions include new plugin listings, release updates, metadata corrections, distribution tooling and documentation. Plugin implementation changes belong in the plugin's source repository.

## Prepare a submission

Use [the issue form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) to request review, or copy [templates/plugin-entry.json](templates/plugin-entry.json) into the `plugins` array of the appropriate host catalog. Replace every example value; the template's zero key, hashes and commit are placeholders, not usable credentials or release evidence.

A submission must identify the repository, license, maintainers and publisher. For each release, provide the `vX.Y.Z` version, full source commit, host/API requirements, capabilities, UI surfaces and each platform artifact's immutable URL, SHA-256 and byte size. Include independently verifiable publisher/key ownership evidence and actual host/platform test results in the PR.

Public source alone may be listed with `releases: []` and `publisher.public_key: null`; such a listing cannot be installed. Do not invent package URLs, digests, tests or a signing key to fill missing information.

## Work on the registry

Branch from `main` and keep the PR focused on one plugin or tooling change. Append releases to the existing plugin entry and retain prior releases. Do not duplicate plugin IDs or reassign an existing ID to another publisher. A key rotation needs a separate, reviewed transition plan.

```sh
python3 -m unittest discover -s tests
python3 scripts/validate.py
git diff --check
```

CI checks structure, identities, version syntax, host separation and artifact metadata. It compares changes with the PR base or previous main commit to reject removed releases, rewritten artifact records and silent publisher/key changes. It does not establish publisher identity, fetch binaries, verify remote signatures or test host execution. Maintainers perform those reviews before accepting installable releases.

## Review requirements

Maintainers check publisher and key ownership, source/tag correspondence, license, package signature and digest, compatibility declarations and the requested capabilities. New permissions, migrations and uninstall behavior need explicit review. Record cross-compilation separately from execution tests and live provider tests.

A submission does not grant host permissions or imply that a third-party publisher is endorsed by ZeroDeNet. Report vulnerabilities through [SECURITY.md](SECURITY.md).

## Documentation and merge

Use English as the default and update matching `.zh-CN.md` guides in the same PR. Keep workstation details, credentials, compiled packages and development keys out of Git. Describe the effect and validation in the PR. Merge reviewed changes by squash or rebase to retain a linear `main` history.
