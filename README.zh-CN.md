# ZeroDeNet Plugins

[English](README.md) · **简体中文**

ZeroDeNet 生态的插件仓库，维护官方插件源码、开发者文档，以及面向 [ZBoard](https://github.com/zerodenet/zboard) 和 [ZNet Sink](https://github.com/zerodenet/znet-sink) 的共享插件市场设计。

[![Plugin checks](https://github.com/zerodenet/plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/zerodenet/plugins/actions/workflows/ci.yml)
[![License: MPL-2.0](https://img.shields.io/badge/License-MPL--2.0-blue.svg)](LICENSE)

## 插件

| 插件 | 宿主 | 功能 |
| --- | --- | --- |
| [OAuth](zboard/oauth/README.zh-CN.md) | ZBoard | 通过 GitHub、Google 或自定义 OAuth2 / OpenID Connect 提供方登录与注册。 |

OAuth 插件目前支持源码构建和集成测试，签名发行版本与公共目录已列入规划。ZNet Sink 接入也已列入规划，其插件运行时与宿主 API 尚未提供。

## 开始使用

安装插件前，先阅读对应插件的 README，确认宿主要求和配置方式，再按照[安装指南](docs/usage.zh-CN.md)操作。开发阶段可以使用宿主的签名工具在本地构建安装包。

本地开发时，克隆仓库并运行检查：

```sh
git clone https://github.com/zerodenet/plugins.git
cd plugins
sh scripts/check.sh
```

当前检查需要 Go 1.26.8 和 Node.js 18 或更新版本。打包另需 Python 3，以及包含插件打包器的 ZBoard 源码目录。环境设置和构建命令见[开发指南](docs/development.zh-CN.md)。

## 架构

插件通过宿主应用开放的 API 提供第三方集成和扩展界面。各宿主负责安装、权限、配置、私有数据和升级；账户注册、凭证管理等业务规则由宿主核心服务执行。

共享市场将按插件、宿主和平台组织发行版本。各宿主保留自己的 API 和包兼容规则，具体契约见[架构说明](docs/governance.zh-CN.md)与[市场提案](docs/marketplace-design.zh-CN.md)。

## 文档

| 文档 | 适用读者 |
| --- | --- |
| [安装与运维](docs/usage.zh-CN.md) | 安装、维护插件的管理员 |
| [开发指南](docs/development.zh-CN.md) | 构建、测试插件的开发者 |
| [架构说明](docs/governance.zh-CN.md) | 设计宿主集成的插件作者 |
| [发布指南](docs/publishing.zh-CN.md) | 准备发行版本的维护者 |
| [市场提案](docs/marketplace-design.zh-CN.md) | 参与共享分发设计的贡献者 |

[查看全部文档 →](docs/README.zh-CN.md)

## 参与贡献

欢迎提交问题报告、文档改进、翻译和插件贡献。评审流程见[贡献指南](CONTRIBUTING.zh-CN.md)，项目决策方式见[项目治理](GOVERNANCE.zh-CN.md)。

可复现的问题请提交至 [GitHub Issues](https://github.com/zerodenet/plugins/issues)；安全漏洞请按[安全报告流程](SECURITY.zh-CN.md)处理。

## 许可证

[Mozilla Public License 2.0](LICENSE)。第三方依赖遵循各自的许可证。
