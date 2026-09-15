import { readdir, readFile, stat } from 'node:fs/promises';

const dist = new URL('../dist/', import.meta.url);
const configuredBase = process.env.MARKETPLACE_BASE_PATH || '/';
const base = `/${configuredBase.replace(/^\/+|\/+$/g, '')}${configuredBase === '/' ? '' : '/'}`;
const required = [
  'marketplace-snapshot.json',
  'api/plugins.json',
  'api/plugins/zboard/stable.json',
  'api/plugins/zboard/rc.json',
  'api/plugins/zboard/dev.json',
  'api/plugins/znet-sink/stable.json',
  'api/plugins/znet-sink/rc.json',
  'api/plugins/znet-sink/dev.json',
  'schemas/marketplace-snapshot.schema.json',
  'schemas/product-registry.schema.json',
  'schemas/release-manifest.schema.json',
];

for (const path of required) {
  const info = await stat(new URL(path, dist));
  if (!info.isFile() || info.size === 0) throw new Error(`missing Pages artifact: ${path}`);
}

const fullSnapshot = JSON.parse(await readFile(new URL('api/plugins.json', dist), 'utf8'));
for (const host of ['zboard', 'znet-sink']) {
  for (const channel of ['stable', 'rc', 'dev']) {
    const path = `api/plugins/${host}/${channel}.json`;
    const page = JSON.parse(await readFile(new URL(path, dist), 'utf8'));
    if (page.snapshot_version !== fullSnapshot.snapshot_version) throw new Error(`${path}: snapshot version mismatch`);
    if (page.page !== 1 || page.page_size !== 1000 || page.total !== page.items.length) {
      throw new Error(`${path}: invalid static page envelope`);
    }
    for (const product of page.items) {
      if (product.targets.length !== 1 || product.targets[0].host !== host) {
        throw new Error(`${path}: contains a target for another host`);
      }
      if (!product.targets[0].releases.length || product.targets[0].releases.some((release) => release.channel !== channel)) {
        throw new Error(`${path}: contains a release for another channel`);
      }
    }
  }
}

async function htmlFiles(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const url = new URL(entry.name + (entry.isDirectory() ? '/' : ''), directory);
    if (entry.isDirectory()) files.push(...await htmlFiles(url));
    else if (entry.name.endsWith('.html')) files.push(url);
  }
  return files;
}

if (base !== '/') {
  for (const file of await htmlFiles(dist)) {
    const html = await readFile(file, 'utf8');
    for (const [, attribute, path] of html.matchAll(/\b(href|src)="(\/[^"#?]*)/g)) {
      if (path !== base.slice(0, -1) && !path.startsWith(base)) {
        throw new Error(`${file.pathname}: ${attribute} escapes Pages base path ${base}: ${path}`);
      }
    }
  }
}

console.log(`Pages build verified for base path ${base}`);
