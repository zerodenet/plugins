# ZNet Sink 插件

[English](README.md) · **简体中文**

[ZeroDeNet Plugins](https://github.com/zerodenet/plugins/blob/main/README.zh-CN.md) 的客户端插件分支，专门维护 [ZNet Sink](https://github.com/zerodenet/znet-sink) 扩展。

## 状态

当前分支建立客户端接入范围与贡献流程。客户端插件 API、运行时和包格式仍在设计，尚无可安装的客户端插件或运行时检查。

## 范围

客户端插件将通过 ZNet Sink 自己的 API 提供扩展。配置变更、系统权限、连接管理和内核控制遵循客户端服务及策略。市场接入使用共享分发模型，运行兼容性由客户端决定。

实现前所需的契约见[客户端接入](docs/client-integration.zh-CN.md)。

## 开发

客户端插件改动以 `znet-sink` 为基础和合入目标。宿主契约实现后，源码放在 `znet-sink/<plugin>/`，同时提供配置指南、依赖、构建流程和测试。

```sh
git clone --branch znet-sink https://github.com/zerodenet/plugins.git
cd plugins
```

实现开始前，验证文档链接、中英文一致性和与宿主设计的对应关系。运行时与打包检查随其所验证的代码一同引入。

## 项目资源

- [客户端文档](docs/README.zh-CN.md)
- [贡献指南](CONTRIBUTING.zh-CN.md)与[项目治理](GOVERNANCE.zh-CN.md)
- [安全政策](SECURITY.zh-CN.md)
- [平台介绍](https://github.com/zerodenet/plugins/blob/main/README.zh-CN.md)
- [ZBoard 插件集合](https://github.com/zerodenet/plugins/blob/zboard/README.zh-CN.md)

## 许可证

[Mozilla Public License 2.0](LICENSE)。第三方依赖保留各自许可证。
