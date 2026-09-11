# 仓库规范

[English](AGENTS.md) · **简体中文**

编辑前阅读 README.md、CONTRIBUTING.zh-CN.md 和 docs/governance.zh-CN.md。本仓库是精选准入与发现目录，只维护 main 分支。插件源码、发行历史、安装包、兼容元数据和更新说明属于开发者自己的仓库。

保留插件 ID 和既有条目。目录只保存稳定身份、发布者公钥、仓库资料与发行源入口、宿主范围以及审核过的能力和界面上限。不得在此加入常规正式版、RC 或 Dev 发行记录，不执行提交的安装包，也不编造发布者证据。仓库、密钥或源契约变更、能力扩大及撤回需要专门审核。

在线发行发现、频道与版本选择、校验、安装、升级、降级、移除、本地状态及审计由宿主管理。离线导入继续作为管理员明确授权的独立通道。

运行 python3 -m unittest discover -s tests、python3 scripts/validate.py 和 git diff --check。中英文指南同步维护，生成产物和秘密不得跟踪。
