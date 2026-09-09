# Security policy

**English** · [简体中文](SECURITY.zh-CN.md)

## Reporting a vulnerability

Report vulnerabilities privately before disclosing details that could affect deployed systems. If GitHub's private vulnerability reporting is available in this repository's Security tab, use that channel. Otherwise, contact a maintainer privately or open an issue requesting a private contact without including exploit details.

Include affected plugin and host versions, operating system, impact, and a minimal reproduction. Remove access tokens, client secrets, signing keys, personal data, and production configuration from attachments.

Maintainers will assess affected versions and coordinate a fix and disclosure. This project does not publish a fixed response-time commitment or a long-term support schedule.

## Scope

Reports may concern plugin source, configuration handling, dependencies, package creation, or the distribution design maintained here. Vulnerabilities in a host's core services should also be reported through that host's security process.

## Operating plugins

Package signatures establish origin and integrity. Administrators select trusted publishers and review requested capabilities. ZBoard's current native plugin processes run as trusted code; process separation does not provide an operating-system sandbox.

See [Architecture](docs/governance.md) for the trust model and [Publishing](docs/publishing.md) for signing-key handling.
