# Verifying publisher source control

**English** · [简体中文](source-control.zh-CN.md)

Registration and record updates require source-controlled consent. A personal repository owner can submit directly. A collaborator can use GitHub's write/maintain/admin permission check when the automation credential can read it. The registry's repository-scoped `GITHUB_TOKEN` cannot generally inspect another repository's collaborator permissions; HTTP 403 does not establish that the submitter lacks write access.

For organization repositories, delegated submitters, or unavailable collaborator permission APIs, a source maintainer can publish a public authorization at `.github/marketplace-authorizations.json` on the source repository's **default branch**. The marketplace fetches the current default-branch commit and reads the file at that immutable SHA using public GitHub API requests. It never reads an Issue-supplied branch, file URL or executable.

## Authorize an exact request

1. Open the registration or update Issue with the immutable release manifest URL.
2. In the publisher repository, run the registry's helper below, then review the generated public JSON and commit it to the publisher's default branch. Use a checkout of the marketplace repository for the helper; it fetches only the public Issue and requires no token.

```sh
python3 /path/to/plugins/scripts/source_authorization.py \
  --marketplace zerodenet/plugins --issue 7
```

Example structure (replace the numeric IDs and digest with the helper's actual output):

```json
{
  "schema_version": 1,
  "authorizations": [
    {
      "marketplace": "zerodenet/plugins",
      "issue": 7,
      "actor_id": 123,
      "body_sha256": "<SHA-256 of the exact UTF-8 Issue body>"
    }
  ]
}
```

3. Edit or reopen the same Issue after the source commit is public. A registry push or manual reconciliation also retries open applications.

The authorization binds the marketplace repository, Issue number, GitHub numeric author ID and the exact Issue body. An approval cannot authorize another author, Issue, registry, release URL or edited request. Editing the body requires regenerating and committing the proof; comments and labels do not change the body. The helper preserves unrelated authorizations and replaces the previous proof for the same registry/Issue/author. A rename of the GitHub login does not transfer the numeric identity.

A source repository transfer still requires control of both the registered source and replacement source, each approving the same request. A missing or mismatched proof leaves the application at `status:needs-info`; it is never treated as approval. Files are limited to 16 KiB and 100 exact authorizations; symlinks, duplicate JSON fields and open-ended entries are rejected.

This public file only authorizes the specified marketplace record request. It grants no repository write access, package trust or host permissions, and contains no private signing key or token. Remove obsolete entries as part of ordinary source maintenance. Existing personal-owner and verifiable collaborator submissions remain supported.
