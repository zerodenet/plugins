# ZeroDeNet 插件市场

[English](README.md) · **简体中文**

为 [ZBoard](https://github.com/zerodenet/zboard)、[ZNet Sink](https://github.com/zerodenet/znet-sink) 和未来宿主提供集中登记、收录和版本发现。收录不代表市场审核通过、安全背书或权限授权。

## 浏览与接口

[catalogs/plugins.json](catalogs/plugins.json) 是唯一产品登记。发布者通过登记或资料更新表单提交固定发行中的 `marketplace-entry.json`。自动化校验来源控制权、身份和元数据一致性后，原样登记完整 `listing`；不等待管理员批准标签，不创建入驻 PR。

正式版、RC、Dev 和安装包由发布者自己的仓库管理。市场从公开发行生成站点、统一快照和六个宿主/频道静态接口。权限或界面范围扩大不会导致版本被排除，也不需要重新申请登记。宿主独立校验签名、兼容性和安装包，展示申请权限、获取用户确认，并执行运行时授权。

生产域名为 `plugins.zerodenet.org`，使用 Cloudflare Pages，保留 GitHub Pages 备用。旧 [ZBoard](catalogs/zboard.json) 与 [ZNet Sink](catalogs/znet-sink.json) schema-v2 目录仅为自动生成的兼容投影。

## 首次登记

1. 在自己的仓库维护稳定的产品/包身份、签名身份、许可证和源码。
2. 在公开 GitHub Release 发布签名安装包及固定 `marketplace-entry.json`，支持正式版、RC 和 Dev。
3. 由源码仓库所有者或可被自动核实写权限的协作者提交[登记表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)。

名称、链接、仓库/密钥、宿主/包登记或撤回使用[资料更新表单](https://github.com/zerodenet/plugins/issues/new?template=update-plugin.yml)。来源迁移需要同时证明对新旧仓库的控制权。每个版本的权限变化不需要市场批准，普通发行不需要更新目录。市场不翻译、不改写、不推断产品资料。

离线导入、私有插件和本地测试由宿主管理。市场不执行投稿安装包。

## 参考

参阅[登记格式](docs/registry-format.zh-CN.md)、[自动化](docs/automation.zh-CN.md)、[开发](docs/development.zh-CN.md)、[架构](docs/governance.zh-CN.md)与[文档站](https://docs.zerodenet.org/marketplace/)。
