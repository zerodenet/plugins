# 贡献说明

[English](CONTRIBUTING.md) · **简体中文**

## 登记与更新

使用[登记表单](https://github.com/zerodenet/plugins/issues/new?template=submit-plugin.yml)或[资料更新表单](https://github.com/zerodenet/plugins/issues/new?template=update-plugin.yml)，提交公开固定发行中包含完整原始资料的 `marketplace-entry.json`。支持正式版、RC 和 Dev。自动化校验来源归属、结构、身份、标签/源码及资产大小/摘要后，原子提交原始登记与宿主兼容投影；不要求管理员批准或能力审核。

提交者须为源码仓库所有者，或有可被自动核实的写权限。更新使用当前来源控制权；迁移仓库还须证明旧来源控制权。产品及已有宿主/包 ID 保持稳定。资料错误或不可用标记 `status:needs-info`；成功标记 `status:registered` 并关闭 Issue。来源控制校验防止其他发布者替换既有身份。

## 版本与权限

版本、安装包、兼容声明和更新说明在插件仓库发布。新增权限或界面不需要更新市场登记或批准。市场校验声明结构、保留每个版本的原始声明；接口支持、用户确认与授权由宿主负责。收录不代表安全认证。

实现变更按正常仓库贡献处理。不执行投稿包，不提交秘密，不改写产品资料。中英文参考保持一致。

## 校验

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check
