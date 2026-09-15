# 贡献指南

[English](CONTRIBUTING.md) · **简体中文**

欢迎提交插件准入、条目修正、信任边界变更、发行源适配器和仓库级实现文档。插件实现与版本发布属于插件自己的仓库；面向使用者与插件作者的公开说明属于 [ZeroDeNet 文档站](https://github.com/zerodenet/docs)。

## 准入

使用[申请表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)，不要直接修改 `catalogs/plugins.json`，也不要另开入驻 PR。登记一个稳定产品身份，只声明实际支持的宿主目标；每个目标有独立稳定包 ID 和能力/界面上限。还需提供可独立核实的发布者与公钥归属、一个正式入驻版本、安全维护方式及实际宿主和平台证据。

自动化校验生成的入驻清单并把 Issue 标记为待审核。维护者在该 Issue 内审核插件立意、仓库控制权、发布者身份、各宿主/包身份与最大能力、迁移与卸载行为、安装包签名及真实宿主证据。添加 `status:accepted` 表示批准，并触发 Action 直接提交产品条目和自动生成的宿主投影；添加 `status:closed` 则关闭且不收录。

## 后续版本

不要向本仓库加入版本、产物、摘要、兼容声明或更新说明。通过准入后，开发者在自己的仓库发布正式版、RC 和 Dev 版，宿主直接发现并按登记边界执行校验。

仓库迁移、发布者或密钥轮换、发行源契约变化、新增宿主、扩大能力或界面范围、暂停、撤回或基础入驻资料变化时，使用市场资料更新 Issue，并经过同样的管理员标签决定。常规发版无需更新目录。市场实现与政策代码仍通过 PR 贡献，但插件准入决定不走单独 PR。

## 验证

运行：

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check

CI 检查统一注册表、宿主投影、包清单工具、API、站点、公钥和稳定身份，不执行开发者安装包。仓库级中英文参考保持同步；公开文档变更提交到文档站。禁止提交凭据、私钥、安装包、生成快照和工作站数据。
