# Unified marketplace architecture

**English** · [简体中文](marketplace-design.zh-CN.md)

Users discover one plugin product. Products explicitly declare one or more host targets; the market never guesses a host from IP, Referer, or User-Agent.

| Layer | Owner | Durable content |
| --- | --- | --- |
| Product registration | Central marketplace | Product ID, verbatim publisher metadata, repository, trusted publisher, release source, host/package identities, reviewed ceilings, withdrawal |
| Release manifest | Publisher repository | Version/channel, source commit, target packages, host/platform compatibility, size, digest, signature, release notes |
| Build snapshot | Marketplace build | Publisher release history for the site, validated releases for hosts, freshness, snapshot version |
| Installation lifecycle | Each host | Final download, signature/policy verification, authorization, install, upgrade, rollback, disable, uninstall, audit |

The Astro site and static API come from one build. GitHub Actions performs bounded publisher aggregation, and GitHub Pages atomically publishes pre-rendered discovery and detail pages, the complete snapshot, host/channel JSON projections, and schemas. ZBoard and ZNet Sink filter host version, OS, and architecture locally. The first release needs no database, Worker, or visitor GitHub token; a dynamic service is reserved for future authenticated writes, personalization, or genuinely server-side search.

The site follows Minted Directory Astro's static JSON directory approach. Ever Works informed product cards, detail hierarchy, and publisher/target presentation; the visual system uses conventional white, light-gray, and charcoal foundations, a subdued blue for primary actions, and restrained green and amber for stable and prerelease states. It follows the system light or dark preference. Detail pages expose the developer, documentation, security, support, and release links while distinguishing publisher activity from validated installable releases. The first release only reserves the ratings/reviews position and shows no fabricated score; accounts, review writes, favorites, payments, and an administration backend remain outside scope.

Publisher-supplied names, descriptions, categories, and links are always rendered verbatim. `surfaces` and `capabilities` are host-protocol keys rather than product copy; detail pages may display descriptions from a host-maintained standard dictionary, but must retain each raw key and must not infer unknown meanings. The dictionary must never contain product IDs or product-specific overrides.

Legacy schema-v2 host catalogs are deterministic projections during migration. They are never edited as a second source. They can be removed only after supported ZBoard and ZNet Sink versions use the unified static API and the documented compatibility window ends.
