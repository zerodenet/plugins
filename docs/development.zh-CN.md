# 市场开发

[English](development.md) · **简体中文**

使用 Python 3.10+、Node.js 22 与 pnpm 9.9。锁定依赖以 Minted Directory Astro 提交 `f71c8ae3fcff741285107415701fb6d1390f55b6` 为基线；许可见[第三方说明](../THIRD_PARTY_NOTICES.md)。

完整本地检查：

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    pnpm test:static-api
    pnpm build
    git diff --check

`pnpm build` 明确使用带测试标识的 `tests/fixtures/releases.json`，因此本地可复现构建只生成源码登记状态。生产构建不传 `--fixture` 执行 `scripts/build_snapshot.py`，随后执行 `pnpm build:site`，生成网站、完整快照和六个宿主/频道静态 API 文件。

只编辑 `catalogs/plugins.json`，再运行 `python3 scripts/generate_catalogs.py` 更新兼容投影。快照、站点输出、安装包、私钥和凭据都不入库；宿主安装器与插件源码继续留在各自仓库。
