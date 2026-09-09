# 市场自动化

[English](automation.md) · **简体中文**

市场根据已公开的 GitHub Release 提议更新目录，不重新编译插件、不执行安装包、不代替发布者签名，也不自动合并自己的 PR。

## 收录申请

将 `marketplace-entry.json` 与签名安装包一同发布，在申请表中填写固定的 GitHub Release 产物链接。已有申请正文中的同类链接也可识别。工作流校验发行信息后生成目录 PR；编辑申请会重新校验，机器人维护同一条状态评论，避免重复刷屏。

元数据只描述一个版本，仓库、版本、源码提交必须与实际发行及标签一致，支持解析附注标签。每个包的 URL、SHA-256 和大小必须与该次 Release 中的产物记录一致。元数据下载限定 GitHub HTTPS 发行托管域名，最大 256 KiB。带写权限的工作流不检出或执行贡献者代码。

这些检查证明元数据与 GitHub 发行记录一致。合并前，维护者仍须核验发布者及公钥归属、安装包签名、所需能力、迁移行为及实际宿主测试证据。提交公钥不授予信任。目录 PR 使用 squash 或 rebase 合并，保持 `main` 线性历史。

## 标签

定义见 [.github/labels.json](../.github/labels.json)。工作流自动创建缺失标签并同步颜色和说明，保留无关标签。

| 标签 | 含义 |
| --- | --- |
| `plugin:submission` | 首次收录或提交的发行版本 |
| `plugin:update` | 定时检查发现的发行更新 |
| `host:zboard`、`host:znet-sink` | 根据有效元数据识别的宿主 |
| `status:needs-info` | 申请元数据缺失或有误 |
| `status:in-review` | 已生成目录 PR，等待审核 |
| `status:accepted` | PR 已合并，或版本已存在于主分支目录 |
| `status:closed` | 申请或提议已关闭，未收录 |

标签描述流程状态，手工添加 `status:accepted` 不会写入目录，也不能批准宿主安装。准备 PR 前会重新读取申请正文。合并后仅在关联申请正文仍与记录一致时关闭申请，或由后续对账核实其版本已被收录后关闭。

## 上游更新

每 6 小时检查已有发行记录和发布者公钥的插件仓库，读取最新稳定版 GitHub Release。只有源码的条目不会自动收录。发现新版本后单独生成 PR，并追加到原有发行历史；插件 ID、宿主、仓库、公钥变化以及既有版本的产物变化会被拒绝。

每个插件及版本使用固定提议分支，多次运行复用同一个 PR。被关闭的提议不会静默重开，解决审核反馈后由维护者手动重开。如果两次扫描间发布了多个版本，自动提议最新稳定版；中间版本可逐个提交申请。

工作流也在 `main` 更新后运行，并支持从 **Actions → Marketplace synchronization → Run workflow** 手动启动。自动提交使用 `github-actions[bot]` 身份。OAuth 仓库无需配置跨仓库 Token；首次收录后，只需随 Release 发布元数据即可被定时发现。

## 仓库设置

启用 **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**。工作流仅申请仓库内容、Issue 和 PR 写权限，不会批准 PR。组织策略可能控制此设置。权限不足会使 Action 失败，不会把有效申请误标为资料错误。

GitHub 可能要求维护者批准由 `GITHUB_TOKEN` 创建的 PR 检查，请查看 PR 上的工作流提示，参见 [GitHub 触发规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。本实现不需要个人访问 Token。

## 安装目录

PR 合并后更新 `catalogs/zboard.json` 或 `catalogs/znet-sink.json`，它们仍是源目录。宿主签名安装目录的发布及续签需要独立的市场签名密钥和分发流程；本工作流不会将源 JSON 直接变成可安装目录。
