# ZBoard 第三方登录与注册插件

插件 ID：`zboard.oauth`，版本 `0.2.0`。让 ZBoard 作为 GitHub、Google 或自定义 OAuth2 / OIDC 的客户端，通过第三方授权登录和注册账户。一个插件可同时配置最多 16 个提供方，并独立启停。

**核心管理账户。** 插件只交换授权码、读取或校验第三方身份，返回稳定 Subject、Issuer、邮箱及邮箱验证标志。注册开关、用户唯一性、权限、绑定、审计和 ZBoard 会话均归核心；插件不读写用户表、修改节点凭证或通知节点。

## 配置与使用

1. 在 ZBoard “站点与品牌”设置公开 HTTPS 根地址，在各提供方登记回调 `https://你的站点/api/v1/auth/oidc/callback`。本地开发允许 `http://127.0.0.1:<端口>`。
2. 将发布者公钥加入宿主 `plugins.trusted_publishers`，导入匹配服务器平台的签名 `.zbplugin` 包。
3. 在插件配置页点击“添加 GitHub”“添加 Google”或“添加自定义”。提供方标识保存后不可在页面修改；名称用于登录按钮。
4. GitHub、Google 快捷项预填协议、地址、Scopes 和字段规则，运营者主要填写 Client ID / Secret。自定义项填写下述协议参数。
5. 保存并检测，启用插件。登录页和注册页分别出现已启用提供方入口。检测验证配置，OIDC 还读取元数据；它不验证真实客户端授权。

公开字段可回读编辑，Client Secret 不回显。已存在密钥时，留空保留；输入新值替换，勾选清除则移除。修改客户端、协议、Issuer 或令牌地址后必须重新填写密钥。保存带 revision，冲突需刷新重试。删除某个提供方不会删除核心已有账户或绑定，但会关闭该提供方登录。

## 注册与绑定

- 已绑定身份直接登录。新身份在核心允许注册时创建普通用户，不授予管理员权限。
- 提供方返回有效的已验证邮箱时自动注册；没有已验证邮箱时，在 ZBoard 完成页补充邮箱并验证验证码。此路径需要站点配置 SMTP，不依赖普通密码注册的验证码开关。
- 同邮箱已有账户不会自动合并。先使用原方式登录，再到“账户安全”确认本地密码后绑定。
- 第三方注册账户初始没有本地密码；第三方登录后五分钟内可在账户安全设置初始密码。已有密码不能被此接口覆盖。
- 绑定和解绑都需要当前本地密码。每个用户可分别绑定多个提供方；每个外部身份只能归属一个用户。
- 停用、卸载、配置修改使未完成的登录/注册失效，保留已提交的绑定与既有核心会话。

## 自定义 OAuth2 / OIDC

OAuth2 授权本身不定义统一用户身份结构，因此自定义 OAuth2 还需配置用户资料接口和稳定 ID 字段。支持授权码流程与 S256 PKCE，Token 端点支持 HTTP Basic、POST 表单或公开客户端认证。用户资料请求使用 Bearer Token 和 GET，返回 JSON。

```json
{
  "providers": [
    {"id":"github","preset":"github","client_id":"YOUR_GITHUB_CLIENT_ID","client_secret":"YOUR_SECRET"},
    {"id":"google","preset":"google","client_id":"YOUR_GOOGLE_CLIENT_ID","client_secret":"YOUR_SECRET"},
    {
      "id":"company","name":"公司账号","preset":"custom","protocol":"oauth2",
      "issuer":"https://identity.example.com",
      "authorization_endpoint":"https://identity.example.com/oauth/authorize",
      "token_endpoint":"https://identity.example.com/oauth/token",
      "userinfo_endpoint":"https://identity.example.com/api/me",
      "client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_SECRET",
      "token_auth_method":"basic","scopes":["profile","email"],
      "subject_field":"data.id","email_field":"data.email","email_verified_field":"data.email_verified"
    }
  ]
}
```

字段路径支持 `id`、`sub`、`data.id` 等点分对象路径；ID 必须是稳定字符串或 int64 范围整数，不能使用可变用户名或邮箱。邮箱验证只接受 JSON 布尔值 `true`。没有验证字段时不能声称邮箱已验证，由核心补充验证。

自定义 OIDC 使用 `protocol: "oidc"`、精确 `issuer`、客户端信息和包含 `openid` 的 scopes，通过标准 discovery 获取端点，不需要 OAuth2 的用户字段映射。

GitHub 快捷项使用授权码、`/user` 的稳定数值 ID，以及 `/user/emails` 的 primary+verified 邮箱；不会信任公开资料中的 email 字符串。Google 使用 OIDC，校验签名、Issuer、Audience、到期时间、nonce、azp 和存在时的 at_hash，再读取邮箱声明。

旧 `0.1.0` 单提供方 OIDC 配置可读取；保留空 provider ID 作为旧绑定的命名空间。新提供方使用独立稳定 ID，不能将其改名当作普通展示名称修改。

## 网络与状态边界

提供方网络仅允许公网 HTTPS 443，拒绝重定向和环境代理。DNS 解析检查所有地址并固定连接到已检查 IP；单响应最多 1 MiB、请求最多 8 秒，元数据缓存五分钟且配置修改时失效。暂不支持内网 IdP、端点查询参数、自定义脚本、任意请求头或非授权码流程。

核心维护单次 state、PKCE、浏览器绑定和完成票据，插件不能选择宿主用户 ID 或会话权限。初始密码设置要求刚完成授权的核心证明。宿主重启需重新授权；多实例需将认证流量送到活动插件宿主。

## 独立仓库与验证

`zboard/plugins/oauth/` 有独立 `.git/`；父仓库忽略 `/plugins/`。源码目录与运行时安装目录（例如 `data/plugins/`）分离。仓库不预设远程地址。

需要 Go 1.26.8、Python 3、Node.js 18+，只依赖公开 SDK `backend/pkg/pluginapi/v1`。本版本需要支持多提供方、配置投影和核心注册的宿主，旧页面/配置或单 OIDC 宿主不能完整承载它。

```sh
GOWORK=off ./scripts/check.sh
# 联合开发时可使用被忽略的 go.work：
go work init . ../../backend
```

检查包含配置与网络边界、真实签名 ID Token、GitHub / 自定义 OAuth2 协议 fixture、保留密钥、race、vet、真实 gRPC 进程和页面消息桥测试。实际第三方授权仍需要运营者登记的 Client ID、Secret 和回调地址。

## 离线包

```sh
python3 scripts/package.py --dev-key --platform linux-amd64
python3 scripts/package.py --dev-key --platform linux-arm64
python3 scripts/package.py --dev-key
# 正式发布使用维护者密钥；源码不在邻接目录时指定宿主打包器
python3 scripts/package.py --zboard /path/to/zboard --key /secure/publisher.key --key-id your-publisher --platform linux-amd64
```

产物 `dist/zboard.oauth-0.2.0-<平台>.zbplugin`。开发公钥 `.local/publisher.key.pub`，ID `oauth-local-dev`；脚本不自动信任该密钥。私钥、开发配置、构建产物和 go.work 不进入版本跟踪。

macOS 开发包此前完整导入、配置、启停曾通过，但重复启动出现宿主 10 秒超时，随后同一 PID 被 Gatekeeper 拒绝；未完成稳定平台验收。包的 Ed25519 签名不替代 Apple 代码签名或公证。Linux 包可交叉构建，仍需目标部署环境验证。不要通过关闭系统安全策略验收。

参考：[GitHub OAuth](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)、[GitHub 邮箱 API](https://docs.github.com/en/rest/users/emails)、[Google OIDC](https://developers.google.com/identity/openid-connect/openid-connect)、[OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html)、[PKCE](https://www.rfc-editor.org/rfc/rfc7636.html)。核心契约见宿主 `docs/plugin-identity.md`。
