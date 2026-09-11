# ZeroDeNet 插件市场

[English](README.md) · **简体中文**

这是面向 [ZBoard](https://github.com/zerodenet/zboard)、[ZNet Sink](https://github.com/zerodenet/znet-sink) 及未来 ZeroDeNet 宿主的精选插件目录。插件通过市场准入，表示宿主团队已经审核其立意、维护与签名身份、发行来源以及允许使用的最大集成边界。

本仓库是登记目录，不是版本台账。开发者在自己的仓库维护正式版、RC 和 Dev 生命周期；支持的宿主直接发现这些发行版本，使用已登记的发布者公钥验签，并提供在线安装、升级、降级和频道选择。

## 浏览插件

| 宿主 | 目录 | 已有项目 |
| --- | --- | --- |
| ZBoard | [catalogs/zboard.json](catalogs/zboard.json) | [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth) |
| ZNet Sink | [catalogs/znet-sink.json](catalogs/znet-sink.json) | 暂无入驻插件 |

目录保存入驻资料：插件 ID、名称、作用、作者/维护者、许可证、资料链接、仓库地址、发布者公钥、发行源、界面范围和能力上限。宿主从插件中心展示基础资料，再根据登记的仓库地址读取 Releases 中的版本、产物、兼容声明和更新说明。

## 只申请一次

1. 在独立仓库维护插件，提供许可证、配置指南、安全联系渠道及稳定签名身份。
2. 发布一个正式签名的入驻版本，包含固定安装包和 marketplace-entry.json。
3. 使用[入驻表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)，或参照[目录条目模板](templates/plugin-entry.json)提交方案。

通过准入后，后续正式版、RC 和 Dev 版只在插件仓库发布，常规发版不再提交市场 Issue，基础入驻资料变化时更新目录。仓库地址、发布者身份或公钥、发行源契约、支持宿主、界面上限或能力上限发生变化时，也需要回来更新登记。

离线导入不依赖市场准入，继续用于开发自测、私有或不便开源的插件、本地 DIY 以及其他自行管理的分发方式。

## 仓库布局

catalogs 保存各宿主的精选目录，scripts 保存准入和校验工具，templates 保存条目示例，docs 定义契约、发行政策和宿主边界。

参见[目录格式](docs/registry-format.zh-CN.md)、[发布规范](docs/publishing.zh-CN.md)、[自动化](docs/automation.zh-CN.md)和[架构边界](docs/governance.zh-CN.md)。英文为参考版本，简体中文指南同步维护。
