# 市场自动化

[English](automation.md) · **简体中文**

入驻与公开发布由两条独立流程负责。

`marketplace.yml` 处理首次入驻和已登记资料更新。它只运行已审核的 `main` 代码，校验一个正式 `marketplace-entry.json`、GitHub 标签/源码与产物记录，并把申请 Issue 标记为 `status:in-review`。管理员在同一个 Issue 内审核发布者/密钥归属、包签名、每个宿主目标与能力上限，以及真实运行证据。添加 `status:accepted` 就是批准决定：Action 会重新校验固定发行，并用一次原子提交把原样 `listing` 和两个自动生成的宿主兼容投影一起写入 `main`，随后显式触发 Pages 发布工作流。这里使用 `workflow_dispatch`，避免自动化提交所用的 `GITHUB_TOKEN` 抑制后续 `push` 工作流。添加 `status:closed` 则关闭申请且不予收录。入驻流程不再创建独立分支或 PR。名称、简介、分类、链接及其他产品字段不经过翻译、改写或缺省推断，流程也绝不执行投稿包。

GitHub 只允许具备相应仓库角色的协作者管理标签；工作流仅把真人触发的两个决定标签视为管理操作。编辑、重新打开、机器人标签、推送和手动校准都只能重新验证，不能批准。Issue 正文发生变化后，批准标签会被移除，必须由管理员重新审核并再次添加。写入前还会确认 Issue 与 `main` 均未发生变化，并发冲突会关闭写入而不是覆盖。

`publish-marketplace.yml` 在注册/网站变化、每三小时或人工触发时运行。它校验注册表，在构建期有界读取作者发行，作者仓库暂时失败时复用该产品上次有效数据，再从同一快照分别构建 GitHub Pages 仓库路径版本和 Cloudflare Pages 根路径版本。网站、市场快照、API 和 schema 保持同一次运行、同一快照版本。

Cloudflare Direct Upload 使用组织级 `CLOUDFLARE_ACCOUNT_ID` 与 `CLOUDFLARE_API_TOKEN`。项目名公开固定为 `zero-plugins`；工作流优先读取 `CLOUDFLARE_PLUGINS_PROJECT` Secret 或 Variable，并在未配置时使用该固定值。Token 只需目标账号的 Cloudflare Pages 编辑权限。GitHub Pages 继续发布 `/plugins/` 路径，作为独立备用地址。

正式域名 `plugins.zerodenet.org` 绑定到 Cloudflare Pages 项目，宿主读取 `/api/plugins/{host}/{channel}.json`，再在本地按版本与平台筛选；既有 schema-v2 地址仅作迁移期只读回退。未来若引入 Worker，它是可选增强，不是静态市场可用性的前置条件。

GitHub 凭据只存在于构建任务；访客浏览不会逐个请求作者仓库。入驻提交只会在 Issue 标签审核决定后产生，普通市场发布仍由另一条工作流负责。显式撤回仍先于陈旧缓存处理。
