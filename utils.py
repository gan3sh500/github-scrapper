import os
import re
import json
import uuid
import pprint
import pickle
import requests
from requests.exceptions import ConnectTimeout


BASE_URL = 'https://api.github.com/'


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def dump_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_uuid(seed_string: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_DNS, seed_string)


def read_pickle(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def dump_pickle(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


config = read_json('config.json')


class RateLimiter:
    def __init__(self, max_calls: int, time_limit: float):
        '''
        Class to make safe calls without exceeding max_calls in
        time_limit.
        For github REST API this is
        max_calls = 5000
        time_limit = 3600
        '''
        self.max_calls = max_calls
        self.time_limit = time_limit
        self.calls = 0
        self.start = None
  

    def reset(self):
        self.calls = 0
        self.start = time.time()

    def safe_call(self, func, args):
        if self.start is None:
            self.start = time.time()
        if self.run_time > self.time_limit:
            self.reset()
        if self.calls > self.max_calls:
            time.sleep(self.time_limit - self.run_time)
            self.reset()
        response = func(args)
        self.calls += 1
        return response

    @property
    def run_time(self):
        if self.start is None:
            return 0
        return time.time() - self.start


def call_endpoint(url, headers={'Accept': 'application/vnd.github.v3+json'}, params={}):
    try:
        response = requests.get(url, params=params, auth = ('username', config["authorization_code"]), headers=headers, timeout=5)
    except ConnectTimeout:
        return None
    return response.json()


def get_issues_in_repo(owner, repo, labels=None, page=1):
    url = BASE_URL + f'repos/{owner}/{repo}/issues'
    if labels is None:
        params = {}
    elif isinstance(labels, list):
        params = {'labels':','.join(labels)}
    elif isinstance(labels, str):
        params = {'labels': labels}
    params.update({
        'state': 'all',
        'page': page,
        'per_page': 100,
    })
    response_json = call_endpoint(url, params=params)
    if not isinstance(response_json, list):
        pprint.pprint(response_json, indent=4)
        raise ValueError("Response was not a list")
    issues = []
    for issue in response_json:
        code = extract_code_from_body(issue['body'])
        issues.append({
            'updated_at': issue['updated_at'],
            'state': issue['state'],
            'issue': issue['number'],
            'labels': [x['name'] for x in issue['labels']],
            'body' : issue['body'],
            'body_code': code,
            'title': issue['title']
        })
    return issues


def extract_code_from_body(body: str):
    if not isinstance(body, str):
        raise ValueError('Body of the issue was not text')
    multiline_pattern = re.compile('\r\n[`]+([\w]*)\r\n([^`]+)[`]+')
    multiline_code = multiline_pattern.findall(body)
    singleline_pattern = re.compile('`([^`\n]+)`')
    singleline_code = singleline_pattern.findall(body)
    return multiline_code + singleline_code


def get_modified_files(owner, repo, pr):
    url = BASE_URL + f'repos/{owner}/{repo}/pulls/{pr}/files'
    response_json = call_endpoint(url)
    changed_files = []
    for changed_file in response_json:
        changed_files.append({
            'status': changed_file['status'],
            'filename': changed_file['filename']
        })
    return changed_files


def get_mentioned_pr(owner, repo, issue):
    url = BASE_URL + f'repos/{owner}/{repo}/issues/{issue}/timeline'
    response_json = call_endpoint(url)
    print(response_json)

def get_commits_in_repo(owner, repo, page=1):
    url = BASE_URL + f'repos/{owner}/{repo}/commits'
    params = {
        'page': page,
        'per_page': 100,
    }
    response_json = call_endpoint(url, params=params)
    commits = []
    for index, commit in enumerate(response_json):
        commits.append({
            'id':commit['sha'],
            'time': commit['commit']['committer']['date'],
            })
    return commits

def get_all_commits_in_repo(owner, repo, labels=None):
    all_commits = []
    i = 1
    while(True):
        commits = get_commits_in_repo(owner, repo, page=i)
        if len(commits) > 0:
            all_commits.extend(commits)
            i += 1
        else:
            break
    return all_commits

def test_on_test_issues_repo():
    list_of_keys = ['updated_at', 'state', 'issue', 'labels', 'body', 'body_code', 'title']
    issues = get_all_issues_in_repo('gan3sh500', 'test-issues-repo', labels=['bug'])
    if not isinstance(issues, list):
        raise ValueError('The response is not a list')
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ValueError(f'The issue {index} is not a dict')
        for key in list_of_keys:
            if key not in issue:
                raise ValueError(f'The key {key} is missing in issue {index}')
    pprint.pprint(issues, indent=4)

def test_on_test_issues_repo_commits():
    list_of_keys = ['id', 'time',]
    commits = get_all_commits_in_repo('gan3sh500', 'test-issues-repo')
    if not isinstance(commits, list):
        raise ValueError('The response is not a list')
    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            raise ValueError(f'The issue {index} is not a dict')
        for key in list_of_keys:
            if key not in commit:
                raise ValueError(f'The key {key} is missing in issue {index}')
    pprint.pprint(commits, indent=4)
    
def get_all_issues_in_repo(owner, repo, labels=None):
    all_issues = []
    i = 1
    while(True):
        issues = get_issues_in_repo(owner, repo, labels=labels, page=i)
        if len(issues) > 0:
            all_issues.extend(issues)
            i += 1
        else:
            break
    return all_issues


if __name__ == '__main__':
    test_on_test_issues_repo()
    # test_on_test_issues_repo_commits()