# Contributing

**English** · [简体中文](CONTRIBUTING.zh-CN.md)

## Registration and updates

Use the [registration form](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml) or [record-update form](https://github.com/zerodenet/plugins/issues/new?template=update-plugin.yml). Submit a public immutable `marketplace-entry.json` containing the exact complete listing. Stable, RC and Dev releases are supported. Automation checks source ownership, structure, identities, tag/source and asset size/digest, then atomically commits the verbatim registry and generated host projections. No maintainer approval or capability review is required.

The submitter must own the source repository, have automatically verifiable write permission, or present exact-request consent committed by the source repository. Updating a product uses its current source control; a repository transfer also requires control of the old source. Product and existing host/package IDs remain stable. Invalid or unavailable metadata receives `status:needs-info`; success receives `status:registered` and closes the Issue. Source-control checks prevent another publisher from replacing an existing identity.


When collaborator permissions cannot be read, use a source-controlled authorization binding the exact marketplace Issue, numeric author ID and body hash. See [publisher source control](docs/source-control.md). This also permits explicitly delegated submissions without granting repository access.

## Releases and permissions

Publish versions, artifacts, compatibility declarations and release notes in the plugin repository. New permissions or UI declarations require no market record update or approval. The market checks their structure, preserves each release's declaration, and leaves support, user confirmation and authorization to the host. Collection does not certify safety.

Implementation contributions use normal repository changes. Do not execute packages, track secrets, or rewrite publisher copy. Keep English and Chinese references aligned.

## Validation

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check
