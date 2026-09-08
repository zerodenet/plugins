(() => {
 const $=id=>document.getElementById(id);
 let revision=null, entries=[], selected=-1, draft=null, busy=false;
 const fields={id:'provider-id',name:'name',protocol:'protocol',issuer:'issuer',authorization_endpoint:'authorization-endpoint',token_endpoint:'token-endpoint',userinfo_endpoint:'userinfo-endpoint',subject_field:'subject-field',email_field:'email-field',email_verified_field:'email-verified-field',token_auth_method:'token-auth',scopes:'scopes',client_id:'client-id'};
 const notice=(text,error=false)=>{$('notice').textContent=text;$('notice').className=error?'error':'success';};
 function lock(value){busy=value;$('fields').hidden=!draft;$('fields').disabled=value||revision===null||!draft;for(const id of ['reload','add-github','add-google','add-custom','test'])$(id).disabled=value|| (id!=='reload'&&revision===null);$('remove').disabled=selected<0;}
 function updateProtocol(){const custom=draft?.preset==='custom'||!draft?.preset;$('custom-fields').hidden=!custom;const oauth=$('protocol').value==='oauth2';$('oauth-fields').hidden=!oauth;for(const id of ['issuer','authorization-endpoint','token-endpoint','userinfo-endpoint','subject-field'])$(id).required=custom&&(id==='issuer'||oauth);$('preset-note').textContent=custom?'':`${draft.preset==='github'?'GitHub':'Google'} 的协议、地址、Scopes 和用户字段已预设，只需填写客户端信息。`;}
 function edit(index,preset){
  if(busy)return;selected=index;
  draft=index>=0?{...entries[index]}:{id:preset==='custom'?'':preset,name:preset==='custom'?'':preset==='github'?'GitHub':'Google',preset,protocol:preset==='google'?'oidc':'oauth2',token_auth_method:'basic',subject_field:'id',email_field:'email',email_verified_field:'email_verified',scopes:[]};
  for(const [key,id]of Object.entries(fields))$(id).value=key==='scopes'?(draft.scopes||[]).join(' '):(draft[key]||'');
  $('provider-id').disabled=index>=0;$('provider-id').required=index<0;
  $('enabled').checked=!draft.disabled;$('client-secret').value='';$('clear-secret').checked=false;
  $('secret-hint').textContent=draft.has_secret?'已保存密钥。留空保留，输入新值替换；更换客户端或端点时必须重新输入。':'尚未保存密钥。';
  $('editor-title').textContent=index>=0?'编辑提供方':'添加提供方';updateProtocol();lock(false);
 }
 function render(){
  $('providers').replaceChildren();$('empty').hidden=entries.length>0;
  entries.forEach((entry,index)=>{const button=document.createElement('button');button.type='button';button.textContent=`${entry.name||entry.id} · ${entry.disabled?'已停用':'已启用'}`;button.addEventListener('click',()=>edit(index));$('providers').append(button);});
 }
 function show(view){if(!view||!Number.isSafeInteger(view.revision)||typeof view.configured!=='boolean')throw new Error('配置状态无效');revision=view.revision;entries=view.config?.providers||[];if(!Array.isArray(entries)||entries.length>16)throw new Error('提供方配置无效');$('state').textContent=`配置版本 ${revision} · ${entries.length} 个提供方`;render();}
 async function refresh(){if(busy)return;lock(true);try{const context=await oauthBridge.request('context.load');if(context.plugin_id!=='zboard.oauth'||context.surface!=='admin'||context.page_id!=='settings')throw new Error('需要管理员配置会话');show(await oauthBridge.request('config.load'));draft=null;selected=-1;notice('选择提供方编辑，或使用快捷配置添加。');}catch(err){revision=null;notice(err.message,true);}finally{lock(false);}}
 function stored(entry){const value={...entry};delete value.has_secret;delete value.client_secret;if(entry.has_secret)value.keep_secret=true;return value;}
 async function persist(next){
  lock(true);notice('正在保存…');
  try{await oauthBridge.request('config.save',{revision,config:{providers:next}});show(await oauthBridge.request('config.load'));draft=null;selected=-1;notice('已保存。插件启用后，登录和注册页会显示相应入口。');}
  catch(err){revision=null;notice(`${err.message} 请刷新后重试。`,true);}
  finally{for(const entry of next)delete entry.client_secret;$('client-secret').value='';lock(false);}
 }
 $('save').addEventListener('click',async event=>{
  event.preventDefault();if(busy||revision===null||!draft||!$('settings').reportValidity())return;
  const value={preset:draft.preset||'custom',disabled:!$('enabled').checked};
  for(const [key,id]of Object.entries(fields))value[key]=key==='scopes'?$('scopes').value.trim().split(/\s+/).filter(Boolean):$(id).value.trim();
  if(selected<0&&entries.some(entry=>entry.id===value.id)){notice('提供方标识已存在。',true);return;}
  if(value.preset!=='custom'){for(const key of ['protocol','issuer','authorization_endpoint','token_endpoint','userinfo_endpoint','subject_field','email_field','email_verified_field','token_auth_method','scopes'])delete value[key];}
  const secret=$('client-secret').value;
  if(secret)value.client_secret=secret;else if(draft.has_secret&&!$('clear-secret').checked)value.keep_secret=true;
  const next=entries.map(stored);if(selected>=0)next[selected]=value;else next.push(value);await persist(next);
 });
 $('remove').addEventListener('click',async()=>{if(busy||selected<0||revision===null)return;await persist(entries.filter((_,index)=>index!==selected).map(stored));});
 for(const preset of ['github','google','custom'])$('add-'+preset).addEventListener('click',()=>{if(entries.length>=16){notice('最多配置 16 个提供方。',true);return;}edit(-1,preset);});
 $('protocol').addEventListener('change',()=>{if($('protocol').value==='oidc'&&!$('scopes').value)$('scopes').value='openid profile email';updateProtocol();});
 $('reload').addEventListener('click',refresh);
 $('test').addEventListener('click',async()=>{if(busy||revision===null)return;lock(true);try{await oauthBridge.request('config.test');notice('配置检测通过；还需要使用真实客户端完成授权验证。');}catch(err){notice(err.message,true);}finally{lock(false);}});
 addEventListener('pagehide',()=>{$('client-secret').value='';},{once:true});
 const resize=()=>oauthBridge.resize(document.documentElement.scrollHeight+24);if(typeof ResizeObserver!=='undefined')new ResizeObserver(resize).observe(document.body);resize();refresh();
})();
