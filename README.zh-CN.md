# ZBoard 插件

[English](README.md) · **简体中文**

[ZeroDeNet Plugins](https://github.com/zerodenet/plugins/blob/main/README.zh-CN.md) 的 ZBoard 插件集合。当前分支维护 ZBoard 插件源码、配置指南、打包和测试。

[![Plugin checks](https://github.com/zerodenet/plugins/actions/workflows/ci.yml/badge.svg?branch=zboard)](https://github.com/zerodenet/plugins/actions/workflows/ci.yml?query=branch%3Azboard)

## 插件

| 插件 | 功能 |
| --- | --- |
| [OAuth](zboard/oauth/README.zh-CN.md) | 通过 GitHub、Google 和自定义 OAuth2 / OpenID Connect 登录与注册 |

OAuth 支持源码构建和集成测试，签名发行版本与公共目录已列入规划。宿主 API 要求和验证状态见各插件 README。

## 开发

```sh
git clone --branch zboard https://github.com/zerodenet/plugins.git
cd plugins
sh scripts/check.sh
```

检查需要 Go 1.26.8 和 Node.js 18 或更新版本。打包另需 Python 3，以及包含插件打包器的兼容 ZBoard 源码目录。完整环境设置见[开发指南](docs/development.zh-CN.md)。

源码保留在 `zboard/<plugin>/`。OAuth 模块为 `github.com/zerodenet/plugins/zboard/oauth`，插件 ID 为 `zboard.oauth`。

## 文档

- [安装与运维](docs/usage.zh-CN.md)
- [OAuth 配置](zboard/oauth/README.zh-CN.md)与[字段参考](zboard/oauth/docs/configuration.zh-CN.md)
- [开发](docs/development.zh-CN.md)与[发布](docs/publishing.zh-CN.md)
- [插件架构](docs/governance.zh-CN.md)

## 贡献

实现分支从 `zboard` 创建，Pull Request 也指向 `zboard`。CI 检查该分支的推送和以它为目标的 PR。共享平台文档属于 [main](https://github.com/zerodenet/plugins/blob/main/README.zh-CN.md)，客户端插件属于 [znet-sink](https://github.com/zerodenet/plugins/blob/znet-sink/README.zh-CN.md)。

提交改动或报告前，请阅读[贡献指南](CONTRIBUTING.zh-CN.md)、[项目治理](GOVERNANCE.zh-CN.md)和[安全政策](SECURITY.zh-CN.md)。

## 许可证

[Mozilla Public License 2.0](LICENSE)。第三方依赖保留各自许可证。
