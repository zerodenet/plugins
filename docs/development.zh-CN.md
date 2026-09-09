# 注册表开发

[English](development.md) · **简体中文**

使用 Python 3.10 或更高版本。校验仅依赖标准库，不安装或构建收录插件。

```sh
git clone git@github.com:zerodenet/plugins.git
cd plugins
git switch -c feat/plugin-submission
python3 -m unittest discover -s tests
python3 scripts/validate.py
```

参照[格式说明](registry-format.zh-CN.md)编辑宿主目录。示例放在 `templates/`，拒绝用例放在 `tests/`，可执行检查放在 `scripts/`。正式条目必须指向真实源码提交及发行版本。Actions 在 main 推送和 PR 时以只读仓库权限运行相同检查，并额外调用 `python3 scripts/validate.py --base <完整提交号>` 保护既有发行记录及发布者身份。

开发 OAuth 请克隆 [higanbana986/zboard-oauth](https://github.com/higanbana986/zboard-oauth)并遵循其开发指南。宿主 API 改动属于宿主仓库；本注册表不包含插件构建工作区或共享运行时。
