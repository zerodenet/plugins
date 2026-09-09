"""Small GitHub client. Tokens are sent only to api.github.com."""
import json
import os
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from validate import no_duplicates, require


class GitHubError(RuntimeError):
    def __init__(self, status, path):
        self.status = status
        super().__init__(f'GitHub HTTP {status}: {path}')


class AssetRedirect(HTTPRedirectHandler):
    max_redirections = 4
    max_repeats = 2

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_asset_url(newurl)
        return Request(newurl, headers={'User-Agent': 'zerodenet-marketplace'})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def check_asset_url(url):
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and parsed.hostname in {
        'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'
    } and not parsed.username and not parsed.password and not parsed.fragment
        and parsed.port in (None, 443), 'asset URL must use GitHub HTTPS release hosting')


def decode_json(raw):
    return json.loads(raw, object_pairs_hook=no_duplicates)


class GitHub:
    def __init__(self, token=None):
        self.token = token if token is not None else os.environ.get('GH_TOKEN', '')

    def api(self, path, method='GET', data=None):
        require(path.startswith('/') and not path.startswith('//'), 'invalid GitHub API path')
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'zerodenet-marketplace',
                   'X-GitHub-Api-Version': '2022-11-28'}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        raw = None if data is None else json.dumps(data).encode()
        if raw is not None:
            headers['Content-Type'] = 'application/json'
        req = Request('https://api.github.com' + path, raw, headers, method=method)
        try:
            with build_opener(NoRedirect).open(req, timeout=30) as response:
                body = response.read(8 * 1024 * 1024 + 1)
                require(len(body) <= 8 * 1024 * 1024, 'GitHub response too large')
                return decode_json(body) if body else None
        except HTTPError as error:
            raise GitHubError(error.code, path) from None

    def pages(self, path):
        separator = '&' if '?' in path else '?'
        for page in range(1, 11):
            rows = self.api(f'{path}{separator}per_page=100&page={page}')
            yield from rows
            if len(rows) < 100:
                return
        raise ValueError('pagination limit exceeded; narrow the repository query')

    def asset(self, url, size):
        check_asset_url(url)
        require(0 < size <= 256 * 1024, 'release metadata must be at most 256 KiB')
        request = Request(url, headers={'User-Agent': 'zerodenet-marketplace'})
        with build_opener(AssetRedirect).open(request, timeout=30) as response:
            data = response.read(256 * 1024 + 1)
        require(len(data) == size, 'metadata download size mismatch')
        return data


def segment(value):
    return quote(str(value), safe='')
