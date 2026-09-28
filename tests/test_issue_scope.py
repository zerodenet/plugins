import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import marketplace_sync


class IssueScopeTest(unittest.TestCase):
    def run_issue_event(self, event, issue, intake_result=None):
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory) / 'event.json'
            event_path.write_text(json.dumps(event))
            github = Mock(token='test-token')
            github.api.return_value = issue
            market = Mock(prefix='/repos/example/plugins')
            market.intake.return_value = intake_result
            with patch.dict(os.environ, {
                'GITHUB_REPOSITORY': 'example/plugins',
                'GITHUB_EVENT_NAME': 'issues',
                'GITHUB_EVENT_PATH': str(event_path),
            }), patch.object(marketplace_sync, 'GitHub', return_value=github), \
                    patch.object(marketplace_sync, 'Marketplace', return_value=market):
                marketplace_sync.main()
            return market

    def test_regular_issue_does_not_receive_submission_actions(self):
        for state in ('open', 'closed'):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as directory:
                event_path = Path(directory) / 'event.json'
                event_path.write_text(json.dumps({'issue': {'number': 7}}))
                github = Mock(token='test-token')
                github.api.return_value = {
                    'number': 7, 'title': 'Documentation typo', 'state': state, 'labels': [],
                }
                market = Mock(prefix='/repos/example/plugins')
                with patch.dict(os.environ, {
                    'GITHUB_REPOSITORY': 'example/plugins',
                    'GITHUB_EVENT_NAME': 'issues',
                    'GITHUB_EVENT_PATH': str(event_path),
                }), patch.object(marketplace_sync, 'GitHub', return_value=github), \
                        patch.object(marketplace_sync, 'Marketplace', return_value=market):
                    marketplace_sync.main()
                market.intake.assert_not_called()
                market.status.assert_not_called()

    def test_valid_submissions_register_without_a_maintainer_label(self):
        issue = {
            'number': 7, 'title': '[Plugin] example', 'body': 'body', 'state': 'open',
            'labels': [{'name': 'plugin:submission'}],
        }
        for action in ('opened', 'edited', 'reopened'):
            with self.subTest(action=action):
                event = {'action': action, 'issue': {'number': 7}, 'sender': {'type': 'User'}}
                market = self.run_issue_event(event, issue, {'sha': 'c' * 40})
                market.intake.assert_called_once_with(issue)
                market.dispatch_publication.assert_called_once_with()

    def test_current_record_does_not_dispatch_another_publication(self):
        issue = {
            'number': 7, 'title': '[Plugin] example', 'body': 'body', 'state': 'open',
            'labels': [{'name': 'plugin:submission'}],
        }
        market = self.run_issue_event({'action': 'edited', 'issue': {'number': 7}}, issue)
        market.intake.assert_called_once_with(issue)
        market.dispatch_publication.assert_not_called()

    def test_automation_labels_do_not_start_recursive_registration(self):
        issue = {'number': 7, 'title': '[Plugin] example', 'state': 'open', 'labels': []}
        for label in ('status:registered', 'status:accepted', 'status:needs-info'):
            event = {'action': 'labeled', 'issue': {'number': 7},
                     'label': {'name': label}, 'sender': {'type': 'Bot'}}
            market = self.run_issue_event(event, issue)
            market.intake.assert_not_called()
            market.dispatch_publication.assert_not_called()

    def test_human_closed_label_closes_without_intake(self):
        issue = {
            'number': 7, 'title': '[Plugin] example', 'body': 'body', 'state': 'open',
            'labels': [{'name': 'plugin:submission'}, {'name': 'status:closed'}],
        }
        event = {
            'action': 'labeled', 'issue': {'number': 7},
            'label': {'name': 'status:closed'}, 'sender': {'type': 'User'},
        }
        market = self.run_issue_event(event, issue)
        market.close_application.assert_called_once_with(issue)
        market.intake.assert_not_called()


if __name__ == '__main__':
    unittest.main()
