# 插件开发规范

## 目录与依赖

本仓库采用 `<host>/<plugin>/` 布局。当前 Go 模块是 `github.com/zerodenet/plugins/zboard/oauth`，插件 ID 仍为 `zboard.oauth`。模块路径与安装身份各司其职，迁移源码不得改变已有用户绑定的命名空间。

依赖只通过宿主公开 SDK 接入，使用 `go.mod` / `go.sum` 锁定版本，不导入宿主 internal 包，不提交本机路径 replace。当前 OAuth SDK 依赖固定的 ZBoard 提交，要求支持多提供方身份协议的宿主；仅比较展示版本号不足以证明协议可用。

## 本地验证

需要 Go 1.26.8、Node.js 18+；打包另需 Python 3。

```sh
sh scripts/check.sh
```

检查默认 `GOWORK=off`，避免本地宿主修改掩盖已锁定 SDK 的兼容性。联合开发可以在 `zboard/oauth/` 创建被忽略的 workspace，再显式传入：

```sh
cd zboard/oauth
go work init . /absolute/path/to/zboard/backend
GOWORK="$PWD/go.work" ./scripts/check.sh
```

提交前再次使用默认检查入口验证锁定依赖。修改配置、身份交换、网络行为或页面桥时，补充对应行为测试；不能只测试正常路径，需覆盖拒绝和失败后的状态。

## 本地打包

准备包含 `backend/tools/pluginpackager` 的 ZBoard 检出目录，然后从插件目录运行：

```sh
python3 scripts/package.py --zboard /absolute/path/to/zboard --dev-key --platform linux-amd64
```

也可设置 `ZBOARD_DIR`。插件构建使用自己的模块，宿主打包器使用宿主模块；不要隐式依赖目录相邻关系。开发私钥位于插件的 `.local/`，制品位于 `dist/`，都不会进入版本跟踪。开发签名只能用于测试。

新增插件至少提供：稳定 ID、宿主和版本约束、能力及入口声明、配置说明、秘密值处理、数据/迁移契约、验证脚本和平台验收结果。宿主未提供的能力不得通过任意脚本、数据库连接或自定义通用命令补齐。
