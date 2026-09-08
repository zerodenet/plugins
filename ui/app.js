(() => {
  const $ = (id) => document.getElementById(id);
  let revision = null;
  let configured = false;
  let busy = false;
  const notice = (text, error = false) => { $('notice').textContent = text; $('notice').className = error ? 'error' : 'success'; };
  const lock = (value) => {
    busy = value;
    $('fields').disabled = value || revision === null;
    $('reload').disabled = value;
    $('test').disabled = !configured;
  };
  const showState = (view) => {
    if (!view || !Number.isSafeInteger(view.revision) || view.revision < 0 || typeof view.configured !== 'boolean') throw new Error('宿主返回了无效的配置状态。');
    revision = view.revision;
    configured = view.configured;
    $('state').textContent = configured ? `已保存 · 配置版本 ${revision} · 字段不回显` : '尚未保存配置';
  };
  async function refresh() {
    if (busy) return;
    lock(true);
    try {
      const context = await oauthBridge.request('context.load');
      if (context.plugin_id !== 'zboard.oauth' || context.surface !== 'admin' || context.page_id !== 'settings') throw new Error('此页面需要管理员配置会话。');
      showState(await oauthBridge.request('config.load'));
      notice('每次保存都需要填写完整配置。检测使用宿主已保存的版本。');
    } catch (err) { revision = null; notice(err.message, true); }
    finally { lock(false); }
  }
  // The host sandbox intentionally excludes allow-forms; use an explicit
  // bridge action rather than native form submission.
  $('save').addEventListener('click', async (event) => {
    event.preventDefault();
    if (busy || revision === null || !$('settings').reportValidity()) return;
    const scopes = $('scopes').value.trim().split(/\s+/);
    if (!scopes.includes('openid')) { notice('Scopes 必须包含 openid。', true); return; }
    const config = { issuer: $('issuer').value.trim(), client_id: $('client-id').value.trim(), client_secret: $('client-secret').value, scopes };
    lock(true);
    notice('正在保存…');
    try {
      showState(await oauthBridge.request('config.save', { revision, config }));
      notice('配置已保存。检测通过后，可在账户安全中绑定并验证第三方登录。');
    } catch (err) {
      revision = null;
      notice(`${err.message} 请刷新配置版本后重新填写。`, true);
    } finally {
      $('client-secret').value = '';
      config.client_secret = '';
      $('replace').checked = false;
      lock(false);
    }
  });
  $('test').addEventListener('click', async () => {
    if (busy || !configured) return;
    lock(true);
    notice('正在检测宿主已保存配置的 OIDC 元数据…');
    try {
      await oauthBridge.request('config.test');
      notice('元数据检测通过。未验证 Client ID / Secret，也未执行授权或登录。');
    } catch (err) { notice(`${err.message} 请检查 Issuer、公网 HTTPS 可达性和 OIDC 元数据。`, true); }
    finally { lock(false); }
  });
  $('reload').addEventListener('click', refresh);
  addEventListener('pagehide', () => { $('client-secret').value = ''; }, { once: true });
  const resize = () => oauthBridge.resize(document.documentElement.scrollHeight + 24);
  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(resize).observe(document.body);
  resize();
  refresh();
})();
