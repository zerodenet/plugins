# Publishing and marketplace admission

**English** · [简体中文](publishing.zh-CN.md)

## First admission

Publish one stable signed release from the independent plugin repository. Include immutable platform packages, checksums, compatibility declarations, source commit, and marketplace-entry.json. Apply to the marketplace with that metadata URL and evidence for publisher ownership, security maintenance, host behavior, and the requested capability ceiling.

The admission review records stable discovery and trust metadata only. It does not import the onboarding version or any later release into a central release ledger.

## Publisher-owned lifecycle

After admission, the publisher may release Stable, RC, and Dev versions without another marketplace issue. Each accepted release:

- uses the admitted plugin ID, repository, publisher ID, and production signing key;
- follows the host package and metadata contract;
- stays within the admitted UI surface and capability ceilings;
- publishes immutable packages and one marketplace-entry.json asset;
- marks RC and Dev as prereleases and Stable as a normal release.

Hosts discover these versions directly, show channel and exact-version choices, inspect compatibility, verify package signature and digest, and perform lifecycle operations. A release outside the admitted boundary is rejected and requires a marketplace update before it can be installed online.

Development artifacts signed with disposable CI keys are for isolated offline testing, not marketplace installation. Offline import also remains available for private, local, or non-open-source plugins.

## Directory updates

Return to the marketplace only for repository relocation, publisher/key rotation, release-source contract changes, support for another host, capability or surface expansion, or withdrawal. Basic information remains in the marketplace registration. These are admission changes, not releases.
