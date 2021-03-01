from pathlib import Path
from code_parser import parse_text, recurse_on_tree

class InferenceEngine(object):
    def __init__(self, repo_dir: str):
        self.repo_dir = Path(repo_dir)
        self.filelist = self.repo_dir.glob('**/*.py')
        self.namespace = {}
        for filename in self.filelist:
            with open(filename, 'r') as f:
                text = f.read()
                tree = parse_text(text)
                names = recurse_on_tree(tree)
                self.namespace[filename] = set(names)
        
    def infer(self, body_code:list, body_text:str):
        target_namespace = []
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