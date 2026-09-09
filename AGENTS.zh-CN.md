# 仓库指南

[English](AGENTS.md) · **简体中文**

修改前阅读 `README.md`、`CONTRIBUTING.md` 和 `docs/governance.md`。本仓库是元数据注册表，唯一持续维护的分支为 `main`。源目录为 `catalogs/zboard.json` 与 `catalogs/znet-sink.json`；插件源码、构建流程和安装包属于独立仓库。

保留插件 ID 和既有发行记录。不得把插件运行时或 SDK 复制进市场、执行提交的安装包、自动信任提交的公钥，或编造发行元数据。只有源码的条目必须使用空发行数组。授权、核心状态和生命周期事务由宿主管理。

运行 `python3 -m unittest discover -s tests`、`python3 scripts/validate.py` 和 `git diff --check`。校验规则改动需补充针对性的拒绝用例。同步中英文文档并检查本地 Markdown 链接。生成产物和密钥不得跟踪。

遵循当前检出目录要求的 Git 作者及提交者身份。保持 `main` 线性历史，并在目标仓库保留已迁移源码的历史。不得将注册表源文件描述为签名宿主目录，也不得以交叉编译代替平台运行验证。
