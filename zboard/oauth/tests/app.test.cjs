const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
async function fixture(initial=[],failSave=false){
 const elements=new Map();const ids=[...fs.readFileSync(path.join(__dirname,'../ui/index.html'),'utf8').matchAll(/id="([^"]+)"/g)].map(m=>m[1]);
 const element=()=>({value:'',checked:false,disabled:false,hidden:false,children:[],listeners:{},addEventListener(name,fn){this.listeners[name]=fn;},reportValidity(){return true;},replaceChildren(){this.children=[];},append(child){this.children.push(child);}});
 for(const id of ids)elements.set(id,element());const calls=[];let revision=1;let providers=initial;
 const context={document:{getElementById:id=>elements.get(id),createElement:element,documentElement:{scrollHeight:900},body:{}},Number,Error,addEventListener(){},oauthBridge:{resize(){},async request(type,body){calls.push({type,body:body&&JSON.parse(JSON.stringify(body))});if(type==='context.load')return{plugin_id:'zboard.oauth',surface:'admin',page_id:'settings'};if(type==='config.load')return{revision,configured:true,config:{providers}};if(type==='config.save'){if(failSave)throw new Error('conflict');revision++;providers=body.config.providers.map(p=>({...p,has_secret:!!p.client_secret||p.keep_secret,client_secret:undefined,keep_secret:undefined}));return{revision,configured:true};}return{healthy:true};}}};
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../ui/app.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));return{elements,calls};
}
test('GitHub shortcut saves without OIDC and clears the secret',async()=>{
 const {elements:e,calls}=await fixture();e.get('add-github').listeners.click();e.get('client-id').value='client';e.get('client-secret').value='secret';assert.equal(e.get('settings').listeners.submit,undefined);assert.equal(e.get('custom-fields').hidden,true);
 await e.get('save').listeners.click({preventDefault(){}});const save=calls.find(c=>c.type==='config.save');assert.equal(save.body.config.providers[0].preset,'github');assert.equal(save.body.config.providers[0].client_secret,'secret');assert.equal(e.get('client-secret').value,'');assert.match(e.get('state').textContent,/版本 2/);
});
test('editing one provider preserves other entries and retains secrets',async()=>{
 const {elements:e,calls}=await fixture([{id:'github',name:'GitHub',preset:'github',client_id:'gh',has_secret:true},{id:'google',name:'Google',preset:'google',client_id:'g',has_secret:true}]);e.get('providers').children[0].listeners.click();assert.equal(e.get('client-secret').value,'');assert.equal(e.get('provider-id').disabled,true);e.get('enabled').checked=false;
 await e.get('save').listeners.click({preventDefault(){}});const p=calls.find(c=>c.type==='config.save').body.config.providers;assert.equal(p.length,2);assert.equal(p[0].disabled,true);assert.equal(p[0].keep_secret,true);assert.equal(p[1].keep_secret,true);
});
test('custom OAuth2 exposes profile mapping and endpoints',async()=>{
 const {elements:e,calls}=await fixture();e.get('add-custom').listeners.click();e.get('provider-id').value='company';e.get('name').value='Company';e.get('client-id').value='client';e.get('issuer').value='https://id.example.com';e.get('authorization-endpoint').value='https://id.example.com/auth';e.get('token-endpoint').value='https://id.example.com/token';e.get('userinfo-endpoint').value='https://id.example.com/me';e.get('subject-field').value='data.id';
 await e.get('save').listeners.click({preventDefault(){}});const p=calls.find(c=>c.type==='config.save').body.config.providers[0];assert.equal(p.protocol,'oauth2');assert.equal(p.subject_field,'data.id');assert.equal(p.userinfo_endpoint,'https://id.example.com/me');
});
test('conflicts disable writes until refresh and erase entered secrets',async()=>{
 const {elements:e,calls}=await fixture([],true);e.get('add-google').listeners.click();e.get('client-id').value='client';e.get('client-secret').value='secret';await e.get('save').listeners.click({preventDefault(){}});assert.equal(e.get('fields').disabled,true);assert.equal(e.get('client-secret').value,'');await e.get('save').listeners.click({preventDefault(){}});assert.equal(calls.filter(c=>c.type==='config.save').length,1);
});
