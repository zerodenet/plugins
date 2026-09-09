# OAuth configuration reference

**English** · [简体中文](configuration.zh-CN.md)

For installation and the first provider, see [OAuth for ZBoard](../README.md). This page covers provider settings and the account behavior of the supported ZBoard integration.

## Configuration structure

The top-level `providers` array holds up to 16 providers. Each new provider has a stable `id`, using 1–32 lowercase letters, digits, underscores, or hyphens. IDs must be unique. The settings UI keeps the ID fixed after creation; change `name` to relabel a login button.

A complete example with placeholder credentials:

```json
{
  "providers": [
    {
      "id": "github",
      "preset": "github",
      "client_id": "YOUR_GITHUB_CLIENT_ID",
      "client_secret": "YOUR_GITHUB_CLIENT_SECRET"
    },
    {
      "id": "google",
      "preset": "google",
      "client_id": "YOUR_GOOGLE_CLIENT_ID",
      "client_secret": "YOUR_GOOGLE_CLIENT_SECRET"
    },
    {
      "id": "company",
      "name": "Company account",
      "preset": "custom",
      "protocol": "oauth2",
      "issuer": "https://identity.example.com",
      "authorization_endpoint": "https://identity.example.com/oauth/authorize",
      "token_endpoint": "https://identity.example.com/oauth/token",
      "userinfo_endpoint": "https://identity.example.com/api/me",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "token_auth_method": "basic",
      "scopes": ["profile", "email"],
      "subject_field": "data.id",
      "email_field": "data.email",
      "email_verified_field": "data.email_verified"
    }
  ]
}
```

## Provider fields

| Field | Description |
| --- | --- |
| `id` | Stable provider identity within the plugin; part of the account-binding namespace. |
| `name` | Display name used for the sign-in option. |
| `preset` | `github`, `google`, or `custom`. Presets supply protocol defaults. |
| `disabled` | Disable one provider while retaining its configuration. |
| `protocol` | `oauth2` or `oidc`; custom OIDC uses discovery. |
| `issuer` | Stable identity authority; for OIDC it must match the issuer exactly. |
| `client_id` / `client_secret` | Credentials registered with the provider. |
| `scopes` | Requested scopes; OIDC requires `openid`. |
| `token_auth_method` | `basic`, `post`, or `none`; a public client using `none` must not have a secret. |
| `authorization_endpoint` | Custom OAuth2 authorization endpoint. |
| `token_endpoint` | Custom OAuth2 token endpoint. |
| `userinfo_endpoint` | Custom OAuth2 JSON profile endpoint, requested with Bearer authentication and GET. |
| `subject_field` | Required OAuth2 profile path for a stable subject, such as `id` or `data.id`. |
| `email_field` | Optional profile path for the email address. |
| `email_verified_field` | Optional profile path indicating verification; only JSON boolean `true` is accepted. |

The configuration is limited to 64 KiB. Unknown fields and duplicate provider IDs are rejected. OAuth2 uses the authorization code flow with S256 PKCE. Subject values must be stable strings or integers in the int64 range; mutable usernames and email addresses are unsuitable identifiers.

For a custom OIDC provider, set `protocol` to `oidc`, supply the issuer and client credentials, and include `openid` in the scopes. Endpoints come from discovery; OAuth2 profile mappings are not required.

## Preset behavior

GitHub uses the stable numeric ID from `/user` and a primary, verified address from `/user/emails`. A public profile email is not sufficient proof of email ownership.

Google uses OIDC. Identity validation checks signature, issuer, audience, expiry, nonce, `azp`, and `at_hash` when present.

## Editing secrets

The configuration page displays public settings and whether a secret exists, without returning the secret itself. In that UI, leave a stored secret blank to retain it, enter a value to replace it, or select the clear option to remove it. Changing the client, protocol, issuer, or token endpoint requires re-entering the secret.

These behaviors apply to the plugin configuration editor. An advanced JSON update replaces the submitted configuration; preserve the intended credentials when using that path. Configuration writes use a revision check. After a conflict, refresh and reapply changes.

## Account behavior

| Situation | ZBoard behavior |
| --- | --- |
| Identity already linked | Sign in after core account checks. |
| New identity, registration enabled, verified email supplied | Register an ordinary user. |
| New identity without a verified email | Complete email verification in ZBoard; SMTP is required regardless of the password-registration verification setting. |
| New identity, registration disabled | Reject registration and login for that unlinked identity. |
| Email matches an existing account | Require explicit linking from the existing account. |

Linking and unlinking require the account's current local password. A newly registered external account initially has no local password; within five minutes of external authentication, its owner may set the initial password in account security. This flow cannot overwrite an existing password.

Each external identity belongs to one ZBoard account; an account can link multiple providers. Disabling or uninstalling the plugin, or changing its configuration, invalidates unfinished login and registration flows. Committed identity bindings and existing core sessions remain intact.

The legacy `0.1.0` single-provider configuration remains readable. Its empty provider ID is preserved for existing bindings; new providers use explicit IDs. Treat a provider ID change as an identity namespace change.

## Network requirements

Provider endpoints must use public HTTPS on port 443. Requests reject redirects, environment proxies, private destinations, and endpoint query parameters. DNS results are checked and connections use a validated address. Responses are limited to 1 MiB with an eight-second request timeout; discovery metadata is cached for five minutes and invalidated after configuration changes.

Private-network identity providers, custom scripts, arbitrary request headers, and non-authorization-code flows are outside the current integration. The host owns single-use state, PKCE, browser binding, and completion tickets. Restarting the host requires a new authorization flow; multi-instance deployments must route authentication traffic to the active plugin host.

## Troubleshooting

| Problem | What to verify |
| --- | --- |
| Redirect URI rejected | Provider registration exactly matches the site's callback URI. |
| Discovery or profile request fails | Public HTTPS reachability and the network requirements above. |
| Provider does not appear | Both the plugin and the provider are enabled and configuration is saved. |
| New user cannot register | Host registration setting, verified-email status, and SMTP configuration. |
| Existing account cannot link | Sign in to that account and confirm its local password. |
| Configuration test passes but login fails | Test a full authorization flow with the real client credentials and registered redirect URI. |

Host implementation details are maintained in [ZBoard's identity contract](https://github.com/zerodenet/zboard/blob/feature/plugin/docs/plugin-identity.md). Use the host and plugin versions when reporting behavior that differs from this reference.
