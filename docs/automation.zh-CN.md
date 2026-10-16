# 市场自动化

[English](automation.md) · **简体中文**

插件收录在 Issue 中完成审核。作者发布自己的安装包并提交发行链接，维护者通过标签批准申请，Action 随后更新 `main` 上对应的目录。首次收录和发行更新均不要求提交目录 PR。

## 提交与审核

1. 在公开的 GitHub Release 中同时发布签名安装包和 `marketplace-entry.json`，然后填写[申请表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)。
2. Action 校验元数据，自动添加申请类型、宿主和审核状态标签，并在同一条机器人评论中记录审核指纹。资料有误时标记 `status:needs-info`，作者编辑 Issue 后重新校验。
3. 维护者核验发布者及公钥归属、包签名、能力、迁移行为和实际宿主测试证据，完成后添加 `status:approved`。批准人须具有仓库 write、maintain 或 admin 权限，triage 权限不足以批准收录。
4. Action 重新获取并校验发行，与审核指纹比对后，只提交对应宿主目录的变更。成功后将批准标签替换为 `status:accepted` 并关闭 Issue。提交记录保留申请编号、批准人和审核指纹。

元数据只能描述一个版本，仓库、版本和源码提交须与实际发行及标签一致，支持附注标签。包 URL、SHA-256 和大小须与该次 Release 的产物记录一致。元数据下载限定 GitHub HTTPS 发行托管域名，最大 256 KiB。工作流只检出已经审核的 `main` 代码，不编译或执行申请中的插件包。

审核指纹绑定申请正文及已校验的发行元数据。编辑或重新打开申请会回到待审核状态；发行产物发生变化，或审核快照晚于批准事件时，也必须重新批准。目录写入前观察到批准标签被撤销或 Issue 被关闭，会停止发布。GitHub 的 Issue 状态与 Git 提交属于不同 API 操作，写入之后的撤销不会回滚目录。

## 标签

定义见 [.github/labels.json](../.github/labels.json)。Action 同步颜色和说明，保留无关标签。

| 标签 | 含义 |
| --- | --- |
| `plugin:submission` | 首次收录或提交的发行版本 |
| `plugin:update` | 定时检查发现的新版 |
| `host:zboard`、`host:znet-sink` | 根据有效元数据识别的宿主 |
| `status:needs-info` | 资料需要修正，或批准人不具备审核权限 |
| `status:in-review` | 已通过自动校验，等待维护者审核 |
| `status:approved` | 维护者审核通过，触发目录发布 |
| `status:accepted` | 发行已写入 `main` |
| `status:closed` | 申请已关闭但未收录 |

`status:approved` 表示审核决定，`status:accepted` 表示落库结果。手工添加 `status:accepted` 不会发布目录。两个标签均不授予宿主内的权限，也不会自动信任发布者公钥。

## 上游更新

每 6 小时检查已有发行记录和发布者公钥的插件仓库，读取最新稳定版 GitHub Release。发现新版后创建审核 Issue，继续走同一套批准流程。只有源码的条目不参与自动发现。插件 ID、宿主、仓库、公钥变更以及既有版本产物变更会被拒绝。

同一仓库及版本已有作者申请或已关闭申请时，不重复创建，也不会自动重开被拒绝的申请。两次扫描间出现多个版本时只提议最新稳定版，中间版本可分别提交申请。

推送到 `main` 或从 **Actions → Marketplace synchronization → Run workflow** 手动启动，也会检查待处理申请和上游发行。这些扫描不会将已有批准标签当作新的批准事件。发布者无需配置可访问市场仓库的 Token。

## 权限与恢复

工作流申请 `contents: write` 和 `issues: write`，不需要 PR 权限或允许 Actions 创建 PR 的设置。目录写入使用 `GITHUB_TOKEN`，须符合仓库和组织规则。如果 `main` 强制所有变更通过 PR，维护者需先选择允许这条已审核发布路径的仓库策略或获授权的自动化身份。脚本不会修改分支保护，也不会绕过被拒绝的写入。

写入被拒、API 故障或目录并发冲突会使 Action 失败，申请保持打开。检查失败日志并解决原因后，重跑该批准任务，或移除再添加 `status:approved`。重复执行已完成的目录写入不会重复追加版本。申请或审核快照发生变化时，须重新审核并添加新的批准标签。

工作流使用 `queue: max` 串行处理，最多保留 100 个等待事件，超过上限时 GitHub 会取消额外任务。批准任务被取消时可重新添加批准标签，详见 [GitHub 并发规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)。目录写入携带原文件 SHA，防止覆盖并发修改。

使用 `GITHUB_TOKEN` 产生的提交不会再次触发 push 工作流，所以本 Action 在写入前完成校验；机器人创建的更新 Issue 也在同一次任务中校验。详见 [GitHub 触发规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。

## 既有提议与安装目录

旧自动化 PR 不再参与此工作流。尚未收录的版本应在申请 Issue 中完成审核和批准，再由维护者关闭被替代的 PR。工作流不会删除分支或关闭无关 PR。

发布更新 `catalogs/zboard.json` 或 `catalogs/znet-sink.json`，它们仍是源目录。宿主签名安装目录使用独立市场密钥和分发流程。市场批准不能替代宿主的安装包校验、信任决定与生命周期控制。
