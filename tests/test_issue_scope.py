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


if __name__ == '__main__':
    unittest.main()
