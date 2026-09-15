import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: process.env.MARKETPLACE_SITE_ORIGIN || 'https://plugins.zerodenet.org',
  base: process.env.MARKETPLACE_BASE_PATH || '/',
  build: { format: 'directory' },
  vite: { build: { sourcemap: false } },
});
