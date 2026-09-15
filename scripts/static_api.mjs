const HOSTS = new Set(['zboard', 'znet-sink']);
const CHANNELS = new Set(['stable', 'rc', 'dev']);

export function buildStaticPage(snapshot, host, channel) {
  if (!HOSTS.has(host)) throw new Error(`unsupported static API host: ${host}`);
  if (!CHANNELS.has(channel)) throw new Error(`unsupported static API channel: ${channel}`);
  const items = [];
  for (const product of snapshot.products) {
    const target = product.targets.find((candidate) => candidate.host === host);
    if (!target) continue;
    const releases = target.releases.filter((release) =>
      release.channel === channel && release.artifacts.length > 0);
    if (!releases.length) continue;
    items.push({
      ...product,
      targets: [{ ...target, releases }],
      installable: true,
      compatibility: 'host',
      latest_published_at: releases.map((release) => release.published_at).sort().at(-1) || null,
    });
  }
  items.sort((left, right) => left.name.localeCompare(right.name));
  return {
    snapshot_version: snapshot.snapshot_version,
    generated_at: snapshot.generated_at,
    page: 1,
    page_size: 1000,
    total: items.length,
    items,
  };
}
