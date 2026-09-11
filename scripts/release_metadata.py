"""Validate one onboarding release and derive a durable marketplace listing."""
import base64
import copy
import hashlib
import re

from github_api import decode_json, segment
from validate import HOSTS, fields, https, require, strings, text, validate, validate_entry

PRE = r'(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
TAG = rf'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-{PRE}(?:\.{PRE})*)?'
METADATA_URL = re.compile(
    r'https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/releases/download/('
    + TAG + r')/marketplace-entry\.json')


def submission(body):
    urls = {match.group(0) for match in METADATA_URL.finditer(body or '')}
    require(len(urls) == 1,
            'Provide exactly one onboarding marketplace-entry.json URL / 请提供唯一的入驻发行元数据链接')
    match = METADATA_URL.fullmatch(urls.pop())
    return match[1], match[2]


def infer_host(release):
    requirements = release.get('requires', {})
    hosts = {host for host in HOSTS if host in requirements}
    require(len(hosts) == 1, 'metadata must identify exactly one host')
    return hosts.pop()


def listing_entry(github, repository, tag):
    release = github.api(f'/repos/{repository}/releases/tags/{segment(tag)}')
    require(not release['draft'] and not release['prerelease'] and release['tag_name'] == tag
            and '-' not in tag, 'marketplace onboarding requires one published stable release')
    assets = list(github.pages(f'/repos/{repository}/releases/{release["id"]}/assets'))
    records = [asset for asset in assets if asset['name'] == 'marketplace-entry.json']
    require(len(records) == 1, 'onboarding release needs one marketplace-entry.json asset')
    record = records[0]
    expected_url = f'https://github.com/{repository}/releases/download/{tag}/marketplace-entry.json'
    require(record['browser_download_url'] == expected_url, 'metadata asset repository or tag mismatch')
    raw = github.asset(expected_url, record['size'])
    require(record.get('digest') == 'sha256:' + hashlib.sha256(raw).hexdigest(),
            'metadata digest does not match GitHub release asset')
    document = decode_json(raw)
    required = {'id', 'name', 'description', 'repository', 'license', 'maintainers', 'publisher', 'source', 'releases'}
    require(required <= document.keys(), 'onboarding metadata is incomplete')
    require(document['repository'] == f'https://github.com/{repository}',
            'metadata must belong to the publishing repository')

    record = github.api(f'/repos/{repository}/contents/marketplace.json')
    require(record.get('type') == 'file' and record.get('encoding') == 'base64'
            and 0 < record.get('size', 0) <= 64 * 1024,
            'repository must expose a bounded marketplace.json file')
    try:
        repository_raw = base64.b64decode(''.join(record['content'].split()), validate=True)
    except (KeyError, TypeError, ValueError):
        repository_raw = b''
    require(len(repository_raw) == record['size'], 'marketplace.json size or encoding mismatch')
    information = decode_json(repository_raw)
    fields(information, ('schema_version', 'id', 'name', 'description', 'repository', 'license', 'maintainers'),
           ('homepage', 'documentation', 'security'))
    require(information['schema_version'] == 1 and information['id'] == document['id']
            and information['repository'] == document['repository'],
            'marketplace.json identity differs from the onboarding release')
    require(all(text(information[field]) for field in ('name', 'description', 'license'))
            and strings(information['maintainers']) and information['maintainers'],
            'marketplace.json basic information is incomplete')
    for field in ('homepage', 'documentation', 'security'):
        if field in information:
            https(information[field])
    require(all(information[field] == document[field]
                for field in ('name', 'description', 'license', 'maintainers')),
            'onboarding release information differs from marketplace.json')
    require(isinstance(document['releases'], list) and len(document['releases']) == 1,
            'onboarding metadata must describe exactly its own release')
    version = document['releases'][0]
    require(version.get('version') == tag == document['source'].get('version'),
            'release version differs from metadata')
    require(version.get('source_commit') == document['source'].get('commit'),
            'source commits differ')
    host = infer_host(version)

    ref = github.api(f'/repos/{repository}/git/ref/tags/{segment(tag)}')['object']
    for _ in range(4):
        if ref['type'] != 'tag':
            break
        ref = github.api(f'/repos/{repository}/git/tags/{ref["sha"]}')['object']
    require(ref['type'] == 'commit' and ref['sha'] == version['source_commit'],
            'tag does not resolve to the declared source commit')
    by_url = {asset['browser_download_url']: asset for asset in assets}
    require(isinstance(version.get('artifacts'), list) and version['artifacts'],
            'onboarding release has no packages')
    for artifact in version['artifacts']:
        asset = by_url.get(artifact.get('url'))
        require(asset is not None and asset['size'] == artifact.get('size')
                and asset.get('digest') == 'sha256:' + artifact.get('sha256', ''),
                'package must match a GitHub asset size and digest in this release')

    entry = {
        'id': document['id'],
        'repository': document['repository'],
        'publisher': document['publisher'],
        'metadata_source': {'type': 'repository-file', 'path': 'marketplace.json'},
        'release_source': {'type': 'github-releases', 'metadata_asset': 'marketplace-entry.json'},
        'surfaces': version.get('surfaces'),
        'capabilities': version.get('capabilities'),
    }
    validate_entry(entry, host)
    return host, entry


def append_entry(catalog, entry, host):
    validate(catalog, host)
    validate_entry(entry, host)
    result = copy.deepcopy(catalog)
    old = next((item for item in result['plugins'] if item['id'] == entry['id']), None)
    if old is None:
        result['plugins'].append(copy.deepcopy(entry))
    else:
        require(old == entry,
                'the plugin is already listed; address, key, source contract or capability changes need a focused marketplace PR')
    validate(result, host)
    return result
