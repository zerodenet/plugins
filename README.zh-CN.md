# ZeroDeNet Plugins

[English](README.md) · **简体中文**

ZeroDeNet 生态的插件平台。本仓库统一维护项目文档、各宿主的插件集合，以及面向 [ZBoard](https://github.com/zerodenet/zboard) 和 [ZNet Sink](https://github.com/zerodenet/znet-sink) 的共享市场设计。

## 仓库分支

| 分支 | 职责 |
| --- | --- |
| **main** | 平台介绍、共享架构、贡献规范和市场提案 |
| [**zboard**](https://github.com/zerodenet/plugins/tree/zboard) | ZBoard 插件、配置指南、构建和测试 |
| [**znet-sink**](https://github.com/zerodenet/plugins/tree/znet-sink) | 客户端插件开发和集成文档 |

当前分支是文档入口，各宿主插件集合在自己的分支中维护和发行。贡献应提交到负责相应改动的分支。

## 插件集合

### ZBoard

[OAuth 插件](https://github.com/zerodenet/plugins/blob/zboard/zboard/oauth/README.zh-CN.md)将 GitHub、Google 和自定义 OAuth2 / OpenID Connect 提供方接入 ZBoard 登录与注册流程。源码构建和集成测试位于 `zboard` 分支。

### ZNet Sink

[客户端分支](https://github.com/zerodenet/plugins/blob/znet-sink/README.zh-CN.md)定义客户端插件的接入范围。宿主 API 和插件运行时正在设计，尚无客户端插件实现。

签名发行版本和公共市场目录已列入规划。[市场提案](docs/marketplace-design.zh-CN.md)描述跨宿主的共享发现和分发。

## 架构

插件通过专用 API 扩展宿主。各应用负责权限检查、配置、私有数据、安装与升级；核心业务规则由所属应用执行。

市场按插件、宿主和平台组织发行版本，安装决策与运行行为遵循各宿主契约。职责划分见[插件架构](docs/governance.zh-CN.md)。

## 文档

- [文档索引](docs/README.zh-CN.md)
- [插件选择与运维](docs/usage.zh-CN.md)
- [开发模式](docs/development.zh-CN.md)
- [发布模式](docs/publishing.zh-CN.md)
- [贡献指南](CONTRIBUTING.zh-CN.md)与[项目治理](GOVERNANCE.zh-CN.md)

宿主专属的配置、命令和问题排查文档在各自分支维护。

## 社区

通过 [GitHub Issues](https://github.com/zerodenet/plugins/issues)报告问题或提交设计提案，问题报告应注明宿主与插件。安全漏洞按[安全政策](SECURITY.zh-CN.md)报告。

## 许可证

[Mozilla Public License 2.0](LICENSE)。第三方依赖保留各自许可证。
