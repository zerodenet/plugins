#!/usr/bin/env python3
"""Maintain submission labels and propose reviewed catalog updates."""
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
STATES = {'status:needs-info', 'status:in-review', 'status:accepted', 'status:closed'}


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

    def propose(self, host, entry, issue=None):
        base = self.github.api(self.prefix + '/git/ref/heads/main')['object']['sha']
        catalog, blob = self.catalog(host, base)
        updated = append_entry(catalog, entry, host)
        if catalog == updated:
            return None
        version = entry['releases'][0]['version']
        branch = f'automation/{host}/{entry["id"]}/{version}'
        prs = self.github.api(self.prefix + '/pulls?state=all&head=' + segment(self.repository.split('/')[0] + ':' + branch))
        if prs:
            # Never reopen a rejected proposal or overwrite a reviewed branch.
            return prs[0]
        encoded = base64.b64encode((json.dumps(updated, indent=2, ensure_ascii=False) + '\n').encode()).decode()
        try:
            self.github.api(self.prefix + '/git/refs', 'POST', {'ref': 'refs/heads/' + branch, 'sha': base})
        except GitHubError as error:
            if error.status != 422:
                raise
            # A previous run may have created its branch before failing to open
            # a PR. Reuse only an exact proposed catalog or an untouched base.
            previous, _ = self.catalog(host, branch)
            require(previous == catalog or previous == updated, 'existing automation branch changed; inspect it before retrying')
        previous, previous_blob = self.catalog(host, branch)
        if previous != updated:
            require(previous_blob == blob, 'automation branch no longer matches main')
            self.github.api(f'{self.prefix}/contents/catalogs/{host}.json', 'PUT', {
                'message': f'registry: add {entry["id"]} {version}', 'branch': branch,
                'sha': blob, 'content': encoded,
                'author': {'name': 'github-actions[bot]', 'email': '41898282+github-actions[bot]@users.noreply.github.com'},
            })
        link = entry['repository'] + '/releases/tag/' + version
        body = (f'Update `{entry["id"]}` for `{host}` from [upstream {version}]({link}).\n\n'
                'Verified: metadata SHA-256, tag/source commit, release asset sizes and GitHub-recorded digests, '
                'host schema, publisher continuity and immutable release history. Plugin binaries were not executed or rebuilt. '
                'Package signatures and publisher ownership still require maintainer review.\n\n'
                '已校验发行元数据、源码提交、GitHub 产物摘要与大小及历史不可变性；安装包验签、公钥归属和实际宿主测试仍由维护者审核。\n\n'
                '- [ ] Publisher/key ownership and package signatures reviewed / 发布者归属及包签名已核验\n'
                '- [ ] Capabilities, migrations and host test evidence reviewed / 能力、迁移及宿主测试证据已审核\n')
        if issue:
            digest = hashlib.sha256((issue.get('body') or '').encode()).hexdigest()
            body += f'\nSubmission: #{issue["number"]}\n<!-- marketplace-submission:{issue["number"]}:{digest} -->\n'
        pr = self.github.api(self.prefix + '/pulls', 'POST', {
            'title': f'registry: {entry["id"]} {version}', 'head': branch, 'base': 'main', 'body': body,
        })
        self.status(pr['number'], 'status:in-review', ['host:' + host, 'plugin:submission' if issue else 'plugin:update'])
        return pr

    def intake(self, issue):
        if issue.get('pull_request') or issue['state'] != 'open':
            return
        number = issue['number']
        try:
            repository, tag = submission(issue.get('body'))
            host, entry = release_entry(self.github, repository, tag)
            # Recheck after network work; an edit or close must invalidate this run.
            fresh = self.github.api(f'{self.prefix}/issues/{number}')
            if fresh.get('body') != issue.get('body') or fresh['state'] != 'open':
                return
            pr = self.propose(host, entry, issue)
        except GitHubError as error:
            if error.status != 404:
                raise
            self.status(number, 'status:needs-info', ['plugin:submission'])
            self.comment(number, 'The public release or tag is unavailable. / 请确认发行已公开且标签存在。')
            return
        except (ValueError, KeyError, TypeError) as error:
            self.status(number, 'status:needs-info', ['plugin:submission'])
            self.comment(number, 'Metadata needs attention / 请修正发行元数据：\n\n' + str(error))
            return
        if pr is None:
            self.status(number, 'status:accepted', ['plugin:submission', 'host:' + host])
            self.comment(number, 'This release is recorded in the main catalog. / 此版本已收录到主分支目录。')
            self.github.api(f'{self.prefix}/issues/{number}', 'PATCH', {'state': 'closed', 'state_reason': 'completed'})
        else:
            state = 'status:in-review' if pr['state'] == 'open' else 'status:closed'
            self.status(number, state, ['plugin:submission', 'host:' + host])
            self.comment(number, f'Marketplace proposal / 市场更新 PR：{pr["html_url"]}\n\n'
                         'Maintainer review is required before inclusion. / 合并审核通过后才会收录。')

    def reconcile(self):
        for issue in self.github.pages(self.prefix + '/issues?state=open'):
            if not issue.get('pull_request') and (issue['title'].startswith('[Plugin]') or any(label['name'] == 'plugin:submission' for label in issue['labels'])):
                self.intake(issue)

    def updates(self):
        failures = []
        for host in sorted(HOSTS):
            catalog, _ = self.catalog(host)
            for old in catalog['plugins']:
                if not old['releases'] or old['publisher']['public_key'] is None:
                    continue
                repository = old['repository'].removeprefix('https://github.com/')
                try:
                    latest = self.github.api(f'/repos/{repository}/releases/latest')
                    actual_host, entry = release_entry(self.github, repository, latest['tag_name'])
                    require(actual_host == host and entry['id'] == old['id'], 'upstream host or plugin ID changed')
                    self.propose(host, entry)
                except (ValueError, KeyError, TypeError, GitHubError) as error:
                    failures.append(f'{host}/{old["id"]}: {error}')
        if failures:
            raise RuntimeError('Some upstream releases require attention:\n' + '\n'.join(failures))

    def closed_pr(self, pr):
        if pr['head']['repo'] is None or pr['head']['repo']['full_name'] != self.repository or not pr['head']['ref'].startswith('automation/'):
            return
        self.status(pr['number'], 'status:accepted' if pr.get('merged') else 'status:closed')
        match = re.search(r'<!-- marketplace-submission:(\d+):([a-f0-9]{64}) -->', pr.get('body') or '')
        if match:
            issue = self.github.api(f'{self.prefix}/issues/{match[1]}')
            if hashlib.sha256((issue.get('body') or '').encode()).hexdigest() == match[2]:
                if pr.get('merged'):
                    self.intake(issue)
                else:
                    self.status(issue['number'], 'status:closed')


def main():
    github = GitHub()
    require(github.token, 'GH_TOKEN is required')
    market = Marketplace(github, os.environ['GITHUB_REPOSITORY'])
    event = decode_json(Path(os.environ['GITHUB_EVENT_PATH']).read_bytes())
    market.labels()
    event_name = os.environ['GITHUB_EVENT_NAME']
    if event_name == 'issues':
        issue = github.api(f'{market.prefix}/issues/{event["issue"]["number"]}')
        if issue['title'].startswith('[Plugin]') or any(label['name'] == 'plugin:submission' for label in issue['labels']):
            if issue['state'] == 'closed':
                if not any(label['name'] == 'status:accepted' for label in issue['labels']):
                    market.status(issue['number'], 'status:closed')
            else:
                market.intake(issue)
    elif event_name == 'pull_request_target':
        market.closed_pr(event['pull_request'])
    else:
        market.reconcile()
        market.updates()


if __name__ == '__main__':
    main()
