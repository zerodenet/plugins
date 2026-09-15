import assert from 'node:assert/strict';
import test from 'node:test';
import { artifactSizeLabel } from '../src/lib/presentation.mjs';
import { buildStaticPage } from './static_api.mjs';

const release = (channel) => ({
  version: channel === 'stable' ? '1.0.0' : '1.1.0-dev.1',
  channel,
  published_at: '2026-09-15T00:00:00Z',
  host_version: { min: '0.0.1', max_exclusive: '0.1.0' },
  artifacts: [{ os: 'linux', arch: 'amd64', url: 'https://example.invalid/package', size: 1, sha256: 'a'.repeat(64) }],
});

const snapshot = {
  snapshot_version: `sha256:${'b'.repeat(64)}`,
  generated_at: '2026-09-15T00:00:00Z',
  products: [{
    id: 'org.example.bridge',
    name: 'Bridge',
    release_feed: [release('dev')],
    targets: [
      { host: 'zboard', releases: [release('stable'), release('dev')] },
      { host: 'znet-sink', releases: [] },
    ],
  }],
};

test('static API fixes host and channel but retains client compatibility metadata', () => {
  const page = buildStaticPage(snapshot, 'zboard', 'stable');
  assert.equal(page.page, 1);
  assert.equal(page.page_size, 1000);
  assert.equal(page.total, 1);
  assert.equal(page.items[0].targets.length, 1);
  assert.equal(page.items[0].targets[0].host, 'zboard');
  assert.equal(page.items[0].targets[0].releases.length, 1);
  assert.deepEqual(page.items[0].targets[0].releases[0].host_version, {
    min: '0.0.1',
    max_exclusive: '0.1.0',
  });
});

test('static API omits hosts and channels without validated artifacts', () => {
  assert.equal(buildStaticPage(snapshot, 'znet-sink', 'stable').total, 0);
  assert.equal(buildStaticPage(snapshot, 'zboard', 'rc').total, 0);
});

test('a single-host product is published only for its declared host', () => {
  const zboardOnly = structuredClone(snapshot);
  zboardOnly.products[0].targets = [zboardOnly.products[0].targets[0]];
  assert.equal(buildStaticPage(zboardOnly, 'zboard', 'stable').total, 1);
  assert.equal(buildStaticPage(zboardOnly, 'znet-sink', 'stable').total, 0);
});

test('small package sizes are readable instead of rounding to zero MiB', () => {
  assert.equal(artifactSizeLabel(1324), '1.29 KiB');
  assert.equal(artifactSizeLabel(2532), '2.47 KiB');
  assert.equal(artifactSizeLabel(2 * 1024 * 1024), '2 MiB');
});
