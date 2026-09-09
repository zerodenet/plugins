# Registry format

**English** · [简体中文](registry-format.zh-CN.md)

The source registry uses schema version `1`. It is a repository editing contract, distinct from ZBoard's signed catalog v1 and the proposed shared distribution v2. The executable validator is [scripts/validate.py](../scripts/validate.py).

## Catalogs

`catalogs/zboard.json` and `catalogs/znet-sink.json` contain `schema_version`, `host` and `plugins`. The host value must match the filename. A plugin ID occurs once per host catalog. The same project may publish separate artifacts for each host; one host's capabilities never authorize another host.

## Plugin entry

| Field | Meaning |
| --- | --- |
| `id`, `name`, `description` | Stable package identity and discovery text |
| `repository` | Public GitHub source repository |
| `license`, `maintainers` | License identifier and responsible maintainers |
| `publisher.id` | Stable package-signing key identifier |
| `publisher.public_key` | Base64 Ed25519 public key; `null` only before any release |
| `source.version`, `source.commit`, `source.manifest` | Current source version, full Git SHA and relative manifest path |
| `releases` | Immutable release records; empty means source-only |

The source version is a `v`-prefixed release identifier. ZBoard package manifests and runtime handshakes retain the unprefixed semantic version required by its protocol. For example, market release `v0.0.1` corresponds to package version `0.0.1`.

## Release and artifact

Each release has `version`, `source_commit`, `requires`, `surfaces`, `capabilities` and `artifacts`. `requires` includes the catalog's host key and host/API compatibility. ZBoard releases also declare positive integer `plugin_protocol` and `ui_bridge` versions. Optional ZBoard recommendations and tested-version declarations should be copied from the signed manifest.

Each artifact has `platform`, `url`, `sha256` and `size` in bytes. Supported target names are `linux-amd64`, `linux-arm64`, `darwin-amd64`, `darwin-arm64`, `windows-amd64` and `any`. `any` means a genuinely platform-independent package and cannot be combined with target-specific artifacts. Artifacts must use immutable HTTPS URLs without embedded credentials, query strings or fragments. ZBoard packages use `.zbplugin`; the current registry limit is 32 MiB per compressed artifact.

## Updating entries

Add a new release without replacing the bytes or digest of an existing version. New permissions or a changed publisher key require explicit review. Key rotation and signed withdrawal records are not part of source schema v1; do not silently replace a public key used by older releases. For an urgent withdrawal, open a security report and coordinate catalog exclusion with host operators.

Source CI checks structure and internal consistency. A maintainer must independently verify source references, package bytes, signatures and publisher ownership. The public key in a listing is evidence for review, not a host trust anchor.
