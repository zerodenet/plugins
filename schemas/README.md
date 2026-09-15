# Versioned schemas

These JSON Schema documents are reviewable interchange contracts. The Python validators remain the executable strict boundary because they also enforce cross-document identity, host capability namespaces, immutable release URLs, transition rules, and duplicate constraints that JSON Schema alone does not express clearly.

- `product-registry.schema.json`: hand-maintained registry schema v3.
- `release-manifest.schema.json`: publisher-owned release manifest schema v1.
- `marketplace-snapshot.schema.json`: derived build snapshot schema v1.
