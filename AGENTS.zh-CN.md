# 仓库指南

[English](AGENTS.md) · **简体中文**

编辑前阅读 README.zh-CN.md、CONTRIBUTING.zh-CN.md 和 docs/governance.zh-CN.md。本仓库负责集中登记、收录和发现，只维护 main。`catalogs/plugins.json` 是唯一维护的产品登记；各宿主目录是自动生成的兼容投影。源码、版本、安装包、兼容元数据和更新说明属于发布者仓库。

保留产品及宿主/包身份和已有条目。能力和界面数组只是说明信息，不是审核上限。登记、权限变化、界面变化和普通发行不需要市场批准。自动校验来源控制权、结构、身份、标签/源码一致性、资产位置、大小和摘要；不执行投稿包、不编造发布者证据。仓库/密钥变化仍校验来源控制权；显式撤回保持有效。

宿主负责包签名校验、API/平台兼容、安装、权限展示和用户确认、运行时授权、生命周期、本地状态和日志。市场收录不代表安全背书或授权；离线导入按宿主自己的信任流程处理。

执行以下校验。保持中英文参考一致，生成快照、站点、安装包和秘密信息不进入 Git。

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check
