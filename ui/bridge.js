// Opaque-origin iframe: authenticate host messages by source window AND token.
(() => {
  const token = new URLSearchParams(location.hash.slice(1)).get('bridge_token');
  const pending = new Map();
  let next = 0;
  let closed = false;
  const receive = (event) => {
    const m = event.data;
    if (event.source !== parent || !m || m.source !== 'zboard-plugin-host' || m.bridge_token !== token) return;
    const request = pending.get(m.request_id);
    if (!request) return;
    pending.delete(m.request_id);
    clearTimeout(request.timer);
    if (m.ok === true) request.resolve(m.result);
    else request.reject(new Error('宿主拒绝请求或操作失败，请查看插件管理中的操作记录。'));
  };
  addEventListener('message', receive);
  window.oauthBridge = {
    request(type, payload = {}) {
      if (closed || !token || parent === window) return Promise.reject(new Error('请从 ZBoard 插件管理打开此页面。'));
      if (pending.size >= 4) return Promise.reject(new Error('请求过多，请等待当前操作完成。'));
      return new Promise((resolve, reject) => {
        const request_id = `oauth_${++next}`;
        const timer = setTimeout(() => {
          pending.delete(request_id);
          reject(new Error('宿主响应超时。若刚执行保存，请先刷新状态再重试。'));
        }, 25000);
        pending.set(request_id, { resolve, reject, timer });
        parent.postMessage({ ...payload, source: 'zboard-plugin-ui', bridge_token: token, request_id, type }, '*');
      });
    },
    resize(height) {
      if (!closed && token) parent.postMessage({ source: 'zboard-plugin-ui', bridge_token: token, type: 'ui.resize', height }, '*');
    },
  };
  addEventListener('pagehide', () => {
    closed = true;
    removeEventListener('message', receive);
    for (const request of pending.values()) { clearTimeout(request.timer); request.reject(new Error('插件页面已关闭。')); }
    pending.clear();
  }, { once: true });
})();
