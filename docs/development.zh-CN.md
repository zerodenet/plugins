# 开发指南

[English](development.md) · **简体中文**

当前文档适用于 `zboard` 分支。克隆时使用 `git clone --branch zboard https://github.com/zerodenet/plugins.git`，实现 PR 指向 `zboard`。平台文档位于 [main](https://github.com/zerodenet/plugins/blob/main/README.zh-CN.md)。

## 仓库结构

```text
zboard/oauth/        OAuth 插件：Go 服务、界面、测试和打包脚本
scripts/check.sh    仓库检查入口
.github/workflows/  持续集成
docs/               使用指南、贡献者指南和提案
```

插件源码按 `<host>/<plugin>/` 组织，各自维护依赖文件、manifest 和测试。OAuth 的模块路径为 `github.com/zerodenet/plugins/zboard/oauth`，安装标识为 `zboard.oauth`。

宿主实现和 SDK 留在各自仓库。插件使用公开 SDK 并锁定依赖版本；本地路径替换放在不跟踪的开发 workspace 中。

## 环境要求

| 工具 | 要求 | 用途 |
| --- | --- | --- |
| Go | 1.26.8 工具链 | 构建、race 测试和 vet |
| Node.js | 18 或更新版本 | 界面和消息桥测试 |
| Python | 3 | 组装插件包 |
| ZBoard 源码 | 包含 `backend/tools/pluginpackager` 和兼容插件 API 的版本 | 包签名与宿主集成 |

OAuth 的 `go.mod` 固定了 SDK 依赖。宿主需实现其多提供方身份 API、配置投影和注册流程。兼容性同时取决于这些 API 与 manifest 的版本约束。

## 运行检查

从仓库根目录运行：

```sh
sh scripts/check.sh
```

检查脚本包含 Go 格式检查、race 测试、vet、服务构建、真实 gRPC 插件进程测试，以及界面和消息桥测试。默认使用 `GOWORK=off`，验证 `go.mod` 中记录的依赖。

联合开发宿主与插件时：

```sh
cd zboard/oauth
go work init . /absolute/path/to/zboard/backend
GOWORK="$PWD/go.work" ./scripts/check.sh
```

提交前再次运行默认检查，确认本地 SDK 修改没有掩盖依赖兼容问题。

## 构建开发包

在 `zboard/oauth/` 中运行：

```sh
python3 scripts/package.py --zboard /absolute/path/to/zboard --dev-key --platform linux-amd64
```

可用 `ZBOARD_DIR` 代替 `--zboard` 提供宿主路径。脚本使用插件模块构建二进制，使用宿主模块执行打包器，生成 `dist/zboard.oauth-0.2.0-linux-amd64.zbplugin`。开发密钥保存在 `.local/`，发布者 ID 为 `oauth-local-dev`。

支持的构建目标为 `linux-amd64`、`linux-arm64`、`darwin-amd64`、`darwin-arm64` 和 `windows-amd64`。省略 `--platform` 时使用本地 Go 平台。目标构建验证编译结果，安装和运行还需在目标平台测试。

仅测试宿主应信任开发密钥。生产签名方式见[发布指南](publishing.zh-CN.md)。

## 验证集成

将包安装到测试宿主，验证配置、启用、停用、升级和卸载。认证集成应使用已登记的提供方应用，检查登录、注册策略和账户绑定，并记录宿主提交、插件版本、平台和未完成的检查。

行为测试应覆盖成功操作、非法输入、超时和失败后的状态。协议 fixture 和测试凭据与打包的界面及运行文件分别存放。
