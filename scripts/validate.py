#!/usr/bin/env python3
"""Validate the curated plugin directory without reading publisher releases."""
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
SURFACES = {'zboard': {'admin', 'public', 'account'}, 'znet-sink': set()}


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
            and not parsed.fragment and not parsed.query and parsed.port in (None, 443),
            'URL must be credential-free HTTPS without query or fragment')
    return parsed


def strings(value):
    return isinstance(value, list) and all(text(v) for v in value) and len(set(value)) == len(value)


def validate_entry(entry, host):
    fields(entry, ('id', 'repository', 'publisher', 'metadata_source',
                   'release_source', 'surfaces', 'capabilities'))
    require(matches(r'[a-z0-9][a-z0-9._-]{1,159}', entry['id']), 'invalid plugin ID')
    repository = https(entry['repository'])
    require(repository.hostname == 'github.com' and matches(r'/[\w.-]+/[\w.-]+', repository.path),
            'repository must identify a GitHub source repository')

    publisher = entry['publisher']
    fields(publisher, ('id', 'public_key'))
    require(matches(r'[a-z0-9][a-z0-9._-]{0,79}', publisher['id']), 'invalid publisher ID')
    try:
        key = base64.b64decode(publisher['public_key'], validate=True)
    except (TypeError, ValueError):
        key = b''
    require(len(key) == 32, 'publisher must provide an Ed25519 public key')

    metadata = entry['metadata_source']
    fields(metadata, ('type', 'path'))
    require(metadata['type'] == 'repository-file', 'unsupported metadata source')
    require(metadata['path'] == 'marketplace.json', 'repository metadata path must be marketplace.json')

    source = entry['release_source']
    fields(source, ('type', 'metadata_asset'))
    require(source['type'] == 'github-releases', 'unsupported release source')
    require(matches(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.json', source['metadata_asset']),
            'release metadata asset must be a simple JSON filename')

    require(strings(entry['surfaces']) and set(entry['surfaces']) <= SURFACES[host], 'invalid UI surface ceiling')
    require(strings(entry['capabilities']), 'capabilities must be a unique string array')
    require(all(matches(r'[a-z0-9][a-z0-9._-]{1,159}', value) and value.startswith(host + '.')
                for value in entry['capabilities']), 'capability belongs to another host or is invalid')


def validate(catalog, expected_host):
    fields(catalog, ('schema_version', 'host', 'plugins'))
    require(catalog['schema_version'] == 2, 'unsupported directory schema')
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
    """Listings are durable; release history deliberately is not stored here."""
    current_ids = {entry['id'] for entry in current['plugins']}
    for old in previous.get('plugins', []):
        require(old['id'] in current_ids, 'retain existing listings; removal needs an explicit withdrawal record')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='compare with a Git commit to protect existing listings')
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
                    validate_transition(previous, current)
            print(f'{path.relative_to(ROOT)}: valid')
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'catalog: {error}')


if __name__ == '__main__':
    main()
