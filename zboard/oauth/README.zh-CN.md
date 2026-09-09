# ZBoard OAuth 插件

[English](README.md) · **简体中文**

让用户通过 GitHub、Google 或组织的身份提供方登录 ZBoard。插件将外部 OAuth2 / OpenID Connect 提供方接入 ZBoard 的账户注册与绑定流程。

**插件 ID：** `zboard.oauth` · **源码版本：** `0.2.0`

## 提供方

| 提供方 | 配置方式 | 身份来源 |
| --- | --- | --- |
| GitHub | 快捷配置，填写 Client ID 和 Client Secret | 稳定的 GitHub 用户 ID 与已验证主邮箱 |
| Google | 快捷配置，填写 Client ID 和 Client Secret | OpenID Connect 身份声明 |
| 自定义 OAuth2 | 配置端点、Scopes 和用户资料字段映射 | JSON 用户资料中的稳定身份标识 |
| 自定义 OpenID Connect | 配置 Issuer、客户端凭据和 Scopes | Discovery 元数据与已校验身份声明 |

最多配置 16 个提供方，各自设置显示名称和启停状态。配置页提供 GitHub、Google 快捷入口和自定义提供方编辑器。

## 使用要求

宿主需实现插件要求的多提供方身份 API、公开配置投影和外部账户注册流程。Manifest 当前声明 `>=0.0.1 <0.1.0`、插件协议 `1` 和页面桥 `1`；除宿主显示版本外，还应确认 API 支持情况。

部署站点需要公开 HTTPS 根地址，并在提供方登记应用回调地址。当提供方未返回已验证邮箱、新用户需要补充邮箱验证时，站点还需配置 SMTP。

安装包供应状态见[仓库 README](../../README.zh-CN.md)。构建目标包含 Linux、macOS 和 Windows。macOS 宿主启动曾遇到 Gatekeeper 拒绝，稳定平台运行及生产签名、公证仍待验证。

## 配置步骤

1. 在 ZBoard 站点设置中填写公开根地址。
2. 在各提供方登记以下重定向 URI，将示例域名替换为实际域名：

   ```text
   https://panel.example.com/api/v1/auth/oidc/callback
   ```

3. 按[安装指南](../../docs/usage.zh-CN.md)信任发布者并导入签名包。
4. 打开插件配置页，添加 GitHub、Google 或自定义提供方，填写应用的 Client ID 和 Client Secret。
5. 保存并检测配置，然后启用插件，使用测试账户验证完整流程。

配置检测校验参数，并在 OIDC 模式下读取 Discovery 元数据；检测成功不代表已完成提供方授权。本地开发还可使用回环回调，例如 `http://127.0.0.1:18090/api/v1/auth/oidc/callback`。

## 账户与注册

ZBoard 判断外部身份能否登录、注册或绑定账户。关闭注册后，未绑定身份不能通过插件创建账户或登录；已有绑定身份仍需通过宿主的账户检查。

相同邮箱不会自动绑定账户。用户应先登录已有账户，再到安全设置中绑定提供方。移除提供方会关闭对应登录入口，但保留核心账户和已建立的绑定。

自定义字段、密钥处理、账户绑定行为和问题排查见[配置参考](docs/configuration.zh-CN.md)。

## 开发

从仓库根目录运行：

```sh
sh scripts/check.sh
```

插件包含协议 fixture、配置测试、真实 gRPC 进程测试，以及界面和消息桥测试。[开发指南](../../docs/development.zh-CN.md)介绍工具链、SDK workspace 和本地打包；[发布指南](../../docs/publishing.zh-CN.md)介绍发行签名与平台验证。

## 支持

提交 [Issue](https://github.com/zerodenet/plugins/issues) 时，请提供插件版本、宿主构建、平台和脱敏复现步骤。安全漏洞按[安全政策](../../SECURITY.zh-CN.md)报告。

采用 [MPL-2.0](../../LICENSE) 许可证。
