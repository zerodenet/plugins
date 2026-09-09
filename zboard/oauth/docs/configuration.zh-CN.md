# OAuth 配置参考

[English](configuration.md) · **简体中文**

安装和首次配置见 [ZBoard OAuth 插件](../README.zh-CN.md)。本文介绍提供方设置，以及所支持 ZBoard 集成中的账户行为。

## 配置结构

顶层 `providers` 数组最多包含 16 个提供方。新增提供方使用稳定 `id`，由 1–32 个小写字母、数字、下划线或连字符组成，且不能重复。配置界面在创建后固定 ID；修改登录按钮名称时使用 `name`。

以下为使用占位凭据的完整示例：

```json
{
  "providers": [
    {
      "id": "github",
      "preset": "github",
      "client_id": "YOUR_GITHUB_CLIENT_ID",
      "client_secret": "YOUR_GITHUB_CLIENT_SECRET"
    },
    {
      "id": "google",
      "preset": "google",
      "client_id": "YOUR_GOOGLE_CLIENT_ID",
      "client_secret": "YOUR_GOOGLE_CLIENT_SECRET"
    },
    {
      "id": "company",
      "name": "Company account",
      "preset": "custom",
      "protocol": "oauth2",
      "issuer": "https://identity.example.com",
      "authorization_endpoint": "https://identity.example.com/oauth/authorize",
      "token_endpoint": "https://identity.example.com/oauth/token",
      "userinfo_endpoint": "https://identity.example.com/api/me",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "token_auth_method": "basic",
      "scopes": ["profile", "email"],
      "subject_field": "data.id",
      "email_field": "data.email",
      "email_verified_field": "data.email_verified"
    }
  ]
}
```

## 提供方字段

| 字段 | 说明 |
| --- | --- |
| `id` | 插件内稳定的提供方身份，也是账户绑定命名空间的一部分。 |
| `name` | 登录选项的显示名称。 |
| `preset` | `github`、`google` 或 `custom`，快捷项预填协议默认值。 |
| `disabled` | 停用单个提供方并保留配置。 |
| `protocol` | `oauth2` 或 `oidc`；自定义 OIDC 使用 Discovery。 |
| `issuer` | 稳定的身份来源；OIDC 中必须与 Issuer 精确一致。 |
| `client_id` / `client_secret` | 在提供方登记的客户端凭据。 |
| `scopes` | 请求的权限范围，OIDC 必须包含 `openid`。 |
| `token_auth_method` | `basic`、`post` 或 `none`；使用 `none` 的公开客户端不能配置密钥。 |
| `authorization_endpoint` | 自定义 OAuth2 授权端点。 |
| `token_endpoint` | 自定义 OAuth2 令牌端点。 |
| `userinfo_endpoint` | 自定义 OAuth2 JSON 用户资料端点，使用 Bearer 认证和 GET 请求。 |
| `subject_field` | OAuth2 稳定身份字段的必填路径，例如 `id` 或 `data.id`。 |
| `email_field` | 可选的邮箱字段路径。 |
| `email_verified_field` | 可选的邮箱验证字段路径，只接受 JSON 布尔值 `true`。 |

配置上限为 64 KiB，未知字段和重复提供方 ID 会被拒绝。OAuth2 使用授权码流程与 S256 PKCE。身份标识必须是稳定字符串或 int64 范围整数，不能使用会变化的用户名或邮箱。

自定义 OIDC 将 `protocol` 设为 `oidc`，填写 Issuer、客户端凭据，并在 Scopes 中包含 `openid`。端点来自 Discovery，无需 OAuth2 用户资料字段映射。

## 快捷提供方行为

GitHub 使用 `/user` 返回的稳定数值 ID，以及 `/user/emails` 中已验证的主邮箱。公开资料中的邮箱不足以证明邮箱归属。

Google 使用 OIDC，校验签名、Issuer、Audience、有效期、nonce、`azp`，以及存在时的 `at_hash`。

## 编辑密钥

配置页展示公开参数和密钥是否存在，不回传密钥原文。在该界面中，已有密钥留空表示保留，输入新值表示替换，选择清除则移除。修改客户端、协议、Issuer 或令牌端点后，需要重新填写密钥。

以上行为适用于插件配置编辑器。高级 JSON 更新会替换提交的配置，使用该入口时应保留预期凭据。写入使用版本检查，发生冲突后应刷新并重新应用修改。

## 账户行为

| 情况 | ZBoard 行为 |
| --- | --- |
| 身份已有绑定 | 通过核心账户检查后登录。 |
| 新身份，允许注册，提供已验证邮箱 | 注册普通用户。 |
| 新身份，未提供已验证邮箱 | 在 ZBoard 完成邮箱验证；需要 SMTP，不受密码注册验证码设置影响。 |
| 新身份，禁止注册 | 拒绝该未绑定身份注册和登录。 |
| 邮箱与已有账户相同 | 需要从已有账户显式绑定。 |

绑定和解绑需要账户当前的本地密码。通过外部身份新注册的账户初始没有本地密码，用户可在外部认证完成后的五分钟内到安全设置设置初始密码；该流程不能覆盖已有密码。

每个外部身份只归属一个 ZBoard 账户，一个账户可绑定多个提供方。停用、卸载插件或修改配置会使未完成的登录与注册流程失效，已提交的身份绑定和已有核心会话保留。

旧 `0.1.0` 单提供方配置仍可读取，空提供方 ID 为已有绑定保留；新提供方使用明确 ID。修改提供方 ID 应视为身份命名空间变化。

## 网络要求

提供方端点必须使用公网 HTTPS 443。请求拒绝重定向、环境代理、内网目标和端点查询参数。所有 DNS 结果经过检查，连接使用已验证地址。单响应最多 1 MiB，请求超时八秒；Discovery 元数据缓存五分钟，配置变更后失效。

当前集成不支持内网身份提供方、自定义脚本、任意请求头和非授权码流程。宿主管理一次性 state、PKCE、浏览器绑定和完成票据。宿主重启后需重新授权；多实例部署需将认证流量路由至活动插件宿主。

## 问题排查

| 问题 | 检查内容 |
| --- | --- |
| 回调 URI 被拒绝 | 提供方登记值是否与站点回调 URI 完全一致。 |
| Discovery 或用户资料请求失败 | 公网 HTTPS 可达性和上述网络要求。 |
| 提供方未显示 | 插件与提供方是否都已启用，配置是否已保存。 |
| 新用户无法注册 | 宿主注册设置、邮箱验证状态和 SMTP 配置。 |
| 已有账户无法绑定 | 先登录该账户，再确认本地密码。 |
| 配置检测通过但登录失败 | 用真实客户端凭据和已登记回调 URI 验证完整授权流程。 |

宿主实现细节维护在 [ZBoard 身份契约](https://github.com/zerodenet/zboard/blob/feature/plugin/docs/plugin-identity.md)中。报告与本文不同的行为时，请同时提供宿主和插件版本。
