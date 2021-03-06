import pandas as pd

from utils import read_json


class Dataset:
    def __init__(self, dataset_path):
        self.data = read_json(dataset_path)
        self.commits_df = pd.DataFrame.from_dict(self.data['commits'])
        self.commits_df['time'] = pd.to_datetime(self.commits_df['time'])
        self.issues_df = pd.DataFrame.from_dict(self.data['issues'])
        self.issues_df['updated_at'] = pd.to_datetime(self.issues_df['updated_at'])

    def get_issues_iter(self):
        return (self.issues_df.loc[[i]] for i in range(len(self.issues_df)))

    @property
    def get_issues(self):
        return self.issues_df

    @property
    def get_commits(self):
        return self.commit_df

