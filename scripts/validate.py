#!/usr/bin/env python3
"""Validate marketplace source catalogs; never execute or download plugin code."""
import argparse
import base64
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {'zboard', 'znet-sink'}
PLATFORMS = {'linux-amd64', 'linux-arm64', 'darwin-amd64', 'darwin-arm64', 'windows-amd64', 'any'}
PRE = r'(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
TAG = rf'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-{PRE}(?:\.{PRE})*)?'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(value, required, optional=()):
    require(isinstance(value, dict), 'expected an object')
    require(set(required) <= value.keys() and value.keys() <= set(required) | set(optional), 'missing or unknown fields')


def text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 2000


def matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def https(value):
    require(text(value), 'expected HTTPS URL')
    parsed = urlsplit(value)
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
            and not parsed.fragment and not parsed.query and parsed.port in (None, 443), 'URL must be credential-free HTTPS without query or fragment')
    return parsed


def strings(value):
    return isinstance(value, list) and all(text(v) for v in value) and len(set(value)) == len(value)


def validate_entry(entry, host):
    fields(entry, ('id', 'name', 'description', 'repository', 'license', 'maintainers', 'publisher', 'source', 'releases'))
    require(matches(r'[a-z0-9][a-z0-9._-]{1,159}', entry['id']), 'invalid plugin ID')
    for name in ('name', 'description', 'license'):
        require(text(entry[name]), 'missing ' + name)
    repository = https(entry['repository'])
    require(repository.hostname == 'github.com' and matches(r'/[\w.-]+/[\w.-]+', repository.path), 'repository must identify a GitHub source repository')
    require(strings(entry['maintainers']) and entry['maintainers'], 'maintainers are required')
    pub = entry['publisher']
    fields(pub, ('id', 'public_key'))
    require(matches(r'[a-z0-9][a-z0-9._-]{0,79}', pub['id']), 'invalid publisher ID')
    if pub['public_key'] is not None:
        require(isinstance(pub['public_key'], str) and len(base64.b64decode(pub['public_key'], validate=True)) == 32, 'invalid Ed25519 public key')
    source = entry['source']
    fields(source, ('version', 'commit', 'manifest'))
    require(matches(TAG, source['version']), 'source version must be a v-prefixed version')
    require(matches(r'[a-f0-9]{40}', source['commit']), 'source commit must be a full Git SHA')
    path = source['manifest']
    require(text(path) and not path.startswith('/') and '\\' not in path and all(p not in ('', '.', '..') for p in path.split('/')), 'manifest must be a safe relative path')
    require(isinstance(entry['releases'], list), 'releases must be an array')
    require(not entry['releases'] or pub['public_key'] is not None, 'installable releases need a publisher public key')
    versions = set()
    for release in entry['releases']:
        fields(release, ('version', 'source_commit', 'requires', 'surfaces', 'capabilities', 'artifacts'))
        version = release['version']
        require(matches(TAG, version) and version not in versions, 'invalid or duplicate release version')
        versions.add(version)
        require(matches(r'[a-f0-9]{40}', release['source_commit']), 'release commit must be a full Git SHA')
        require(isinstance(release['requires'], dict) and text(release['requires'].get(host)), 'release must declare its target host requirement')
        require(not any(h in release['requires'] for h in HOSTS - {host}), 'cross-host requirement')
        require(strings(release['surfaces']) and strings(release['capabilities']), 'surfaces and capabilities must be unique string arrays')
        require(all(c.startswith(host + '.') for c in release['capabilities']), 'capability belongs to another host')
        if host == 'zboard':
            require(set(release['surfaces']) <= {'admin', 'public', 'account'}, 'invalid ZBoard UI surface')
            for protocol in ('plugin_protocol', 'ui_bridge'):
                require(type(release['requires'].get(protocol)) is int and release['requires'][protocol] > 0, 'missing protocol requirement')
        require(isinstance(release['artifacts'], list) and release['artifacts'], 'release must contain artifacts')
        platforms = set()
        for artifact in release['artifacts']:
            fields(artifact, ('platform', 'url', 'sha256', 'size'))
            platform = artifact['platform']
            require(platform in PLATFORMS and platform not in platforms, 'invalid or duplicate platform')
            platforms.add(platform)
            https(artifact['url'])
            require(matches(r'[a-f0-9]{64}', artifact['sha256']), 'invalid SHA-256')
            require(type(artifact['size']) is int and 0 < artifact['size'] <= 32 * 1024 * 1024, 'invalid package size')
            if host == 'zboard':
                require(artifact['url'].endswith('.zbplugin'), 'ZBoard requires .zbplugin packages')
        require('any' not in platforms or len(platforms) == 1, 'platform-independent artifacts cannot be mixed with platform-specific ones')


def validate(catalog, expected_host):
    fields(catalog, ('schema_version', 'host', 'plugins'))
    require(type(catalog['schema_version']) is int and catalog['schema_version'] == 1, 'unsupported source schema')
    require(catalog['host'] == expected_host and expected_host in HOSTS, 'catalog host mismatch')
    require(isinstance(catalog['plugins'], list), 'plugins must be an array')
    identities = set()
    for entry in catalog['plugins']:
        validate_entry(entry, expected_host)
        require(entry['id'] not in identities, 'duplicate plugin ID')
        identities.add(entry['id'])


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON field: ' + key)
        result[key] = value
    return result


def validate_transition(previous, current):
    entries = {entry['id']: entry for entry in current['plugins']}
    for old in previous['plugins']:
        require(old['id'] in entries, 'retain existing listings; withdrawals need a reviewed schema change')
        new = entries[old['id']]
        require(old['publisher']['id'] == new['publisher']['id'], 'publisher identity cannot be reassigned')
        if old['publisher']['public_key'] is not None:
            require(old['publisher']['public_key'] == new['publisher']['public_key'], 'key rotation requires an explicit transition contract')
        releases = {release['version']: release for release in new['releases']}
        for release in old['releases']:
            require(releases.get(release['version']) == release, 'existing releases must be retained without rewriting artifact metadata')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='compare with a Git commit to protect existing release records')
    args = parser.parse_args()
    try:
        if args.base:
            require(matches(r'[a-f0-9]{40}', args.base), 'base must be a full Git SHA')
            subprocess.run(['git', 'cat-file', '-e', args.base + '^{commit}'], cwd=ROOT, check=True, capture_output=True)
        for host in sorted(HOSTS):
            path = ROOT / 'catalogs' / (host + '.json')
            current = json.loads(path.read_text(), object_pairs_hook=no_duplicates)
            validate(current, host)
            if args.base:
                relative = str(path.relative_to(ROOT))
                files = subprocess.check_output(['git', 'ls-tree', '--name-only', args.base, '--', relative], cwd=ROOT, text=True)
                if files.strip():
                    raw = subprocess.check_output(['git', 'show', args.base + ':' + relative], cwd=ROOT, text=True)
                    previous = json.loads(raw, object_pairs_hook=no_duplicates)
                    validate(previous, host)
                    validate_transition(previous, current)
            print(f'{path.relative_to(ROOT)}: valid')
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'catalog: {error}')


if __name__ == '__main__':
    main()
