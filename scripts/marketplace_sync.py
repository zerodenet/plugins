#!/usr/bin/env python3
"""Turn first-time plugin applications into reviewed directory proposals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re

from github_api import GitHub, GitHubError, decode_json, segment
from release_metadata import append_entry, listing_entry, submission
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

    def comment(self, number, message):
        marker = '<!-- marketplace-automation -->'
        path = f'{self.prefix}/issues/{number}/comments'
        body = marker + '\n' + message
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

    def propose(self, host, entry, issue):
        base = self.github.api(self.prefix + '/git/ref/heads/main')['object']['sha']
        catalog, blob = self.catalog(host, base)
        updated = append_entry(catalog, entry, host)
        if catalog == updated:
            return None
        branch = f'automation/{host}/{entry["id"]}'
        owner = self.repository.split('/')[0]
        prs = self.github.api(self.prefix + '/pulls?state=all&head=' + segment(owner + ':' + branch))
        if prs:
            return prs[0]
        encoded = base64.b64encode((json.dumps(updated, indent=2, ensure_ascii=False) + '\n').encode()).decode()
        try:
            self.github.api(self.prefix + '/git/refs', 'POST', {'ref': 'refs/heads/' + branch, 'sha': base})
        except GitHubError as error:
            if error.status != 422:
                raise
        previous, previous_blob = self.catalog(host, branch)
        if previous != updated:
            require(previous_blob == blob, 'automation branch no longer matches main')
            self.github.api(f'{self.prefix}/contents/catalogs/{host}.json', 'PUT', {
                'message': f'registry: list {entry["id"]}', 'branch': branch,
                'sha': blob, 'content': encoded,
                'author': {'name': 'github-actions[bot]', 'email': '41898282+github-actions[bot]@users.noreply.github.com'},
            })
        digest = hashlib.sha256((issue.get('body') or '').encode()).hexdigest()
        body = (
            f'Admit {entry["id"]} to the {host} marketplace.\n\n'
            'Review covers purpose, maintainer and signing identity, capability ceiling, release source, '
            'license, security contact and actual host evidence. Future stable, RC and Dev versions remain '
            'in the publisher repository and do not require marketplace issues while they stay inside this boundary.\n\n'
            '审核插件立意、维护与签名身份、能力上限、发行源、许可证、安全联系及实际宿主证据。'
            '后续正式版、RC 与 Dev 版由开发者仓库维护，只要不突破本条目的信任边界，就无需重复提交市场 Issue。\n\n'
            f'Submission: #{issue["number"]}\n<!-- marketplace-submission:{issue["number"]}:{digest} -->\n')
        return self.github.api(self.prefix + '/pulls', 'POST', {
            'title': f'registry: list {entry["id"]}', 'head': branch, 'base': 'main', 'body': body,
        })

    def intake(self, issue):
        if issue.get('pull_request') or issue['state'] != 'open':
            return
        number = issue['number']
        try:
            repository, tag = submission(issue.get('body'))
            host, entry = listing_entry(self.github, repository, tag)
            fresh = self.github.api(f'{self.prefix}/issues/{number}')
            if fresh.get('body') != issue.get('body') or fresh['state'] != 'open':
                return
            proposal = self.propose(host, entry, issue)
        except GitHubError as error:
            if error.status != 404:
                raise
            self.status(number, 'status:needs-info', ['plugin:submission'])
            self.comment(number, 'The onboarding release is unavailable. / 请确认入驻发行已公开。')
            return
        except (ValueError, KeyError, TypeError) as error:
            self.status(number, 'status:needs-info', ['plugin:submission'])
            self.comment(number, 'Application needs attention / 请修正入驻资料：\n\n' + str(error))
            return
        if proposal is None:
            self.status(number, 'status:accepted', ['plugin:submission', 'host:' + host])
            self.comment(number, 'This plugin is listed. Future versions are discovered from its repository. / 插件已入驻，后续版本由宿主从开发者仓库发现。')
            self.github.api(f'{self.prefix}/issues/{number}', 'PATCH', {'state': 'closed', 'state_reason': 'completed'})
        else:
            state = 'status:in-review' if proposal['state'] == 'open' else 'status:closed'
            self.status(number, state, ['plugin:submission', 'host:' + host])
            self.comment(number, f'Marketplace admission proposal / 市场入驻 PR：{proposal["html_url"]}')

    def reconcile(self):
        for issue in self.github.pages(self.prefix + '/issues?state=open'):
            if not issue.get('pull_request') and (
                    issue['title'].startswith('[Plugin]') or
                    any(label['name'] == 'plugin:submission' for label in issue['labels'])):
                self.intake(issue)

    def closed_pr(self, pr):
        if pr['head']['repo'] is None or pr['head']['repo']['full_name'] != self.repository \
                or not pr['head']['ref'].startswith('automation/'):
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
        if not (issue['title'].startswith('[Plugin]') or
                any(label['name'] == 'plugin:submission' for label in issue['labels'])):
            return
        if issue['state'] == 'closed':
            if not any(label['name'] == 'status:accepted' for label in issue['labels']):
                market.status(issue['number'], 'status:closed')
        else:
            market.intake(issue)
    elif event_name == 'pull_request_target':
        market.closed_pr(event['pull_request'])
    else:
        market.reconcile()


if __name__ == '__main__':
    main()
