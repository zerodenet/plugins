import snapshot from '../../.generated/marketplace-snapshot.json';

export type Artifact = { os: string; arch: string; url: string; size: number; sha256: string };
export type Release = {
  version: string; channel: string; published_at: string; notes_url: string;
  host_version: { min: string; max_exclusive?: string }; surfaces: string[]; capabilities: string[]; artifacts: Artifact[];
};
export type PublisherRelease = {
  tag: string; name: string; channel: string; prerelease: boolean; published_at: string; url: string;
  body: string; body_truncated: boolean; assets_count: number; validated: boolean;
};
export type Target = { host: string; package_id: string; surfaces: string[]; capabilities: string[]; releases: Release[] };
export type Product = {
  id: string; name: string; description: string; categories: string[]; license: string; maintainers: string[];
  repository: string; publisher: { id: string; public_key: string }; homepage?: string; documentation?: string;
  security?: string; icon?: string; screenshots?: string[];
  release_source: { type: string; metadata_asset: string }; targets: Target[]; release_feed: PublisherRelease[];
};

export const marketplace = snapshot;
export const products = snapshot.products as Product[];
export const latest = (target: Target) => target.releases.find((release) => release.channel === 'stable') || target.releases[0];
