import type { APIRoute } from 'astro';
import { marketplace } from '../../../../lib/marketplace';
// The build publisher and this local-preview route share the same pure projection.
import { buildStaticPage } from '../../../../../scripts/static_api.mjs';

const hosts = ['zboard', 'znet-sink'];
const channels = ['stable', 'rc', 'dev'];

export const prerender = true;
export function getStaticPaths() {
  return hosts.flatMap((host) => channels.map((channel) => ({ params: { host, channel } })));
}

export const GET: APIRoute = ({ params }) => {
  const { host, channel } = params;
  if (!host || !channel) return new Response('Not found', { status: 404 });
  return new Response(`${JSON.stringify(buildStaticPage(marketplace, host, channel), null, 2)}\n`, {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
