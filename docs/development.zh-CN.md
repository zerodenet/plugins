# 开发模式

[English](development.md) · **简体中文**

## 选择分支

平台文档和共享提案属于 `main`。ZBoard 实现从 `zboard` 开始，客户端实现从 `znet-sink` 开始，Pull Request 也以同一宿主分支为合入目标。

[ZBoard 开发指南](https://github.com/zerodenet/plugins/blob/zboard/docs/development.zh-CN.md)提供 OAuth 工具链、构建和测试命令。[客户端接入范围](https://github.com/zerodenet/plugins/blob/znet-sink/docs/client-integration.zh-CN.md)记录开展客户端插件开发前所需的契约。

## 源码归属

宿主分支按 `<host>/<plugin>/` 存放插件源码，分别维护依赖、manifest、打包脚本和检查。仓库结构变化时保留稳定插件 ID 和公开模块路径。宿主应用与 SDK 留在各自仓库。

共享架构和项目政策在当前分支维护，以独立文档提交或文件更新同步。同步时检查差异；整体合入宿主分支会同时带入其实现。

## 验证

`main` 的修改检查产品状态是否准确、链接是否有效，以及中英文文档是否一致。宿主分支按实际实现定义检查；新增能力先在宿主边界验证，再由插件使用。

分支选择与评审见[贡献指南](../CONTRIBUTING.zh-CN.md)，能力和生命周期要求见[架构说明](governance.zh-CN.md)。
