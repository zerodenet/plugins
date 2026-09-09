# 注册表格式

[English](registry-format.md) · **简体中文**

源注册表采用 schema version `1`。它是仓库编辑格式，与 ZBoard 签名目录 v1 及拟议的共享分发 v2 分开。实际校验器见 [scripts/validate.py](../scripts/validate.py)。

## 宿主目录

`catalogs/zboard.json` 与 `catalogs/znet-sink.json` 包含 `schema_version`、`host` 和 `plugins`。宿主值必须与文件名一致。同一插件 ID 在一个宿主目录内只出现一次。同一项目可以为不同宿主分别发布产物；一个宿主的能力不能授权另一个宿主。

## 插件条目

| 字段 | 含义 |
| --- | --- |
| `id`、`name`、`description` | 稳定的包标识与发现信息 |
| `repository` | 公开 GitHub 源码仓库 |
| `license`、`maintainers` | 许可证标识与负责维护者 |
| `publisher.id` | 稳定的安装包签名密钥标识 |
| `publisher.public_key` | Base64 Ed25519 公钥，仅在尚无发行版本时允许为 `null` |
| `source.version`、`source.commit`、`source.manifest` | 当前源码版本、完整 Git SHA 及清单相对路径 |
| `releases` | 不可变发行记录，空数组表示仅有源码 |

源版本采用带 `v` 前缀的发行标识。ZBoard 安装包清单与运行时握手继续使用其协议要求的不带前缀的语义版本。例如市场发行 `v0.0.1` 对应包版本 `0.0.1`。

## 发行与产物

每个发行记录包含 `version`、`source_commit`、`requires`、`surfaces`、`capabilities` 和 `artifacts`。`requires` 包含所属宿主键及宿主/API 兼容要求。ZBoard 发行还须声明正整数 `plugin_protocol` 与 `ui_bridge` 版本。可选的宿主推荐版本与已测试版本应从签名清单复制。

每个产物包含 `platform`、`url`、`sha256` 与字节数 `size`。平台名称支持 `linux-amd64`、`linux-arm64`、`darwin-amd64`、`darwin-arm64`、`windows-amd64` 和 `any`。`any` 表示确实与平台无关的包，不能与专属平台产物混用。地址必须是固定 HTTPS 地址，不得携带凭据、查询参数或片段。ZBoard 安装包使用 `.zbplugin`；当前注册表限制单个压缩产物最大 32 MiB。

## 更新条目

新增版本时保留已有版本的包字节及摘要。新增权限或发布者公钥变更须明确审核。密钥轮换和签名撤回记录不属于源格式 v1；不得静默替换旧版本使用的公钥。紧急撤回通过安全报告协调目录排除与宿主处置。

源目录 CI 检查结构与内部一致性。维护者仍需独立核实源码引用、安装包字节、签名及发布者归属。条目中的公钥是审核资料，不是宿主信任根。
