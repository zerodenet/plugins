# Registry development

**English** · [简体中文](development.zh-CN.md)

Use Python 3.10 or later. Validation uses the standard library and does not install or build listed plugins.

```sh
git clone git@github.com:zerodenet/plugins.git
cd plugins
git switch -c feat/plugin-submission
python3 -m unittest discover -s tests
python3 scripts/validate.py
```

Edit the host catalog using [the format reference](registry-format.md). Keep fixtures in `templates/`, negative validation cases in `tests/` and executable checks in `scripts/`. Production entries must reference real source commits and releases. The Actions workflow runs the same checks on main pushes and pull requests with read-only repository permissions. It additionally calls `python3 scripts/validate.py --base <full-commit-sha>` to protect existing releases and publisher identity.

For OAuth implementation, clone [higanbana986/zboard-oauth](https://github.com/higanbana986/zboard-oauth) and follow its development guide. Host API work belongs in the host repository. This registry contains no plugin build workspace or shared runtime.
