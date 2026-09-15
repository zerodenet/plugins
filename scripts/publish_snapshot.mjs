import { copyFile, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { buildStaticPage } from './static_api.mjs';

await mkdir(new URL('../dist/', import.meta.url), { recursive: true });
const snapshotSource = new URL('../.generated/marketplace-snapshot.json', import.meta.url);
const snapshot = JSON.parse(await readFile(snapshotSource, 'utf8'));
await copyFile(snapshotSource, new URL('../dist/marketplace-snapshot.json', import.meta.url));
await mkdir(new URL('../dist/api/plugins/', import.meta.url), { recursive: true });
await copyFile(snapshotSource, new URL('../dist/api/plugins.json', import.meta.url));
for (const host of ['zboard', 'znet-sink']) {
  await mkdir(new URL(`../dist/api/plugins/${host}/`, import.meta.url), { recursive: true });
  for (const channel of ['stable', 'rc', 'dev']) {
    const page = buildStaticPage(snapshot, host, channel);
    await writeFile(
      new URL(`../dist/api/plugins/${host}/${channel}.json`, import.meta.url),
      `${JSON.stringify(page, null, 2)}\n`,
    );
  }
}
await mkdir(new URL('../dist/schemas/', import.meta.url), { recursive: true });
for (const name of await readdir(new URL('../schemas/', import.meta.url))) {
  if (name.endsWith('.schema.json')) {
    await copyFile(new URL(`../schemas/${name}`, import.meta.url), new URL(`../dist/schemas/${name}`, import.meta.url));
  }
}
