import base64
import copy
import json
import unittest
from unittest.mock import patch
from test_sync import ReleaseAPI
from github_api import GitHubError
from marketplace_sync import Marketplace


class IssueAPI:
    def __init__(self):
        self.catalog = {'schema_version': 1, 'host': 'zboard', 'plugins': []}
        self.issue = {'number': 1, 'state': 'open', 'title': '[Plugin] Example',
                      'body': 'https://github.com/example/zboard-plugin/releases/download/v0.0.1/marketplace-entry.json',
                      'labels': [], 'updated_at': '2026-09-09T00:00:02Z'}
        self.comments = []
        self.writes = []
        self.permission = 'write'
        self.put_error = None

    def pages(self, path):
        if path.endswith('/comments'):
            return copy.deepcopy(self.comments)
        if '/issues?state=' in path:
            return [copy.deepcopy(self.issue)]
        raise AssertionError(path)

    def api(self, path, method='GET', data=None):
        prefix = '/repos/zerodenet/plugins'
        if method != 'GET':
            self.writes.append((path, method, copy.deepcopy(data)))
        if '/collaborators/' in path:
            return {'permission': self.permission}
        if '/contents/catalogs/zboard.json?ref=' in path:
            return {'encoding': 'base64', 'sha': 'b' * 40,
                    'content': base64.b64encode(json.dumps(self.catalog).encode()).decode()}
        if '/contents/catalogs/znet-sink.json?ref=' in path:
            return {'encoding': 'base64', 'sha': 'c' * 40,
                    'content': base64.b64encode(json.dumps({'schema_version': 1, 'host': 'znet-sink', 'plugins': []}).encode()).decode()}
        if path.endswith('/contents/catalogs/zboard.json') and method == 'PUT':
            if self.put_error:
                raise GitHubError(self.put_error, path)
            self.catalog = json.loads(base64.b64decode(data['content']))
            return {'commit': {'sha': 'c' * 40}}
        if path == prefix + '/issues/1':
            if method == 'PATCH':
                self.issue.update(data)
            return copy.deepcopy(self.issue)
        if '/issues/1/labels/' in path and method == 'DELETE':
            from urllib.parse import unquote
            label = unquote(path.rsplit('/', 1)[1])
            self.issue['labels'] = [l for l in self.issue['labels'] if l['name'] != label]
            return None
        if path.endswith('/issues/1/labels') and method == 'POST':
            self.issue['labels'] += [{'name': label} for label in data['labels']]
            return None
        if path.endswith('/issues/1/comments') and method == 'POST':
            self.comments.append({'id': 10, 'user': {'login': 'github-actions[bot]'}, 'body': data['body'], 'updated_at': '2026-09-09T00:00:01Z'})
            return self.comments[-1]
        if path.endswith('/issues/comments/10') and method == 'PATCH':
            self.comments[0]['body'] = data['body']
            return self.comments[0]
        raise AssertionError((path, method, data))

    def approve(self):
        self.issue['labels'].append({'name': 'status:approved'})
        return {'action': 'labeled', 'label': {'name': 'status:approved'},
                'sender': {'login': 'maintainer'}, 'issue': copy.deepcopy(self.issue)}


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.api = IssueAPI()
        self.entry = ReleaseAPI().entry
        self.market = Marketplace(self.api, 'zerodenet/plugins')
        self.mock = patch('marketplace_sync.release_entry', return_value=('zboard', self.entry))
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def labels(self):
        return {label['name'] for label in self.api.issue['labels']}

    def puts(self):
        return [call for call in self.api.writes if call[1] == 'PUT']

    def prepare(self):
        self.market.intake(copy.deepcopy(self.api.issue))
        self.assertIn('status:in-review', self.labels())
        self.assertFalse(self.puts())

    def test_submission_needs_only_issue_then_maintainer_label(self):
        self.prepare()
        self.market.issue_event(self.api.approve())
        self.assertEqual(len(self.puts()), 1)
        path, _, data = self.puts()[0]
        self.assertEqual(path, '/repos/zerodenet/plugins/contents/catalogs/zboard.json')
        self.assertEqual(data['branch'], 'main')
        self.assertEqual(data['sha'], 'b' * 40)
        self.assertIn('Approved-by: maintainer', data['message'])
        self.assertEqual(self.api.catalog['plugins'], [self.entry])
        self.assertIn('status:accepted', self.labels())
        self.assertNotIn('status:approved', self.labels())
        self.assertEqual(self.api.issue['state'], 'closed')
        self.assertFalse(any('/pulls' in call[0] or '/git/refs' in call[0] for call in self.api.writes))

    def test_read_or_triage_user_cannot_approve(self):
        for permission in ('read', 'triage', 'none'):
            with self.subTest(permission=permission):
                self.api.permission = permission
                self.prepare()
                self.market.issue_event(self.api.approve())
                self.assertFalse(self.puts())
                self.assertNotIn('status:approved', self.labels())

    def test_no_review_snapshot_or_forged_comment_cannot_approve(self):
        self.market.issue_event(self.api.approve())
        self.assertFalse(self.puts())
        self.assertIn('status:in-review', self.labels())
        self.api.comments[0]['user']['login'] = 'publisher'
        self.market.issue_event(self.api.approve())
        self.assertFalse(self.puts())

    def test_changed_issue_or_release_requires_new_review(self):
        self.prepare()
        event = self.api.approve()
        self.api.issue['body'] += '\nChanged permissions'
        self.market.issue_event(event)
        self.assertFalse(self.puts())
        self.assertIn('status:in-review', self.labels())
        self.entry['description'] += ' changed'
        self.market.issue_event(self.api.approve())
        self.assertFalse(self.puts())
        self.market.issue_event(self.api.approve())
        self.assertEqual(len(self.puts()), 1)

    def test_old_approval_event_cannot_authorize_a_new_review_snapshot(self):
        self.prepare()
        event = self.api.approve()
        self.api.comments[0]['updated_at'] = '2026-09-09T00:00:03Z'
        self.market.issue_event(event)
        self.assertFalse(self.puts())
        self.assertIn('status:in-review', self.labels())

    def test_close_or_revoke_during_validation_prevents_write(self):
        self.prepare()
        event = self.api.approve()
        def revoke(*args):
            self.api.issue['labels'] = [l for l in self.api.issue['labels'] if l['name'] != 'status:approved']
            return 'zboard', self.entry
        with patch('marketplace_sync.release_entry', side_effect=revoke):
            self.market.issue_event(event)
        self.assertFalse(self.puts())
        self.api.issue['state'] = 'closed'
        self.market.issue_event(event)
        self.assertFalse(self.puts())

    def test_edit_event_invalidates_approval_and_schedule_never_consumes_labels(self):
        self.prepare()
        event = self.api.approve()
        self.market.reconcile()
        self.assertFalse(self.puts())
        self.assertIn('status:approved', self.labels())
        event['action'] = 'edited'
        self.market.issue_event(event)
        self.assertNotIn('status:approved', self.labels())
        self.assertIn('status:in-review', self.labels())

    def test_duplicate_delivery_is_idempotent(self):
        self.prepare()
        event = self.api.approve()
        self.market.issue_event(event)
        self.market.issue_event(event)
        self.assertEqual(len(self.puts()), 1)

    def test_branch_protection_or_conflict_keeps_review_retryable(self):
        for status in (403, 409):
            with self.subTest(status=status):
                self.api.writes.clear()
                self.prepare()
                event = self.api.approve()
                self.api.put_error = status
                with self.assertRaises(GitHubError):
                    self.market.issue_event(event)
                self.assertIn('status:approved', self.labels())
                self.assertEqual(self.api.issue['state'], 'open')
                self.assertEqual(self.api.catalog['plugins'], [])
                self.api.put_error = None
        self.market.issue_event(event)
        self.assertEqual(self.api.issue['state'], 'closed')

    def test_existing_catalog_release_recovers_partial_success_without_duplicate_commit(self):
        self.prepare()
        self.api.catalog['plugins'] = [copy.deepcopy(self.entry)]
        self.market.issue_event(self.api.approve())
        self.assertFalse(self.puts())
        self.assertEqual(self.api.issue['state'], 'closed')

    def test_snapshot_is_rechecked_immediately_before_publish(self):
        self.prepare()
        event = self.api.approve()
        original = self.market.reviewed
        def changed(number, digest, approved_at=None):
            valid = original(number, digest, approved_at)
            self.api.issue['body'] += '\nedited during check'
            return valid
        with patch.object(self.market, 'reviewed', side_effect=changed):
            self.market.issue_event(event)
        self.assertFalse(self.puts())


class UpdateReviewTest(unittest.TestCase):
    def setUp(self):
        self.old = ReleaseAPI().entry
        self.new = copy.deepcopy(self.old)
        self.new['source']['version'] = self.new['releases'][0]['version'] = 'v0.0.2'
        self.repo = self.old['repository'].removeprefix('https://github.com/')
        self.issues = []
        self.writes = []
        self.market = Marketplace(self, 'zerodenet/plugins')

    def pages(self, path):
        if '/issues?state=all' in path:
            return self.issues
        raise AssertionError(path)

    def api(self, path, method='GET', data=None):
        if '/contents/catalogs/' in path:
            host = 'zboard' if 'zboard.json' in path else 'znet-sink'
            catalog = {'schema_version': 1, 'host': host, 'plugins': [self.old] if host == 'zboard' else []}
            return {'encoding': 'base64', 'sha': 'a' * 40,
                    'content': base64.b64encode(json.dumps(catalog).encode()).decode()}
        if path.endswith('/releases/latest'):
            return {'tag_name': 'v0.0.2'}
        if path.endswith('/issues') and method == 'POST':
            self.writes.append(data)
            return {'number': 2, 'state': 'open', **data, 'labels': [{'name': n} for n in data['labels']]}
        raise AssertionError((path, method))

    def test_upstream_update_creates_issue_and_validates_without_pr_or_catalog_write(self):
        with patch('marketplace_sync.release_entry', return_value=('zboard', self.new)), patch.object(self.market, 'intake') as intake:
            self.market.updates()
            self.assertEqual(len(self.writes), 1)
            self.assertIn('plugin:update', self.writes[0]['labels'])
            self.assertNotIn('status:approved', self.writes[0]['labels'])
            intake.assert_called_once()
            # A subsequent API list contains the previous issue, even if closed.
            self.issues = [{**intake.call_args.args[0], 'state': 'closed'}]
            self.market.updates()
            self.assertEqual(len(self.writes), 1)

    def test_existing_author_submission_prevents_duplicate_update_issue(self):
        self.issues = [{'number': 4, 'title': '[Plugin] Submitted by author', 'labels': [],
                        'body': f'https://github.com/{self.repo}/releases/download/v0.0.2/marketplace-entry.json'}]
        with patch('marketplace_sync.release_entry', return_value=('zboard', self.new)):
            self.market.updates()
        self.assertEqual(self.writes, [])

    def test_upstream_cannot_replace_publisher(self):
        self.new['publisher']['id'] = 'another-publisher'
        with patch('marketplace_sync.release_entry', return_value=('zboard', self.new)):
            with self.assertRaises(RuntimeError):
                self.market.updates()
        self.assertEqual(self.writes, [])



if __name__ == '__main__':
    unittest.main()
