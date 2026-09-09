# Client integration scope

**English** · [简体中文](client-integration.zh-CN.md)

**Status: Design scope.** This document identifies the host contracts required before a ZNet Sink plugin can be built and distributed. It does not define an implemented API or package format.

## Host responsibilities

ZNet Sink owns local configuration, system permission decisions, connection lifecycle, credentials, and requests to the Zero kernel. A plugin requests a defined client operation through a versioned capability. The client validates the caller, resource scope, instance state, and policy before executing it.

The runtime must define isolation appropriate to its execution model, including process or webview access, filesystem and network access, resource limits, and behavior when the client stops. ZBoard's service runtime and administrative capabilities do not grant client permissions.

## Required contracts

| Area | Decision needed |
| --- | --- |
| Identity and package | Client host identifier, manifest schema, API compatibility, signature, and platform selection |
| Contributions | Supported UI locations and versioned client operations |
| Configuration and data | Secret handling, private storage, migrations, backup, and removal policy |
| Lifecycle | Installation, enabling, upgrading, failure recovery, disabling, and uninstalling |
| Execution | Isolation, system permissions, resource ownership, and termination |
| Distribution | Catalog compatibility, artifact hosting, update selection, and offline import |

Define these contracts in the client project and validate them with the host before implementing a plugin here. Shared discovery follows the [marketplace proposal](marketplace-design.md), with client-specific packages and admission checks.

## Implementation acceptance

A client plugin contribution must identify the host API it consumes, provide build and test commands, and demonstrate lifecycle and failure behavior on its supported platforms. Package signatures, host compatibility, and capabilities must be checked for both online installation and offline import.

Source will be maintained under `znet-sink/<plugin>/` on this branch. Implementation changes and releases target `znet-sink`; shared platform policy changes target `main`.
