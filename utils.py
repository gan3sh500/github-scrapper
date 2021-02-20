import os
import requests
from requests.exceptions import ConnectTimeout
import config
BASE_URL = 'https://api.github.com/'

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


def call_endpoint(url, headers={'Accept': 'application/vnd.github.v3+json'}):
    try:
        response = requests.get(url, auth = ('username', config.authorization_code), headers=headers, timeout=5)
    except ConnectTimeout:
        return None
    return response.json()


def get_issues_in_repo(owner, repo):
    url = BASE_URL + f'repos/{owner}/{repo}/issues'
    response_json = call_endpoint(url)
    print(response_json)
    # issues = []
    # for issue in response_json:
    #     issues.append({
    #         'state': issue['state'],
    #         'issue': issue['number'],
    #         'labels': [x['name'] for x in issues['labels']],
    #         'body': issue['body'],
    #         'title': issue['title']
    #     })
    # return issues


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
    return call_endpoint(url)


if __name__ == '__main__':
    for i in range(100):
        print(i)
        response = get_issues_in_repo('replicate', 'replicate')

    # print(get_modified_files('replicate', 'replicate', '470'))
    # print(get_mentioned_pr('PytorchLightning', 'pytorch-lightning', '5577'))

