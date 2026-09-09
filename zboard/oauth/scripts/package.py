#!/usr/bin/env python3
"""Build one platform and sign it using ZBoard's official package format."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zboard', type=Path, default=os.environ.get('ZBOARD_DIR'),
                        help='ZBoard checkout containing backend/tools/pluginpackager; or set ZBOARD_DIR')
    parser.add_argument('--platform', help='GOOS-GOARCH; defaults to this Go toolchain host')
    keys = parser.add_mutually_exclusive_group(required=True)
    keys.add_argument('--key', type=Path, help='base64 Ed25519 private key, outside source control')
    keys.add_argument('--dev-key', action='store_true', help='create/reuse an ignored local development key')
    parser.add_argument('--key-id', help='publisher key ID; required with --key')
    args = parser.parse_args()
    if args.zboard is None:
        parser.error('provide --zboard or ZBOARD_DIR; the host is maintained in a separate repository')
    if not args.dev_key and (not args.key_id or args.key_id == 'oauth-local-dev'):
        parser.error('--key requires an explicit non-development --key-id')
    if args.dev_key and args.key_id not in (None, 'oauth-local-dev'):
        parser.error('--dev-key only uses the oauth-local-dev publisher ID')
    args.key_id = args.key_id or 'oauth-local-dev'
    backend = args.zboard.resolve() / 'backend'
    if not (backend / 'tools/pluginpackager/main.go').is_file():
        parser.error('--zboard must contain the pluginpackager tool (feature/plugin or later)')
    platform = args.platform or '-'.join(subprocess.check_output(['go', 'env', 'GOOS', 'GOARCH'], cwd=ROOT, text=True).split())
    if platform not in {'linux-amd64', 'linux-arm64', 'darwin-amd64', 'darwin-arm64', 'windows-amd64'}:
        parser.error('unsupported platform')
    key = args.key.resolve() if args.key else ROOT / '.local/publisher.key'
    # The packager must resolve its own go.mod when an external workspace is set.
    host_env = {**os.environ, 'GOWORK': 'off'}
    if args.dev_key:
        key.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not key.exists():
            run('go', '-C', str(backend), 'run', './tools/pluginpackager', '-keygen', str(key), env=host_env)
    if not key.is_file():
        parser.error('private key file does not exist')
    build = ROOT / '.build'
    build.mkdir(exist_ok=True)
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=platform + '-', dir=build) as temporary:
        stage = Path(temporary)
        manifest = json.loads((ROOT / 'manifest.json').read_text())
        executable = f'runtimes/{platform}/oauth' + ('.exe' if platform.startswith('windows-') else '')
        target = stage / executable
        target.parent.mkdir(parents=True)
        goos, goarch = platform.split('-')
        run('go', 'build', '-trimpath', '-ldflags=-s -w', '-o', str(target), './cmd/oauth', env={**os.environ, 'CGO_ENABLED': '0', 'GOOS': goos, 'GOARCH': goarch})
        shutil.copytree(ROOT / 'ui', stage / 'ui')
        # UI tests are deliberately stored outside ui/ so no test source ships.
        manifest['components']['server'] = {'executables': {platform: executable}}
        (stage / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        package = output / f"zboard.oauth-{manifest['version']}-{platform}.zbplugin"
        run('go', '-C', str(backend), 'run', './tools/pluginpackager', '-source', str(stage), '-key', str(key), '-key-id', args.key_id, '-out', str(package), env=host_env)
        print(package)
    if args.dev_key:
        print(f'Development publisher public key: {key}.pub')
        print('Add that public key to plugins.trusted_publishers only on your test host.')


if __name__ == '__main__':
    main()
