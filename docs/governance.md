# Plugin architecture

**English** · [简体中文](governance.zh-CN.md)

This document defines the integration boundary for ZeroDeNet plugins. Project maintenance and review policies are described in [Project governance](../GOVERNANCE.md).

## Responsibilities

| Component | Owns |
| --- | --- |
| Marketplace | Discovery, publisher information, release metadata, and package distribution |
| Host plugin manager | Admission, runtime instances, configuration, private storage, and lifecycle operations |
| Host core services | Business records, authorization policy, and committed business transactions |
| Plugin | Integration logic and contributed UI through declared host APIs |

ZBoard owns accounts, credentials, orders, entitlements, traffic records, and node configuration publication. A client host owns its configuration, system permissions, connection lifecycle, and controlled kernel operations. These responsibilities remain with each host when it adopts the marketplace.

## Capability model

A manifest declares the operations a plugin needs. The host validates those capabilities against its supported API, the caller's identity, resource scope, active plugin instance, and core policy. A marketplace listing supplies metadata; admission occurs inside the host.

UI surfaces, runtime components, and capabilities describe different parts of a plugin. An `admin` page does not grant administrative business access. For OAuth, the core registration setting and account status still govern whether an external identity can create or access an account.

Plugins use versioned, dedicated interfaces. Database connections, arbitrary SQL, administrator tokens, node credentials, and unrestricted host commands are outside the plugin API.

## Lifecycle contract

| Operation | Host responsibility |
| --- | --- |
| Install | Validate signatures, contents, host/API/platform compatibility, and capabilities before admission. |
| Enable | Prepare the runtime, verify its identity, and apply committed configuration before exposing contributions. |
| Upgrade | Prepare candidate configuration, data migrations, and runtime; commit the switch or preserve the previous installation on failure. |
| Disable | Revoke the instance's UI and call sessions and stop its runtime. |
| Uninstall | Remove program assets according to the host's retention policy. |
| Clear data | Remove plugin-owned configuration and private data without deleting core business records. |

The host records migration order, versions, checksums, and results. Restoring an older program requires checking its compatibility with the stored data. Completed core transactions remain valid after a plugin stops.

ZBoard currently provides encrypted JSON private storage and declarative migrations managed by the host. Relational extension schemas would require a separate host contract; plugins cannot create or migrate core tables themselves.

## Trust and isolation

Catalog signatures establish index provenance; package signatures establish artifact provenance and integrity. Hosts maintain trust for both roles. A public key included in a catalog does not automatically become trusted.

ZBoard's current native service components run as trusted code in separate processes. The host does not provide an OS sandbox for arbitrary third-party binaries. Each future host must define its own runtime, system permission, and resource-isolation model.

## Extending the API

A new capability proposal should specify authorization, resource scope, idempotency, completion semantics, failure recovery, and behavior during lifecycle transitions. The host implements and tests the contract before plugins consume it.

Shared distribution does not introduce global permissions across products. Cross-product integrations use controlled business APIs; plugin storage and host sessions remain separate. The marketplace design does not add a plugin SPI to the Zero kernel.
