# 目录开发

[English](development.md) · **简体中文**

使用 Python 3.10 或更高版本。校验仅依赖标准库，不安装或构建已收录插件。

运行：

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    git diff --check

参照[格式说明](registry-format.zh-CN.md)编辑宿主目录。目录示例放在 templates，拒绝用例放在 tests，可执行检查放在 scripts。正式目录条目只包含准入元数据；发行样例只存在于入驻自动化测试，因为开发者发行不会复制到市场。

发行发现与管理能力属于宿主仓库；插件构建、安装包和发行元数据属于插件仓库。
