# 市场自动化

[English](automation.md) · **简体中文**

## 自动登记

`marketplace.yml` 使用默认分支代码处理首次登记和资料更新。发布者 Issue 创建、编辑或重新打开后自动校验、登记；推送/手动校准会重试未关闭的提交。不存在 `status:accepted` 批准门槛或权限审核。

自动化检查公开固定发行清单、提交者来源控制权、标签/源码身份、资产位置、大小和摘要，支持正式版、RC 与 Dev。原样复制 `listing`，原子提交唯一登记和两个宿主投影，标记 `status:registered`、关闭 Issue，并显式触发发布，避免 `GITHUB_TOKEN` 提交抑制后续 push 工作流。错误/不可用资料标记 `status:needs-info`。协作者仍可用 `status:closed` 关闭无效提交；普通自动标签不会递归触发登记。

提交前检查 Issue 正文/作者/类型及 main 未发生变化。迁移仓库自动核实对新旧来源的控制权。不执行安装包。来源控制校验用于防止冒用身份，不审核插件用途、权限或运行行为。

## 发布

`publish-marketplace.yml` 在相关 main 变更、每三小时或手动运行时取得有界发行元数据；来源故障保留上次可用信息，同一快照分别构建 GitHub Pages 和 Cloudflare Pages。权限和界面扩大不会过滤版本，宿主独立校验和授权所选安装包。

Cloudflare Direct Upload 使用 `CLOUDFLARE_ACCOUNT_ID`、`CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_PLUGINS_PROJECT`（默认 `zero-plugins`）。生产域名为 `plugins.zerodenet.org`，GitHub Pages 保留 `/plugins/` 备用路径。宿主请求 `/api/plugins/{host}/{channel}.json` 并本地筛选平台/版本。凭据只存在于 CI，访客请求不逐个访问来源仓库。显式撤回优先于陈旧缓存。
