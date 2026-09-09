## Listing / 收录信息

Host, plugin ID, version, upstream release and source commit:
宿主、插件 ID、版本、上游发行地址与源码提交：

## Changes / 改动

Describe a new listing, release update, withdrawal or publisher change.
说明新增收录、版本更新、撤回或发布者变更。

## Evidence / 证据

Link publisher/key ownership evidence, package signature verification and host/platform checks.
提供发布者及公钥归属证据、安装包验签和宿主/平台测试结果。

- [ ] Source and packages remain in the independent repository / 源码与安装包保留在独立仓库
- [ ] Used `templates/plugin-entry.json` and retained existing releases / 使用条目模板并保留既有发行记录
- [ ] URLs, SHA-256, byte sizes and compatibility match the signed packages / 地址、摘要、字节数及兼容性与签名包一致
- [ ] No private keys or credentials / 未包含私钥或凭据
- [ ] `python3 -m unittest discover -s tests` and `python3 scripts/validate.py`
- [ ] Documentation updated in both languages where needed / 必要文档已同步中英文
