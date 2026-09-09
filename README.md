# ZeroDeNet Plugins

ZeroDeNet 的共享插件源码与市场规范仓库，面向 ZBoard、ZNet Sink 客户端及后续接入的宿主。市场负责发现和分发，各产品负责插件运行、能力准入、数据与生命周期。

## 当前插件

| 宿主 | 插件 | 功能 | 状态 |
| --- | --- | --- | --- |
| ZBoard | [zboard.oauth](zboard/oauth/README.md) | GitHub、Google、自定义 OAuth2 / OIDC 登录与注册 | 源码版本 0.2.0；需要支持插件身份协议的宿主 |
| ZNet Sink | 暂无 | 客户端插件接口与运行时待独立设计 | 尚未接入 |

这里已迁入 OAuth 插件源码及原始提交历史。共享目录 v2 仍是草案，尚未发布签名市场目录或正式安装包。仓库首页不是 ZBoard 的 `catalog_url`，不要将其填入市场配置。

## 使用与开发

- 安装、配置和卸载：[使用规范](docs/usage.md)、[OAuth 使用说明](zboard/oauth/README.md)。
- 本地检查：安装 Go 1.26.8、Node.js 18+，从仓库根目录运行 `sh scripts/check.sh`。
- 构建与签名：另需 Python 3 和包含插件打包器的 ZBoard 检出目录，见 [开发规范](docs/development.md)。
- 提交修改：[贡献指南](CONTRIBUTING.md)；新增扩展点先阅读 [宿主边界准则](docs/governance.md)。
- 发布插件：[发布与上架规范](docs/publishing.md)；市场演进见 [共享市场草案](docs/marketplace-design.md)。

```text
zboard/oauth/        ZBoard OAuth 插件源码、测试与打包脚本
docs/               使用、开发、宿主边界和发布规范
scripts/check.sh    仓库检查入口
.github/workflows/  自动检查
```

每个插件维护自己的依赖和验证入口。后续客户端插件放入 `znet-sink/<plugin>/`，在宿主协议实现前不放置可安装的占位插件。宿主核心实现和 SDK 分别留在 [ZBoard](https://github.com/zerodenet/zboard) 与 [ZNet Sink](https://github.com/zerodenet/znet-sink) 仓库。

本仓库代码采用 [MPL-2.0](LICENSE)；第三方依赖保留各自许可证。
