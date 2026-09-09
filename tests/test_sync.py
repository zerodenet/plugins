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
from release_metadata import append_entry, release_entry, submission


class ReleaseAPI:
    def __init__(self):
        self.entry = json.loads((ROOT / 'templates/plugin-entry.json').read_text())
        self.repo = self.entry['repository'].removeprefix('https://github.com/')
        self.tag = self.entry['source']['version']
        self.base = f'https://github.com/{self.repo}/releases/download/{self.tag}/'
        self.entry['releases'] = self.entry['releases'][:1]
        self.entry['releases'][0]['source_commit'] = self.entry['source']['commit']
        for a in self.entry['releases'][0]['artifacts']:
            a['url'] = self.base + a['platform'] + '.zbplugin'
        self.assets = [{'name': 'package.zbplugin', 'browser_download_url': a['url'], 'size': a['size'], 'digest': 'sha256:' + a['sha256']} for a in self.entry['releases'][0]['artifacts']]
        self.commit = self.entry['source']['commit']
        self.draft = False
        self.refresh()

    def refresh(self):
        self.raw = json.dumps(self.entry).encode()
        self.metadata = {'name': 'marketplace-entry.json', 'browser_download_url': self.base + 'marketplace-entry.json', 'size': len(self.raw), 'digest': 'sha256:' + hashlib.sha256(self.raw).hexdigest()}

    def api(self, path):
        if '/releases/tags/' in path:
            return {'id': 1, 'tag_name': self.tag, 'draft': self.draft, 'prerelease': False}
        if '/git/ref/tags/' in path:
            return {'object': {'type': 'commit', 'sha': self.commit}}
        raise AssertionError(path)

    def pages(self, path):
        return iter([self.metadata] + self.assets)

    def asset(self, url, size):
        assert url == self.metadata['browser_download_url']
        return self.raw


class SyncTest(unittest.TestCase):
    def test_proposals_only_write_the_host_catalog_and_reuse_existing_prs(self):
        class API:
            def __init__(self):
                self.catalog = {'schema_version': 1, 'host': 'zboard', 'plugins': []}
                self.proposals = []
                self.writes = []
                self.branch_catalog = None
            def api(self, path, method='GET', data=None):
                if method != 'GET': self.writes.append((path, method, data))
                if path.endswith('/git/ref/heads/main'): return {'object': {'sha': 'a' * 40}}
                if '/contents/catalogs/zboard.json?ref=' in path:
                    value = self.catalog if path.endswith('a' * 40) else self.branch_catalog
                    return {'encoding': 'base64', 'sha': 'b' * 40, 'content': base64.b64encode(json.dumps(value).encode()).decode()}
                if '/pulls?state=all&head=' in path: return self.proposals
                if path.endswith('/git/refs'):
                    self.branch_catalog = copy.deepcopy(self.catalog); return {}
                if path.endswith('/contents/catalogs/zboard.json') and method == 'PUT':
                    self.branch_catalog = json.loads(base64.b64decode(data['content'])); return {}
                if path.endswith('/pulls') and method == 'POST':
                    result = {'number': 2, 'state': 'open', 'html_url': 'https://github.com/zerodenet/plugins/pull/2'}
                    self.proposals.append(result); return result
                if path.endswith('/issues/2'): return {'labels': []}
                if path.endswith('/issues/2/labels'): return {}
                raise AssertionError((path, method, data))
        api = API()
        market = Marketplace(api, 'zerodenet/plugins')
        entry = ReleaseAPI().entry
        first = market.propose('zboard', entry)
        writes = len(api.writes)
        self.assertEqual(market.propose('zboard', entry), first)
        self.assertEqual(len(api.writes), writes)
        puts = [path for path, method, _ in api.writes if method == 'PUT']
        self.assertEqual(puts, ['/repos/zerodenet/plugins/contents/catalogs/zboard.json'])
        api.proposals[0]['state'] = 'closed'
        self.assertEqual(market.propose('zboard', entry)['state'], 'closed')
        self.assertEqual(len(api.writes), writes)

    def test_existing_submission_and_form_link_are_supported(self):
        url = 'https://github.com/higanbana986/zboard-oauth/releases/download/v0.0.1/marketplace-entry.json'
        self.assertEqual(submission(f'### Release metadata URL\n\n{url}'), ('higanbana986/zboard-oauth', 'v0.0.1'))
        self.assertEqual(submission(f'- [marketplace-entry.json]({url})'), ('higanbana986/zboard-oauth', 'v0.0.1'))
        for body in ('https://example.com/metadata.json', url + '\n' + url.replace('v0.0.1', 'v0.0.2'), ''):
            with self.assertRaises(ValueError):
                submission(body)

    def test_release_verifies_source_and_all_server_recorded_artifacts(self):
        api = ReleaseAPI()
        host, entry = release_entry(api, api.repo, api.tag)
        self.assertEqual(host, 'zboard')
        self.assertEqual(entry, api.entry)
        for change in (
            lambda a: setattr(a, 'draft', True),
            lambda a: setattr(a, 'commit', 'f' * 40),
            lambda a: a.metadata.update(digest='sha256:' + 'f' * 64),
            lambda a: a.assets[0].update(size=2),
            lambda a: a.assets[0].update(digest='sha256:' + 'f' * 64),
            lambda a: a.assets[0].update(browser_download_url='https://example.com/file.zbplugin'),
        ):
            with self.subTest(change=change):
                api = ReleaseAPI(); change(api)
                with self.assertRaises(ValueError):
                    release_entry(api, api.repo, api.tag)

    def test_metadata_cannot_claim_another_repository(self):
        api = ReleaseAPI()
        api.entry['repository'] = 'https://github.com/other/plugin'; api.refresh()
        with self.assertRaises(ValueError):
            release_entry(api, api.repo, api.tag)

    def test_merge_is_idempotent_and_preserves_immutable_history(self):
        api = ReleaseAPI()
        empty = {'schema_version': 1, 'host': 'zboard', 'plugins': []}
        first = append_entry(empty, api.entry, 'zboard')
        self.assertEqual(append_entry(first, api.entry, 'zboard'), first)
        next_entry = copy.deepcopy(api.entry)
        next_entry['source']['version'] = next_entry['releases'][0]['version'] = 'v0.0.2'
        second = append_entry(first, next_entry, 'zboard')
        self.assertEqual(second['plugins'][0]['releases'][0], api.entry['releases'][0])
        self.assertEqual(len(second['plugins'][0]['releases']), 2)
        self.assertEqual(first['plugins'][0]['releases'], api.entry['releases'])
        for mutate in (
            lambda e: e['publisher'].update(public_key=base64.b64encode(b'x' * 32).decode()),
            lambda e: e['publisher'].update(id='other'),
            lambda e: e.update(repository='https://github.com/other/plugin'),
            lambda e: e['releases'][0]['artifacts'][0].update(size=2),
        ):
            changed = copy.deepcopy(api.entry); mutate(changed)
            with self.assertRaises(ValueError):
                append_entry(first, changed, 'zboard')

    def test_source_only_listing_gets_its_first_release(self):
        api = ReleaseAPI()
        old = copy.deepcopy(api.entry); old['releases'] = []; old['publisher']['public_key'] = None
        current = {'schema_version': 1, 'host': 'zboard', 'plugins': [old]}
        result = append_entry(current, api.entry, 'zboard')
        self.assertEqual(len(result['plugins']), 1)
        self.assertEqual(len(result['plugins'][0]['releases']), 1)

    def test_downloads_never_redirect_to_arbitrary_hosts_or_credentials(self):
        for url in ('http://github.com/a', 'https://evil.example/a', 'https://127.0.0.1/a', 'https://user:secret@github.com/a', 'https://github.com:8443/a', 'https://github.com.evil.example/a'):
            with self.assertRaises(ValueError):
                check_asset_url(url)
        check_asset_url('https://release-assets.githubusercontent.com/a?temporary=token')

    def test_status_only_replaces_owned_status_labels(self):
        class API:
            def __init__(self): self.calls = []
            def api(self, path, method='GET', data=None):
                self.calls.append((path, method, data))
                return {'labels': [{'name': n} for n in ['priority:high', 'status:needs-info', 'host:zboard']]}
        api = API()
        Marketplace(api, 'zerodenet/plugins').status(1, 'status:in-review', ['host:zboard'])
        self.assertEqual([call[1] for call in api.calls], ['GET', 'DELETE', 'POST'])
        self.assertTrue(api.calls[1][0].endswith('status%3Aneeds-info'))
        self.assertEqual(api.calls[2][2], {'labels': ['status:in-review']})

    def test_privileged_workflow_never_checks_out_contributor_code(self):
        workflow = (ROOT / '.github/workflows/marketplace.yml').read_text()
        self.assertIn('ref: main', workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertNotIn('github.event.issue.body', workflow)
        self.assertNotIn('github.event.pull_request.head.sha', workflow)


if __name__ == '__main__':
    unittest.main()
