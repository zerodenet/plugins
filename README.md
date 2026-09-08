# ZBoard OAuth 登录插件

通过 OIDC 身份提供方登录 ZBoard。插件 ID：`zboard.oauth`。包含后台配置页面与动态服务进程，支持签名离线导入、启停、配置替换和提供方检测。

**登录是宿主核心的业务。** 插件只验证提供方身份并返回 Issuer / Subject；核心负责浏览器 state、账号绑定、状态检查、审计及 ZBoard 会话签发。插件不读写用户表，不按邮箱自动合并账号，不修改节点凭证，也不直接通知节点。

## 使用

1. 在 ZBoard “站点与品牌”设置准确的公开 HTTPS 根地址。本地开发可用 `http://127.0.0.1:<端口>`。
2. 在 OIDC 提供方创建客户端，精确登记回调：`https://你的站点/api/v1/auth/oidc/callback`。使用授权码流程及 S256 PKCE。
3. 将发布者公钥加入测试或生产宿主的 `plugins.trusted_publishers`，导入对应服务器平台的 `.zbplugin` 包。
4. 在插件管理中打开配置页，完整填写 Issuer、Client ID、Client Secret（公开客户端可留空）与 scopes，保存并检测，然后启用插件。
5. 用户首次使用时，先通过邮箱密码登录，在“账户安全”确认当前密码并绑定第三方账号。后续可从登录页直接第三方登录。

未绑定的身份不能直接登录或自动注册。新用户仍走 ZBoard 既有注册流程；同邮箱不会自动绑定，管理员权限只取自核心用户记录。停用插件会阻止未完成的登录；已提交绑定和既有核心会话不删除。解绑由核心处理，即使插件已经卸载也可以操作。

目前支持提供标准 OIDC discovery 的提供方。GitHub OAuth App 等只有 OAuth 2.0、没有 OIDC 身份令牌的服务不在本版本支持范围内。需要登记真实客户端信息后，才能验收实际账号授权。

## 配置

```json
{
  "issuer": "https://accounts.example.com/realm",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "scopes": ["openid", "profile", "email"]
}
```

Issuer 必须与 discovery 文档完全一致，包括末尾斜杠；检测地址为 Issuer 去掉末尾 `/` 后追加 `/.well-known/openid-configuration`。scopes 最多 16 个，必须含 `openid`，默认 `openid profile email`。

配置由宿主加密保存。保存是带 revision 的完整替换，宿主不回显任何已保存字段；更新时需要重新填写，secret 留空表示清除旧密钥。保存失败或超时后先刷新状态。初始 `{}` 可应用，但不能用于登录或检测。ApplyConfig 没有网络或核心业务副作用，允许宿主回滚旧 revision。

检测只读取元数据，不发送客户端密钥。它检查端点、Issuer、授权码流程、subject 类型、签名算法、scopes，以及显式声明的 S256 支持；不等于客户端密钥有效或实际登录成功。PKCE 元数据未声明时，实际授权仍始终使用 S256。

## 网络与身份校验

提供方网络请求仅支持公网 HTTPS 443，不使用环境代理、不跟随重定向。DNS 解析后连接经过检查的固定 IP，混合私网/公网答案也拒绝；响应最多 1 MiB，单次请求最多 8 秒。带查询参数、fragment 的端点及内网 IdP 暂不支持。这些是当前插件的部署限制。

元数据按配置缓存五分钟，变更配置立即清除。授权码交换通过 `golang.org/x/oauth2` 发送 PKCE verifier；使用 `coreos/go-oidc/v3` 验证签名、Issuer、Audience、到期时间，再检查 nonce、非空 Subject、azp 和存在时的 at_hash。只接受 RS256 / ES256；Client Secret 仅发送到配置提供方的 Token 端点，提供方令牌不返回浏览器或写入日志。

核心授权状态五分钟到期，完成票据一分钟到期，都只能使用一次并绑定浏览器。核心在身份提交和会话签发时核验插件发布者、generation、config_revision 和活动宿主租约。核心重启会使未完成登录失效；多实例入口需要将认证流量路由到活动插件宿主。

## 独立仓库与构建

本目录 `zboard/plugins/oauth/` 拥有独立 `.git/`；父仓库忽略 `/plugins/`。这是源码目录，运行时安装目录继续使用宿主 `data/plugins/` 或部署路径，不能与源码混用。

需要 Go 1.26.8、Python 3 和 Node.js 18+。仅导入公开 SDK `backend/pkg/pluginapi/v1`，不导入宿主 `internal`。当前需要包含 `zboard.identity.provider.v1` 的 ZBoard `feature/plugin` 或后续兼容版本；只有页面/配置能力的旧宿主会拒绝安装。

```sh
# 插件目录内，独立模块运行
GOWORK=off ./scripts/check.sh

# 与邻接宿主源码同时开发时，使用被忽略的本地工作区；已有文件不重复初始化
go work init . ../../backend
```

`check.sh` 执行配置与 SSRF 边界、签名 ID Token 校验、race、vet、真实 gRPC 子进程握手/配置/重启，以及沙箱消息桥与配置保存测试。核心的绑定/登录、重放、账号停用和热拔插测试在 ZBoard 后端中。

## 离线包

使用宿主官方打包器，按平台单独生成包，包内只有 manifest、签名、UI 和对应可执行文件。

```sh
# 本机开发包；密钥保存在忽略的 .local/，不会自动加入宿主信任
python3 scripts/package.py --dev-key

# Linux 服务端
python3 scripts/package.py --dev-key --platform linux-amd64
python3 scripts/package.py --dev-key --platform linux-arm64

# 维护者签名；源码移到别处时指定宿主工具位置
python3 scripts/package.py --zboard /path/to/zboard \
  --key /secure/publisher.key --key-id your-publisher --platform linux-amd64
```

产物：`dist/zboard.oauth-0.1.0-<平台>.zbplugin`。开发公钥：`.local/publisher.key.pub`，对应发布者 ID 为 `oauth-local-dev`。不要将开发私钥用于生产发布。私钥、构建产物、开发配置和 `go.work` 均不进入版本跟踪，本仓库没有预设远程地址。

macOS 开发包尚未完成稳定运行验收：本机完整导入、配置、启停流程曾通过，但重复启动出现宿主 10 秒超时，随后系统日志记录同一插件进程被 Gatekeeper 拒绝。包的 Ed25519 发布者签名不替代 Apple 代码签名或公证；本脚本未执行 Apple 签名或公证。Linux 包已完成交叉构建和包校验，仍需在目标部署环境验证运行。

协议参考：[OIDC Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)、[OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html)、[OAuth Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html)、[PKCE](https://www.rfc-editor.org/rfc/rfc7636.html)。核心契约见宿主 `docs/plugin-identity.md`。
