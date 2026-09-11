import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from github_api import check_asset_url
from marketplace_sync import Marketplace
from release_metadata import append_entry, listing_entry, submission


class ReleaseAPI:
    def __init__(self):
        self.listing = json.loads((ROOT / 'templates/plugin-entry.json').read_text())
        self.repo = self.listing['repository'].removeprefix('https://github.com/')
        self.tag = 'v0.0.1'
        self.commit = '1' * 40
        self.base = f'https://github.com/{self.repo}/releases/download/{self.tag}/'
        self.artifact = {
            'platform': 'linux-amd64',
            'url': self.base + 'linux-amd64.zbplugin',
            'sha256': '2' * 64,
            'size': 123,
        }
        self.info = {
            'schema_version': 1,
            'id': self.listing['id'],
            'name': 'Example plugin',
            'description': 'Repository-owned plugin information.',
            'repository': self.listing['repository'],
            'license': 'MPL-2.0',
            'maintainers': ['example'],
        }
        self.document = {
            **{key: value for key, value in self.info.items() if key != 'schema_version'},
            'publisher': self.listing['publisher'],
            'source': {'version': self.tag, 'commit': self.commit, 'manifest': 'manifest.json'},
            'releases': [{
                'version': self.tag,
                'source_commit': self.commit,
                'requires': {'zboard': '>=0.0.1 <0.1.0', 'plugin_protocol': 1, 'ui_bridge': 1},
                'surfaces': self.listing['surfaces'],
                'capabilities': self.listing['capabilities'],
                'artifacts': [self.artifact],
            }],
        }
        self.draft = False
        self.prerelease = False
        self.refresh()

    def refresh(self):
        self.raw = json.dumps(self.document).encode()
        self.metadata = {
            'name': 'marketplace-entry.json',
            'browser_download_url': self.base + 'marketplace-entry.json',
            'size': len(self.raw),
            'digest': 'sha256:' + hashlib.sha256(self.raw).hexdigest(),
        }
        self.assets = [
            self.metadata,
            {'name': 'linux-amd64.zbplugin', 'browser_download_url': self.artifact['url'],
             'size': self.artifact['size'], 'digest': 'sha256:' + self.artifact['sha256']},
        ]

    def api(self, path):
        if '/releases/tags/' in path:
            return {'id': 1, 'tag_name': self.tag, 'draft': self.draft, 'prerelease': self.prerelease}
        if '/git/ref/tags/' in path:
            return {'object': {'type': 'commit', 'sha': self.commit}}
        if path.endswith('/contents/marketplace.json'):
            raw = json.dumps(self.info).encode()
            return {'type': 'file', 'encoding': 'base64', 'size': len(raw),
                    'content': base64.b64encode(raw).decode()}
        raise AssertionError(path)

    def pages(self, path):
        return iter(self.assets)

    def asset(self, url, size):
        self.assert_asset = (url, size)
        return self.raw


class SyncTest(unittest.TestCase):
    def test_application_derives_listing_without_copying_release_history(self):
        api = ReleaseAPI()
        host, entry = listing_entry(api, api.repo, api.tag)
        self.assertEqual(host, 'zboard')
        self.assertEqual(entry, api.listing)
        self.assertFalse({'source', 'releases', 'version', 'artifacts'} & entry.keys())

    def test_onboarding_release_verifies_source_and_assets(self):
        for change in (
            lambda a: setattr(a, 'draft', True),
            lambda a: setattr(a, 'prerelease', True),
            lambda a: setattr(a, 'commit', 'f' * 40),
            lambda a: a.metadata.update(digest='sha256:' + 'f' * 64),
            lambda a: a.assets[1].update(size=2),
            lambda a: a.assets[1].update(digest='sha256:' + 'f' * 64),
            lambda a: a.assets[1].update(browser_download_url='https://example.com/file.zbplugin'),
            lambda a: a.info.update(name='Repository metadata changed during admission'),
        ):
            with self.subTest(change=change):
                api = ReleaseAPI()
                change(api)
                with self.assertRaises(ValueError):
                    listing_entry(api, api.repo, api.tag)

    def test_existing_listing_is_idempotent_but_not_rewritten_by_a_release(self):
        api = ReleaseAPI()
        empty = {'schema_version': 2, 'host': 'zboard', 'plugins': []}
        first = append_entry(empty, api.listing, 'zboard')
        self.assertEqual(append_entry(first, api.listing, 'zboard'), first)
        changed = copy.deepcopy(api.listing)
        changed['publisher']['public_key'] = base64.b64encode(b'x' * 32).decode()
        with self.assertRaises(ValueError):
            append_entry(first, changed, 'zboard')

    def test_submission_form_accepts_one_onboarding_release_only(self):
        url = 'https://github.com/example/zboard-example/releases/download/v0.0.1/marketplace-entry.json'
        self.assertEqual(submission(f'### Onboarding release\n\n{url}'), ('example/zboard-example', 'v0.0.1'))
        for body in ('https://example.com/metadata.json', url + '\n' + url.replace('v0.0.1', 'v0.0.2'), ''):
            with self.assertRaises(ValueError):
                submission(body)

    def test_proposal_writes_only_a_durable_listing(self):
        class API:
            def __init__(self):
                self.catalog_value = {'schema_version': 2, 'host': 'zboard', 'plugins': []}
                self.branch_catalog = None
                self.writes = []

            def api(self, path, method='GET', data=None):
                if method != 'GET':
                    self.writes.append((path, method, data))
                if path.endswith('/git/ref/heads/main'):
                    return {'object': {'sha': 'a' * 40}}
                if '/contents/catalogs/zboard.json?ref=' in path:
                    value = self.catalog_value if path.endswith('a' * 40) else self.branch_catalog
                    return {'encoding': 'base64', 'sha': 'b' * 40,
                            'content': base64.b64encode(json.dumps(value).encode()).decode()}
                if '/pulls?state=all&head=' in path:
                    return []
                if path.endswith('/git/refs'):
                    self.branch_catalog = copy.deepcopy(self.catalog_value)
                    return {}
                if path.endswith('/contents/catalogs/zboard.json') and method == 'PUT':
                    self.branch_catalog = json.loads(base64.b64decode(data['content']))
                    return {}
                if path.endswith('/pulls') and method == 'POST':
                    return {'number': 2, 'state': 'open', 'html_url': 'https://github.com/zerodenet/plugins/pull/2'}
                raise AssertionError((path, method, data))

        api = API()
        issue = {'number': 1, 'body': 'application'}
        proposal = Marketplace(api, 'zerodenet/plugins').propose('zboard', ReleaseAPI().listing, issue)
        self.assertEqual(proposal['number'], 2)
        stored = api.branch_catalog['plugins'][0]
        self.assertFalse({'name', 'description', 'license', 'maintainers', 'source', 'releases', 'version', 'artifacts'} & stored.keys())
        self.assertEqual(stored['metadata_source'], {'type': 'repository-file', 'path': 'marketplace.json'})

    def test_downloads_never_redirect_to_arbitrary_hosts_or_credentials(self):
        for url in ('http://github.com/a', 'https://evil.example/a', 'https://127.0.0.1/a',
                    'https://user:secret@github.com/a', 'https://github.com:8443/a',
                    'https://github.com.evil.example/a'):
            with self.assertRaises(ValueError):
                check_asset_url(url)
        check_asset_url('https://release-assets.githubusercontent.com/a?temporary=token')

    def test_workflow_has_no_release_polling_gate(self):
        workflow = (ROOT / '.github/workflows/marketplace.yml').read_text()
        self.assertIn('ref: main', workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertNotIn('schedule:', workflow)
        self.assertNotIn('plugin:update', (ROOT / '.github/labels.json').read_text())


if __name__ == '__main__':
    unittest.main()
