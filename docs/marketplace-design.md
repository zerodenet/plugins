# Shared marketplace proposal

**English** · [简体中文](marketplace-design.zh-CN.md)

**Status: Draft.** This proposal describes a shared distribution layer for ZBoard, ZNet Sink, and future hosts. ZBoard currently implements its own v1 catalog and `.zbplugin` format. The proposed v2 format has not been implemented.

## Motivation

Users should be able to discover ZeroDeNet plugins in one place. Publishers need a consistent way to describe releases, target hosts, compatibility, and artifacts. Hosts need enough signed information to select and verify an appropriate package while retaining control of installation and execution.

A shared catalog can serve a public website and product-specific marketplace views. A host normally presents compatible plugins; a general website can show all supported hosts and explain compatibility requirements.

## Scope

The marketplace covers plugin discovery, publisher metadata, release indexing, signed catalogs, and artifact distribution. Plugin runtimes, business APIs, private data, and lifecycle transactions belong to each host as described in [Architecture](governance.md).

Official source lives on its host branch (`zboard` or `znet-sink`), under `<host>/<plugin>/`. Shared proposals and platform documentation live on `main`. External publishers can keep independent repositories and associate a release with its source URL and commit. Marketplace participation does not require source relocation.

## Release model

The proposed catalog groups releases under a stable plugin ID, with separate installable artifacts for each target host.

| Metadata | Purpose |
| --- | --- |
| Plugin ID, publisher, version | Stable identity and release ownership |
| Host ID and host version range | Target application and compatible versions |
| Package format and API versions | Installation and runtime contracts; UI bridge version where applicable |
| OS and architecture | Supported runtime targets, or an explicit platform-independent designation |
| Capabilities and contributions | Required host operations and contributed interfaces |
| Artifact URL, byte length, SHA-256 | Immutable download identity and integrity |
| Signature and key identifier | Artifact provenance |

One artifact targets one host. A host artifact may contain multiple platform binaries and UI surfaces. Releases for different hosts may evolve independently, even when they belong to the same plugin listing.

The signed package manifest or envelope must bind the target host and compatibility requirements. Installers compare package facts with the catalog and enforce the same checks for offline imports. The exact envelope and v2 JSON schema remain open design work.

## Trust model

Catalog signing and package publishing are distinct roles. A host verifies both against its configured trust. Publisher keys delivered through an untrusted catalog cannot bootstrap that trust.

The catalog can describe withdrawals and key rotations. Host policy defines how those records affect installation and existing instances, including behavior while offline. A marketplace response cannot grant capabilities or delete host business data.

## Compatibility with ZBoard v1

ZBoard's current parser accepts only schema v1 fields, recognizes `public`, `account`, and `admin` surfaces, and expects `requires.zboard` in packages. Adding v2 fields or client entries to that catalog would break validation.

The publishing layer should therefore provide a shared v2 catalog and independently signed compatibility catalogs. An example relative layout is `catalogs/zboard/v1/catalog.json`; this is a proposed path, not a published endpoint. The compatibility document contains only ZBoard v1 entries and `.zbplugin` artifacts.

Existing ZBoard installations can consume that compatibility catalog without adopting the v2 parser. Download locations must satisfy the host's current direct-HTTPS requirements. Client hosts use their own catalog contract until they implement v2.

## Open decisions

- Exact JSON schema, signed envelope, and host identifier registry.
- Publisher onboarding, trusted key rotation, and withdrawal policy.
- Artifact hosting, availability monitoring, and catalog renewal.
- Version selection across host API versions and platforms.
- Client runtime capabilities and isolation requirements, owned by the client project.

## Adoption and validation

First settle the distribution contract, then publish and verify ZBoard-compatible artifacts and catalogs. Add v2 consumption to ZBoard and integrate ZNet Sink after its plugin lifecycle and APIs are implemented.

Acceptance should cover cross-host rejection in online and offline paths, catalog/package identity mismatches, signature failures, multi-host and platform selection, v1 compatibility, and host upgrade failure recovery. Each implementation must identify which parts of this proposal it supports.
