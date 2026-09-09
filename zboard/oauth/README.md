# OAuth for ZBoard

**English** · [简体中文](README.zh-CN.md)

Let users sign in to ZBoard with GitHub, Google, or your organization's identity provider. The plugin connects external OAuth2 / OpenID Connect providers to ZBoard's account registration and linking flows.

**Plugin ID:** `zboard.oauth` · **Source version:** `0.2.0`

## Providers

| Provider | Setup | Identity source |
| --- | --- | --- |
| GitHub | Preset; supply Client ID and Client Secret | Stable GitHub user ID and verified primary email |
| Google | Preset; supply Client ID and Client Secret | OpenID Connect identity claims |
| Custom OAuth2 | Configure endpoints, scopes, and profile field mapping | Stable subject from a JSON user profile |
| Custom OpenID Connect | Configure issuer, client credentials, and scopes | Discovery metadata and validated identity claims |

Configure up to 16 providers, with separate display names and enabled states. The configuration page includes shortcuts for GitHub and Google and an editor for custom providers.

## Requirements

Use a ZBoard build implementing the multi-provider identity API, public configuration projection, and external registration flow required by this plugin. The manifest currently declares `>=0.0.1 <0.1.0`, plugin protocol `1`, and UI bridge `1`; check API support as well as the host's displayed version.

A deployed site needs a public HTTPS base URL and a provider application registered with its callback URL. SMTP is required when a new user must verify an email address not supplied as verified by the provider.

For package availability, see the [repository README](../../README.md). Build targets include Linux, macOS, and Windows. macOS host launches have encountered Gatekeeper rejection; stable platform execution and production signing/notarization remain to be validated.

## Setup

1. Set the public base URL in ZBoard's site settings.
2. Register this redirect URI with each provider, replacing the example domain:

   ```text
   https://panel.example.com/api/v1/auth/oidc/callback
   ```

3. Follow the [installation guide](../../docs/usage.md) to trust the publisher and import the signed package.
4. Open the plugin configuration page and add GitHub, Google, or a custom provider. Enter the application's Client ID and Client Secret.
5. Save and test the configuration, then enable the plugin. Verify the complete flow with a test account.

Configuration testing checks settings and, for OIDC, discovery metadata. A successful check does not exercise authorization with the provider. For local development, ZBoard also accepts a loopback callback such as `http://127.0.0.1:18090/api/v1/auth/oidc/callback`.

## Accounts and registration

ZBoard decides whether an external identity may sign in, register, or link to an account. When registration is closed, an unlinked identity cannot create an account or sign in through this plugin. Existing linked identities remain subject to the host's account checks.

Matching email addresses do not automatically link accounts. Users sign in to their existing account and link a provider from account security settings. Provider removal closes that login route while preserving core accounts and established bindings.

See the [configuration reference](docs/configuration.md) for custom provider fields, secret handling, account-linking behavior, and troubleshooting.

## Development

From the repository root:

```sh
sh scripts/check.sh
```

The plugin includes protocol fixtures, configuration tests, a real gRPC process test, and UI/bridge tests. [Development](../../docs/development.md) covers the toolchain, SDK workspace, and local packaging. [Publishing](../../docs/publishing.md) describes release signing and platform validation.

## Support

Open an [issue](https://github.com/zerodenet/plugins/issues) with the plugin version, host build, platform, and sanitized reproduction steps. Report vulnerabilities using the [security policy](../../SECURITY.md).

Licensed under [MPL-2.0](../../LICENSE).
