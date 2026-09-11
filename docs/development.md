# Directory development

**English** · [简体中文](development.zh-CN.md)

Use Python 3.10 or later. Validation uses the standard library and never installs or builds listed plugins.

Run:

    python3 -m unittest discover -s tests
    python3 scripts/validate.py
    git diff --check

Edit host catalogs using [the format reference](registry-format.md). Keep directory examples in templates, negative cases in tests, and executable checks in scripts. Production directory entries contain admission metadata only. Release fixtures belong only to onboarding automation tests because publisher releases are not copied into the market.

Host release discovery and management belong in the host repository. Plugin builds, packages, and release metadata belong in the plugin repository.
