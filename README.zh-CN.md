# ZeroDeNet 插件市场

[English](README.md) · **简体中文**

面向 [ZBoard](https://github.com/zerodenet/zboard) 和 [ZNet Sink](https://github.com/zerodenet/znet-sink) 的公开插件注册表。发布者在各自仓库构建和发行插件；本仓库记录发行来源、宿主兼容性以及产物验证信息。

## 浏览插件

| 宿主 | 注册表 | 已有项目 |
| --- | --- | --- |
| ZBoard | [catalogs/zboard.json](catalogs/zboard.json) | [OAuth for ZBoard](https://github.com/higanbana986/zboard-oauth) — 源码可用，签名发行待发布 |
| ZNet Sink | [catalogs/znet-sink.json](catalogs/znet-sink.json) | 暂无提交 |

OAuth 将 GitHub、Google 和自定义 OAuth2 / OpenID Connect 提供方接入 ZBoard。源码、测试、配置指南和发行流程均在独立仓库维护。账户创建、注册策略及会话仍由 ZBoard 核心掌管。

上述 JSON 文件是经评审的源记录，不是签名安装目录，不能直接填入 ZBoard 的 `plugins.catalog_url`。`releases` 数组为空的插件只提供源码入口，不代表已有可安装版本。参见[安装与信任](docs/usage.zh-CN.md)。

## 提交插件

1. 在公开源码仓库维护插件，提供许可证、配置指南与安全联系渠道。
2. 独立发布签名版本，提供固定安装包、SHA-256 摘要与平台信息。
3. 使用[提交表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)，或参照[条目模板](templates/plugin-entry.json)向 `main` 提交 PR。

一次发行只更新所属宿主目录内的一个插件条目。市场 CI 校验元数据，不编译插件，也不执行贡献者的安装包。审核要求见[贡献指南](CONTRIBUTING.zh-CN.md)。

## 仓库布局

```text
catalogs/       每个宿主一个源目录
scripts/        注册表校验
templates/     提交示例
.github/        贡献表单与校验工作流
docs/           注册表格式、发行规范及宿主边界
```

所有持续维护的市场数据及政策均位于 `main`。插件源码与二进制产物归属各自独立仓库，市场不再维护按产品区分的源码分支。

## 文档

- [注册表格式](docs/registry-format.zh-CN.md)
- [发布与审核](docs/publishing.zh-CN.md)
- [宿主职责](docs/governance.zh-CN.md)
- [开发指南](docs/development.zh-CN.md)
- [分发提案](docs/marketplace-design.zh-CN.md)
- [治理](GOVERNANCE.zh-CN.md) · [安全](SECURITY.zh-CN.md)

英文为参考版本，简体中文指南同步维护。注册表资料采用 [MPL-2.0](LICENSE)，各插件保留各自许可证。
