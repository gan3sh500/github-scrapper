from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np
import pickle as pkl
import subprocess
from collections import Counter

from code_parser import parse_names_from_text
from utils import get_uuid, read_pickle, dump_pickle


def match_issue_to_commit(issue, commits):
    matched_df = pd.merge_asof(issue, commits, right_on='time',
                                left_on='updated_at', direction='backward')
    return matched_df



class InferenceEngine(object):
    def __init__(self, repo_dir: str, commit_ids: List[str], pickle_dir='~/save_pkl/', refresh=False):
        self.repo_dir = Path(repo_dir)
        self.commit_ids = commit_ids
        self.pickle_dir = Path(pickle_dir)
        self.refresh = refresh
        self.build()

    @property
    def pickle_filename(self):
        return self.pickle_dir / (f'{get_uuid(str(self.repo_dir))}.pkl')

    def save_namespace(self):
        self.pickle_dir.mkdir(exist_ok=True, parents=True)
        dump_pickle(self.all_namespaces, self.pickle_filename)

    def make_namespace(self):
        if self.pickle_filename.is_file() and not self.refresh:
            self.all_namespaces = read_pickle(self.pickle_filename)
        else:
            self.all_namespaces = {}
            for commit_id in self.commit_ids:
                self.all_namespaces[commit_id] = self.make_namespace_for_commit(commit_id)
            self.save_namespace()

    def build(self):
        self.make_namespace()
        '''
        will work on self.all_namespaces to make the document_matrix
        will save the document_matrix, vocab vector and idf vector.
        repo_file_vec = document_matrix[i] * idf_vector
        '''
        all_names = set()
        for commit, namespace in self.all_namespaces.items():
            commit_names = []
            for _, names in namespace.items():
                commit_names.extend(names)
            all_names.union(commit_names)
        self.vocabulary = sorted(set(all_names))

        self.document_matrices = {}
        for commit, namespace in self.all_namespaces.items():
            file_names = sorted(namespace.keys())
            def file_value(x):
                filename = file_names[x]
                file_counter = Counter(namespace[filename])
                return self.make_vector_from_counter(file_counter, self.vocabulary)
            file_value = np.vectorize(file_value, signature='()->(m)')
            document_matrix = file_value(np.arange(len(file_names)))
            self.document_matrices[commit] = {
                'file_names': file_names,
                'document_matrix': document_matrix
            }

    def make_vector_from_counter(self, counter, vocabulary):
        def index_value(x):
            return counter[vocabulary[x]]

        index_value = np.vectorize(index_value)
        vec = index_value(np.arange(len(vocabulary)))
        return vec

    def make_namespace_for_commit(self, commit_id: str) -> Dict:
        # should be computing idf for the commit here.
        self.checkout(commit_id)
        filelist = self.repo_dir.glob('**/*.py')
        namespace = {}
        for filename in filelist:
            with open(filename, 'r') as f:
                text = f.read()
                names = parse_names_from_text(text)
                # make frequency vector for file on whole vocab.              
                namespace[filename] = names
        return namespace

    def checkout(self, commit_id: str):
        subprocess.run(f'git checkout {commit_id}'.split(' '), cwd=self.repo_dir)

    def infer(self, body_code:list, body_text:str, commit_id: str = None) -> Dict:
        '''

        '''
        target_namespace = []
        for language, code in body_code:
            names = parse_names_from_text(text)
            target_namespace.extend(names)
        # compute frequency vec here instead on the whole vocabulary.
        target_namespace = Counter(target_namespace)
        target_vector = self.make_vector_from_counter(target_namespace, self.vocabulary)
        
        # write the actual tf-idf logic
        inferred_files = {}
        for filename, filenamespace in self.all_namespaces[commit_id].items():
            common_names = filenamespace.intersection(target_namespace)
            if len(common_names) > 0:
                inferred_files[filename] = common_names
        return inferred_files

def test_engine():
    repo_dir = r'/mnt/d/Personal/code/test-issues-repo'
    commit_ids = ['69e519f4baaa286dcd144b429367662c6067b056', '7748a5c447b8fbb029f21320351d9773898371ff']
    engine = InferenceEngine(repo_dir=repo_dir, commit_ids=commit_ids, refresh=True)
    # print(engine.all_namespaces)
    json = {
            'commit_id':'69e519f4baaa286dcd144b429367662c6067b056',
            'body': "What if the issue has multiple code blocks? \
                    Without the specification of language used? and comments inside the code? \
                    Like this?\r\n`\r\nimport SampleClass\r\nobj = SampleClass()\r\n`\r\n \
                    Now with multiple code quotes\r\n``\r\nimport SampleClass\r\nobj1 = SampleClass()\r\n``\r\n \
                    Python can be specified now\r\n```python\r\nimport SampleClass\r\nobj2 = SampleClass()\r\n```\r\n \
                    Oh no, There's a comment now\r\n```\r\nimport SampleClass\r\n'''This could be a comment'''\r\nobj3 = SampleClass()\r\n```",
            'body_code':
                [
                    ('', 'import SampleClass\r\nobj = SampleClass()\r\n'),
                    ('', 'import SampleClass\r\nobj1 = SampleClass()\r\n'),
                    ('python', 'import SampleClass\r\nobj2 = SampleClass()\r\n'),
                    ('', "import SampleClass\r\n'''This could be a comment'''\r\nobj3 = SampleClass()\r\n"),
                    ('', "RuntimeError: Caught RuntimeError in pin memory thread for device 0.\r\n \
                          Original Traceback (most recent call last):\r\n  \
                          File \"/lib/python3.7/site-packages/torch/utils/data/_utils/pin_memory.py\", \
                          line 31, in _pin_memory_loop\r\n   \
                          data = pin_memory(data)\r\n  \
                          File \"/lib/python3.7/site-packages/torch/utils/data/_utils/pin_memory.py\", \
                          line 55, in pin_memory\r\n   \
                          return [pin_memory(sample) for sample in data]\r\n \
                          File \"lib/python3.7/site-packages/torch/utils/data/_utils/pin_memory.py\", \
                          line 55, in <listcomp>\r\n"),
                    ('', 'argument'),
                ],
            }
    result = engine.infer(json['body_code'], json['body'], json['commit_id'])
    print(result)

def test_matching():
    issues = pd.DataFrame.from_dict([
    {
        'updated_at': '2019-12-11T09:50:07Z',
        'body': "i'm confused",
    }])
    commits = pd.DataFrame.from_dict([
    {
        'id': '69696969696',
        'time': '2019-12-11T08:50:06Z'
    },
    {
        'id': '79696969696',
        'time': '2019-12-11T10:50:06Z'
    },
    ])
    commits['time'] = pd.to_datetime(commits['time'])
    issues['updated_at'] = pd.to_datetime(issues['updated_at'])
    matched = match_issue_to_commit(issues, commits)
    print(f'Got : {matched.loc[[0]].id}')
    print('Desired : 69696969696')

if __name__ == '__main__':
    test_engine()
    test_matching()
