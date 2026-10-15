import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from github_api import GitHub, GitHubError
from marketplace_sync import Marketplace
from source_authorization import (AUTHORIZATION_PATH, MAX_AUTHORIZATION_BYTES,
                                  authorization_for_issue, authorized_by_source)


class SourceProofTest(unittest.TestCase):
    def setUp(self):
        self.issue = {"number": 7, "body": "exact request\r\n中文", "user": {"id": 123, "login": "publisher"}}
        self.entry = authorization_for_issue("example/market", self.issue)
        self.document = {"schema_version": 1, "authorizations": [self.entry]}
        self.commit = "a" * 40
        self.github = Mock()
        self.github.api.side_effect = GitHubError(403, "/permission")
        self.refresh()

    def refresh(self, raw=None):
        raw = json.dumps(self.document).encode() if raw is None else raw
        self.record = {"type": "file", "path": AUTHORIZATION_PATH, "encoding": "base64", "size": len(raw),
                       "content": base64.b64encode(raw).decode() + "\n"}
        self.github.public_api.side_effect = [
            {"default_branch": "protected/main"},
            {"object": {"type": "commit", "sha": self.commit}}, self.record]

    def test_scoped_default_branch_proof_recovers_cross_repository_permission_denial(self):
        market = Marketplace(self.github, "example/market")
        market.publisher_control("https://github.com/team/plugin", self.issue)
        paths = [call.args[0] for call in self.github.public_api.call_args_list]
        self.assertEqual(paths, ["/repos/team/plugin", "/repos/team/plugin/git/ref/heads/protected%2Fmain",
                                f"/repos/team/plugin/contents/{AUTHORIZATION_PATH}?ref={self.commit}"])

    def test_body_hash_preserves_exact_unicode_and_line_endings(self):
        self.assertEqual(self.entry['body_sha256'], hashlib.sha256(self.issue['body'].encode()).hexdigest())
        for change in ({"body": "changed"}, {"number": 8}, {"user": {"id": 999, "login": "publisher"}}):
            with self.subTest(change=change):
                self.refresh()
                self.assertFalse(authorized_by_source(self.github, "team/plugin", "example/market", {**self.issue, **change}))
        self.refresh()
        self.assertFalse(authorized_by_source(self.github, "team/plugin", "other/market", self.issue))

    def test_no_proof_does_not_turn_permission_403_into_approval(self):
        self.github.public_api.side_effect = GitHubError(404, "/authorization")
        with self.assertRaisesRegex(ValueError, AUTHORIZATION_PATH):
            Marketplace(self.github, "example/market").publisher_control("https://github.com/team/plugin", self.issue)

    def test_read_only_role_does_not_override_source_explicit_consent(self):
        self.github.api.side_effect = None
        self.github.api.return_value = {"permission": "read"}
        Marketplace(self.github, "example/market").publisher_control("https://github.com/team/plugin", self.issue)

    def test_source_default_branch_and_regular_file_are_required(self):
        self.github.public_api.side_effect = [{"default_branch": "main"}, {"object": {"type": "tag", "sha": self.commit}}]
        with self.assertRaisesRegex(ValueError, "default-branch commit"):
            authorized_by_source(self.github, "team/plugin", "example/market", self.issue)
        for mutation in ({"type": "symlink"}, {"size": MAX_AUTHORIZATION_BYTES + 1},
                         {"size": 1}, {"content": "not base64!"}, {"path": "elsewhere.json"}):
            with self.subTest(mutation=mutation):
                self.refresh()
                self.record.update(mutation)
                with self.assertRaises(ValueError):
                    authorized_by_source(self.github, "team/plugin", "example/market", self.issue)

    def test_duplicate_fields_and_open_ended_authorizations_are_rejected(self):
        cases = [b'{"schema_version":1,"schema_version":1,"authorizations":[]}',
                 b'{"schema_version":1,"authorizations":[{"actor_id":123}]}']
        for raw in cases:
            self.refresh(raw)
            with self.assertRaises(ValueError):
                authorized_by_source(self.github, "team/plugin", "example/market", self.issue)
        self.document['authorizations'] = [copy.deepcopy(self.entry)] * 101
        self.refresh()
        with self.assertRaises(ValueError):
            authorized_by_source(self.github, "team/plugin", "example/market", self.issue)

    def test_public_source_reads_never_receive_registry_token(self):
        tokens = []
        def api(client, path):
            tokens.append(client.token)
            return {"path": path}
        with patch.object(GitHub, "api", api):
            self.assertEqual(GitHub(token="private-registry-token").public_api("/repos/team/plugin"),
                             {"path": "/repos/team/plugin"})
        self.assertEqual(tokens, [""])
        with self.assertRaises(ValueError):
            GitHub(token="private").public_api("/user")

    def test_transient_permission_failure_is_not_misclassified_as_missing_authorization(self):
        self.github.api.side_effect = GitHubError(502, "/permission")
        with self.assertRaises(GitHubError):
            Marketplace(self.github, "example/market").publisher_control("https://github.com/team/plugin", self.issue)
        self.github.public_api.assert_not_called()


if __name__ == '__main__':
    unittest.main()
