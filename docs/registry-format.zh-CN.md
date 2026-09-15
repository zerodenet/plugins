# 统一市场契约

[English](registry-format.md) · **简体中文**

市场明确分成三层；任何一层都不能取代宿主安装时的包验证。

## 产品注册

`catalogs/plugins.json` 使用 schema 3，是唯一权威目录来源。首次入驻或资料更新都通过 Issue Template 提交固定发行清单；管理员在该 Issue 添加 `status:accepted` 后，Action 才会把清单中的 `listing` 原样与自动生成的宿主投影一起提交，不另建入驻 PR。不得直接编辑或由站点代码覆盖名称、简介、分类和链接。一个产品保存稳定 `id`、发布者原始资料、仓库、已审核发布者公钥、发行源指针，以及一到两个 `targets`。

可评审的 JSON Schema 位于 [`schemas/`](../schemas/)；`scripts/marketplace_schema.py` 是实际执行的严格边界，还会校验跨文档身份、宿主能力命名空间、迁移约束和不可变产物地址。

每个目标声明 `host`、不可静默改写的 `package_id`，以及已审核的 `surfaces` 和 `capabilities` 上限。单宿主作者只声明一个目标。产品 ID 与 `(host, package_id)` 均唯一；撤回使用显式 `withdrawn: true`。

`catalogs/zboard.json` 和 `catalogs/znet-sink.json` 是自动生成的 schema-v2 兼容投影。使用 `python3 scripts/generate_catalogs.py` 更新，不得独立编辑。

## 作者发布清单

每个 GitHub Release 带一个 `marketplace-entry.json`。schema 1 保存产品 ID、已登记仓库和发布者、源码标签与完整提交，以及唯一发行记录：

- 规范 SemVer、`stable`/`rc`/`dev` 渠道、发布时间和发行说明链接；
- 一到两个宿主目标，包含包 ID、宿主最低版本、可选的排他最高版本、页面与能力；
- 同一 GitHub Release 内的固定产物，包含系统、架构、字节数、SHA-256 与包签名。

发行必须沿用已登记身份并处于各目标能力上限内。生成器读取签名 `.zbplugin` 与 `.zspkg` 的包内身份，计算大小和摘要，但绝不执行包。

## 构建快照

`.generated/marketplace-snapshot.json` 使用 schema 1，将当前注册信息、作者公开发布记录与已校验发行合并，提供快照版本、生成时间、来源新鲜度、产品、目标、版本、兼容范围和产物。`release_feed` 最多保留最近 20 条正式版或预发布动态并标记是否通过市场清单校验；只有目标下的 `releases` 才能进入宿主安装选择。它是派生构建结果，不是第二份人工目录。

单个作者仓库暂时不可用时，构建可保留该产品上次有效版本并标记陈旧；当前注册表中的撤回始终优先，旧缓存不得恢复已撤回产品。
