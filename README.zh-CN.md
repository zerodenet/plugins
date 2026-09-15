# ZeroDeNet 插件市场

[English](README.md) · **简体中文**

这是面向 [ZBoard](https://github.com/zerodenet/zboard)、[ZNet Sink](https://github.com/zerodenet/znet-sink) 及未来 ZeroDeNet 宿主的统一插件市场。用户发现一个产品，产品再显式声明支持的宿主包。市场准入表示宿主团队已经审核其立意、维护与签名身份、发行来源以及允许使用的最大集成边界。

本仓库维护产品登记，并生成统一市场快照，不人工维护版本台账。开发者在自己的仓库管理正式版、RC 和 Dev 生命周期；构建流程校验作者发布清单并汇总为同一快照，各宿主显式查询自身目标后，仍使用已登记的发布者公钥独立验包。

## 浏览与查询

权威注册表是 [catalogs/plugins.json](catalogs/plugins.json)，面向用户的产品字段由 Issue Template 提交的固定发行清单经 Action 原样写入待审核 PR，不直接手工编辑。首发由 GitHub Actions 汇总并校验作者发行，再通过 GitHub Pages 原子发布 Astro 网站、统一快照、按宿主/频道拆分的静态 JSON API 和 schema，推荐市场域名为 `plugins.zerodenet.org`。ZBoard 与 ZNet Sink 下载对应宿主/频道文件，在本地按宿主版本、系统和架构选择产物；无需 Cloudflare Worker。当前已登记产品为 [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth)。

旧 [ZBoard](catalogs/zboard.json) 与 [ZNet Sink](catalogs/znet-sink.json) schema-v2 目录是宿主迁移期的自动兼容投影，不是独立来源。

产品条目保存发布者提交的原始名称、简介、分类、链接及稳定身份、仓库、发布者公钥、发行源，以及一个或多个宿主目标的稳定包 ID 与审核上限。网站直接展示登记值，不翻译、不改写、不推断缺失字段。构建期快照把已校验作者发行合并给网站与 API；宿主仍在本地最终验包。

## 只申请一次

1. 在独立仓库维护插件，提供许可证、配置指南、安全联系渠道及稳定签名身份。
2. 发布一个正式签名的入驻版本，包含固定安装包和 marketplace-entry.json。
3. 从签名安装包生成 `marketplace-entry.json`，再使用[入驻表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)，或参照[产品条目模板](templates/product-registration.json)提交方案。

通过准入后，后续正式版、RC 和 Dev 版只在插件仓库发布，常规发版不再提交市场 Issue。任何登记资料变化都使用[资料更新模板](https://github.com/zerodenet/plugins/issues/new?template=update-plugin.yml)，由 Action 从新的固定清单原样生成审核 PR；网站代码不得添加插件专属覆盖或美化文案。

离线导入不依赖市场准入，继续用于开发自测、私有或不便开源的插件、本地 DIY 以及其他自行管理的分发方式。

## 仓库布局

catalogs 保存统一产品注册表与兼容投影，src 保存 Astro 站点与静态 API 路由，scripts 保存准入、发布清单、快照与校验工具，schemas 定义可评审的数据边界。仓库内的 docs 只保留与实现和维护直接相关的契约、自动化、架构与实施记录。

面向使用者和插件作者的安装、发布、安全与 API 说明统一维护在 [ZeroDeNet 文档站](https://docs.zerodenet.org/marketplace/)。仓库级参考见[目录格式](docs/registry-format.zh-CN.md)、[自动化](docs/automation.zh-CN.md)、[开发](docs/development.zh-CN.md)和[架构边界](docs/governance.zh-CN.md)。
