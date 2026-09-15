import type { APIRoute } from 'astro';
import { marketplace } from '../../lib/marketplace';

export const prerender = true;

export const GET: APIRoute = () => new Response(`${JSON.stringify(marketplace, null, 2)}\n`, {
  headers: { 'content-type': 'application/json; charset=utf-8' },
});
