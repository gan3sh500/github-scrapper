from pathlib import Path
from typing import Dict, List

import cPickle as pkl

from code_parser import parse_text, recurse_on_tree
from utils import get_uuid, read_pickle, dump_pickle


class InferenceEngine(object):
    def __init__(self, repo_dir: str, commit_ids: List[str], pickle_dir='~/save_pkl/'):
        self.repo_dir = Path(repo_dir)
        self.commit_ids = commit_ids
        self.pickle_dir = Path(pickle_dir)
        self.make_namespace()

    @property
    def pickle_filename(self):
        return self.pickle_dir / (f'{get_uuid(self.repo_dir)}.pkl'

    def save_namespace(self):
        self.pickle_dir.mkdir(exist_ok=True, parents=True)
        dump_pickle(self.all_namespaces, self.pickle_filename)
    
    def make_namespace(self):
        if self.pickle_filename.is_file():
            self.all_namespaces = read_pickle(self.pickle_filename)
        else:
            self.all_namespaces = {}
            for commit_id in self.commit_ids:
                self.all_namespaces[commit_id] = self.make_namespace_for_commit(commit_id)
            self.save_namespace()

    def make_namespace_for_commit(self, commit_id: str) -> Dict:
        self.checkout(commit_id)
        filelist = self.repo_dir.glob('**/*.py')
        namespace = {}
        for filename in self.filelist:
            with open(filename, 'r') as f:
                text = f.read()
                tree = parse_text(text)
                names = recurse_on_tree(tree)
                namespace[filename] = set(names)
        return namespace
    
    def checkout(self, commit_id: str):
        subprocess.run(f'git checkout {commit_id}'.split(' '), )
    
    def infer(self, body_code:list, body_text:str, commit_id: str = None) -> Dict:
        target_namespace = []
        if commit_id is not None:
            self.checkout(commit_id)
        for language, code in body_code:
            tree = parse_text(code)
            names = recurse_on_tree(tree)
            target_namespace.extend(names)
        target_namespace = set(target_namespace)
        inferred_files = {}
        for filename, filenamespace in self.namespace.items():
            common_names = filenamespace.intersection(target_namespace)
            if len(common_names) > 0:
                inferred_files[filename] = common_names
        return inferred_files

def test_engine():
    repo_dir = '/mnt/d/Personal/code/test-issues-repo'
    engine = InferenceEngine(repo_dir=repo_dir)
    print(engine.namespace)
    json = { 
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
                    ('', "import SampleClass\r\n'''This could be a comment'''\r\nobj3 = SampleClass()\r\n")
                ],
            }
    result = engine.infer(json['body_code'], json['body'])
    print(result)

if __name__ == '__main__':
    test_engine()