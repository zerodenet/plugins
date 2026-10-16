#!/usr/bin/env python3
"""Review submissions in issues and publish only on maintainer approval."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re

from github_api import GitHub, GitHubError, decode_json, segment
from release_metadata import append_entry, release_entry, submission
from validate import HOSTS, require

ROOT = Path(__file__).resolve().parents[1]
STATES = {'status:needs-info', 'status:in-review', 'status:approved', 'status:accepted', 'status:closed'}


class Marketplace:
    def __init__(self, github, repository):
        require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository), 'invalid market repository')
        self.github, self.repository = github, repository
        self.prefix = f'/repos/{repository}'

    def labels(self):
        existing = {label['name']: label for label in self.github.pages(self.prefix + '/labels')}
        for label in json.loads((ROOT / '.github/labels.json').read_text()):
            old = existing.get(label['name'])
            if old is None:
                self.github.api(self.prefix + '/labels', 'POST', label)
            elif any(old.get(field) != label[field] for field in ('color', 'description')):
                self.github.api(self.prefix + '/labels/' + segment(label['name']), 'PATCH', label)

    def status(self, number, state, extra=()):
        path = f'{self.prefix}/issues/{number}'
        current = self.github.api(path)
        names = {label['name'] for label in current['labels']}
        desired_hosts = set(extra) & {'host:zboard', 'host:znet-sink'}
        stale_hosts = (names & {'host:zboard', 'host:znet-sink'}) - desired_hosts if desired_hosts else set()
        for label in sorted(((names & STATES) - {state}) | stale_hosts):
            self.github.api(path + '/labels/' + segment(label), 'DELETE')
        add = ({state} | set(extra)) - names
        if add:
            self.github.api(path + '/labels', 'POST', {'labels': sorted(add)})

    def comment(self, number, text):
        marker = '<!-- marketplace-automation -->'
        path = f'{self.prefix}/issues/{number}/comments'
        body = marker + '\n' + text
        for comment in self.github.pages(path):
            if comment['user']['login'] == 'github-actions[bot]' and comment['body'].startswith(marker):
                if comment['body'] != body:
                    self.github.api(f'{self.prefix}/issues/comments/{comment["id"]}', 'PATCH', {'body': body})
                return
        self.github.api(path, 'POST', {'body': body})

    def catalog(self, host, ref='main'):
        require(host in HOSTS, 'unsupported host')
        record = self.github.api(f'{self.prefix}/contents/catalogs/{host}.json?ref={segment(ref)}')
        require(record.get('encoding') == 'base64', 'catalog is not a GitHub text blob')
        return decode_json(base64.b64decode(record['content'])), record['sha']

    @staticmethod
    def review_digest(issue, host, entry):
        raw = json.dumps([issue.get('body'), host, entry], sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()

    def reviewed(self, number, digest, approved_at=None):
        marker = f'<!-- marketplace-review:{digest} -->'
        return any(comment['user']['login'] == 'github-actions[bot]'
                   and comment['body'].startswith('<!-- marketplace-automation -->')
                   and marker in comment['body']
                   and (approved_at is None or comment.get('updated_at', '') < approved_at
                        and bool(comment.get('updated_at')))
                   for comment in self.github.pages(f'{self.prefix}/issues/{number}/comments'))

    def prepare_review(self, issue, host, entry):
        number = issue['number']
        digest = self.review_digest(issue, host, entry)
        version = entry['releases'][0]['version']
        self.comment(number, (
            f'Review `{entry["id"]}` `{version}` for `{host}`. / 请审核此插件发行。\n\n'
            'Metadata, source tag, GitHub asset sizes/digests and catalog history validated. '
            'Packages were not executed. Verify publisher/key ownership, package signatures, '
            'capabilities, migrations and actual host tests, then apply `status:approved`.\n\n'
            '已校验元数据、源码标签、GitHub 产物大小及摘要和目录历史。'
            '维护者核验发布者及公钥归属、包签名、能力、迁移与实际宿主测试后，添加 `status:approved`，'
            'Action 将直接更新所属宿主目录，无需 PR。\n\n'
            f'Review fingerprint / 审核指纹: `{digest}`\n<!-- marketplace-review:{digest} -->'))
        self.status(number, 'status:in-review', ['plugin:submission', 'host:' + host])

    def publish(self, issue, host, entry, digest, actor, approved_at):
        # Contents API uses the current blob SHA as a compare-and-swap guard.
        # A concurrent catalog edit fails instead of overwriting another release.
        catalog, blob = self.catalog(host)
        updated = append_entry(catalog, entry, host)
        fresh = self.github.api(f'{self.prefix}/issues/{issue["number"]}')
        require(fresh['state'] == 'open' and fresh.get('body') == issue.get('body')
                and any(label['name'] == 'status:approved' for label in fresh['labels'])
                and self.reviewed(issue['number'], digest, approved_at),
                'submission or approval changed; review again')
        if catalog != updated:
            encoded = base64.b64encode((json.dumps(updated, indent=2, ensure_ascii=False) + '\n').encode()).decode()
            version = entry['releases'][0]['version']
            self.github.api(f'{self.prefix}/contents/catalogs/{host}.json', 'PUT', {
                'message': f'registry: add {entry["id"]} {version} (#{issue["number"]})\n\nApproved-by: {actor}\nReview: {digest}',
                'branch': 'main', 'sha': blob, 'content': encoded,
                'author': {'name': 'github-actions[bot]', 'email': '41898282+github-actions[bot]@users.noreply.github.com'},
            })
        self.finish(issue, host)

    def finish(self, issue, host):
        self.status(issue['number'], 'status:accepted', ['plugin:submission', 'host:' + host])
        self.comment(issue['number'], 'This release is recorded in the main catalog. / 此版本已收录到主分支目录。')
        self.github.api(f'{self.prefix}/issues/{issue["number"]}', 'PATCH', {'state': 'closed', 'state_reason': 'completed'})

    def intake(self, issue, approval=None):
        if issue.get('pull_request') or issue['state'] != 'open':
            return
        number = issue['number']
        try:
            repository, tag = submission(issue.get('body'))
            host, entry = release_entry(self.github, repository, tag)
            catalog, _ = self.catalog(host)
            updated = append_entry(catalog, entry, host)
            fresh = self.github.api(f'{self.prefix}/issues/{number}')
            if fresh.get('body') != issue.get('body') or fresh['state'] != 'open':
                return
            if updated == catalog:
                self.finish(issue, host)
                return
            digest = self.review_digest(issue, host, entry)
            if approval is not None:
                # The event is GitHub's authenticated label event, not issue text.
                require(approval.get('action') == 'labeled'
                        and approval.get('label', {}).get('name') == 'status:approved'
                        and approval['issue']['number'] == number, 'approval must be a label event')
                actor = approval['sender']['login']
                permission = self.github.api(self.prefix + '/collaborators/' + segment(actor) + '/permission')
                require(permission.get('permission') in {'admin', 'maintain', 'write'},
                        'approval requires repository write, maintain or admin permission')
                if (approval['issue'].get('body') != issue.get('body')
                        or not self.reviewed(number, digest, approval['issue']['updated_at'])):
                    self.prepare_review(issue, host, entry)
                    return
                if not any(label['name'] == 'status:approved' for label in fresh['labels']):
                    return
                self.publish(issue, host, entry, digest, actor, approval['issue']['updated_at'])
            else:
                self.prepare_review(issue, host, entry)
        except GitHubError as error:
            # API/branch protection failures are operational failures, not bad
            # publisher metadata. Keep the review fingerprint for a safe retry.
            if error.status != 404 or approval is not None:
                raise
            self.status(number, 'status:needs-info', ['plugin:submission'])
            self.comment(number, 'The public release or tag is unavailable. / 请确认发行已公开且标签存在。')
        except (ValueError, KeyError, TypeError) as error:
            self.status(number, 'status:needs-info', ['plugin:submission'])
            self.comment(number, 'Review required / 需要重新审核：\n\n' + str(error))

    @staticmethod
    def is_submission(issue):
        return not issue.get('pull_request') and (
            issue['title'].startswith('[Plugin]') or any(
                label['name'] in {'plugin:submission', 'plugin:update'} for label in issue['labels']))

    def reconcile(self):
        for issue in self.github.pages(self.prefix + '/issues?state=open'):
            if self.is_submission(issue) and not any(
                    label['name'] == 'status:approved' for label in issue['labels']):
                self.intake(issue)

    def updates(self):
        failures = []
        issues = list(self.github.pages(self.prefix + '/issues?state=all'))
        for host in sorted(HOSTS):
            catalog, _ = self.catalog(host)
            for old in catalog['plugins']:
                if not old['releases'] or old['publisher']['public_key'] is None:
                    continue
                repository = old['repository'].removeprefix('https://github.com/')
                try:
                    latest = self.github.api(f'/repos/{repository}/releases/latest')
                    tag = latest['tag_name']
                    actual_host, entry = release_entry(self.github, repository, tag)
                    require(actual_host == host and entry['id'] == old['id'], 'upstream host or plugin ID changed')
                    if append_entry(catalog, entry, host) == catalog:
                        continue
                    # Both author submissions and closed/rejected requests prevent
                    # duplicate update issues. Nothing is reopened automatically.
                    def matches(issue):
                        if not self.is_submission(issue):
                            return False
                        try:
                            return submission(issue.get('body')) == (repository, tag)
                        except ValueError:
                            return False
                    if any(matches(issue) for issue in issues):
                        continue
                    issue = self.github.api(self.prefix + '/issues', 'POST', {
                        'title': f'[Plugin] {entry["id"]} {tag}',
                        'body': ('Upstream release discovered; maintainer review required. / 发现上游新版，等待维护者审核。\n\n'
                                 f'https://github.com/{repository}/releases/download/{tag}/marketplace-entry.json'),
                        'labels': ['plugin:submission', 'plugin:update', 'host:' + host],
                    })
                    issues.append(issue)
                    # GITHUB_TOKEN-created events do not start another workflow.
                    self.intake(issue)
                except (ValueError, KeyError, TypeError, GitHubError) as error:
                    failures.append(f'{host}/{old["id"]}: {error}')
        if failures:
            raise RuntimeError('Some upstream releases require attention:\n' + '\n'.join(failures))

    def issue_event(self, event):
        issue = self.github.api(f'{self.prefix}/issues/{event["issue"]["number"]}')
        if not self.is_submission(issue):
            return
        names = {label['name'] for label in issue['labels']}
        if issue['state'] == 'closed':
            if 'status:accepted' not in names:
                self.status(issue['number'], 'status:closed')
        elif event.get('action') == 'labeled' and event.get('label', {}).get('name') == 'status:approved':
            self.intake(issue, approval=event)
        elif event.get('action') in {'opened', 'edited', 'reopened'}:
            self.intake(issue)
        elif 'status:approved' not in names:
            self.intake(issue)


def main():
    github = GitHub()
    require(github.token, 'GH_TOKEN is required')
    market = Marketplace(github, os.environ['GITHUB_REPOSITORY'])
    event = decode_json(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes())
    market.labels()
    event_name = os.environ['GITHUB_EVENT_NAME']
    if event_name == 'issues':
        market.issue_event(event)
    else:
        market.reconcile()
        market.updates()


if __name__ == '__main__':
    main()
