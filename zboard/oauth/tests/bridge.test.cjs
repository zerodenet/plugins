const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function fixture() {
  const listeners = new Map();
  const sent = [];
  const timers = new Map();
  const parent = { postMessage: (m, origin) => sent.push({ m, origin }) };
  const window = {};
  let next = 0;
  const context = { window, parent, location: { hash: '#bridge_token=secret-bridge' }, URLSearchParams, Map, Promise, Error,
    addEventListener: (name, fn) => listeners.set(name, fn), removeEventListener: (name) => listeners.delete(name),
    setTimeout: (fn) => { timers.set(++next, fn); return next; }, clearTimeout: (id) => timers.delete(id),
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../ui/bridge.js'), 'utf8'), context);
  return { api: window.oauthBridge, listeners, sent, timers, parent };
}

test('bridge ignores forged window, token, and request ID', async () => {
  const f = fixture();
  const response = f.api.request('config.load');
  const request = f.sent[0].m;
  const data = { source: 'zboard-plugin-host', bridge_token: 'secret-bridge', request_id: request.request_id, ok: true, result: { revision: 4, configured: true } };
  f.listeners.get('message')({ source: {}, data });
  f.listeners.get('message')({ source: f.parent, data: { ...data, bridge_token: 'wrong' } });
  f.listeners.get('message')({ source: f.parent, data: { ...data, request_id: 'unknown' } });
  assert.equal(f.timers.size, 1);
  f.listeners.get('message')({ source: f.parent, data });
  assert.deepEqual(await response, { revision: 4, configured: true });
  assert.equal(f.timers.size, 0);
});

test('request metadata cannot be replaced by config payload', async () => {
  const f = fixture();
  const response = f.api.request('config.save', { type: 'attack', source: 'attack', bridge_token: 'attack', revision: 1, config: {} });
  const request = f.sent[0].m;
  assert.equal(request.type, 'config.save');
  assert.equal(request.bridge_token, 'secret-bridge');
  f.listeners.get('message')({ source: f.parent, data: { source: 'zboard-plugin-host', bridge_token: 'secret-bridge', request_id: request.request_id, ok: false } });
  await assert.rejects(response, /宿主拒绝/);
});

test('timeout and page close release all pending requests', async () => {
  const f = fixture();
  const first = f.api.request('config.load');
  const timeout = [...f.timers.values()][0];
  timeout();
  await assert.rejects(first, /超时/);
  const second = f.api.request('config.test');
  f.listeners.get('pagehide')();
  await assert.rejects(second, /已关闭/);
  await assert.rejects(f.api.request('config.load'), /插件管理/);
  assert.equal(f.listeners.has('message'), false);
});
