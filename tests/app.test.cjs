const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
async function fixture(failSave = false) {
  const elements = new Map();
  for (const id of ['notice','fields','reload','test','state','settings','issuer','client-id','client-secret','scopes','replace','save']) elements.set(id, {value:'',checked:false,disabled:false,listeners:{},addEventListener(name,fn){this.listeners[name]=fn;},reportValidity(){return true;}});
  const calls = [];
  const context = { document:{getElementById:id=>elements.get(id),documentElement:{scrollHeight:700},body:{}},Number,Error,
    addEventListener(){}, oauthBridge:{resize(){},async request(type,body){calls.push({type,body:body && JSON.parse(JSON.stringify(body))});if(type==='context.load')return {plugin_id:'zboard.oauth',page_id:'settings',surface:'admin'};if(type==='config.load')return {revision:1,configured:true};if(type==='config.save'){if(failSave)throw new Error('conflict');return {revision:2,configured:true};}return {healthy:true};}},
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../ui/app.js'),'utf8'),context);
  await new Promise(resolve=>setImmediate(resolve));
  return {elements,calls};
}
test('sandbox save uses explicit bridge action and clears the secret after success',async()=>{
 const {elements:e,calls}=await fixture();
 assert.equal(e.get('fields').disabled,false);
 e.get('issuer').value='https://id.example.com';e.get('client-id').value='client';e.get('client-secret').value='secret';e.get('scopes').value='openid email';e.get('replace').checked=true;
 assert.equal(e.get('settings').listeners.submit,undefined);
 await e.get('save').listeners.click({preventDefault(){}});
 const save=calls.find(c=>c.type==='config.save');
 assert.equal(save.body.revision,1);assert.equal(save.body.config.client_secret,'secret');
 assert.equal(e.get('client-secret').value,'');assert.equal(e.get('replace').checked,false);assert.match(e.get('state').textContent,/版本 2/);
});
test('a rejected save disables further writes until version refresh and removes the secret',async()=>{
 const {elements:e,calls}=await fixture(true);
 e.get('issuer').value='https://id.example.com';e.get('client-id').value='client';e.get('client-secret').value='secret';e.get('scopes').value='openid';
 await e.get('save').listeners.click({preventDefault(){}});
 assert.equal(e.get('fields').disabled,true);assert.equal(e.get('client-secret').value,'');
 await e.get('save').listeners.click({preventDefault(){}});
 assert.equal(calls.filter(c=>c.type==='config.save').length,1);
 await e.get('reload').listeners.click();assert.equal(e.get('fields').disabled,false);
});
