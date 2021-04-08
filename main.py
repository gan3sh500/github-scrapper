from dataset_iterate import Dataset
from inference import InferenceEngine, match_issue_to_commit
import pprint

if __name__ == '__main__':
    dataset = Dataset("/mnt/d/Personal/data/github-scrapper/issues/2021_03_18_20_13_15/PyTorchLightning_lightning-bolts.json")
    commit_ids = list(str(x) for x in set(match_issue_to_commit(dataset.get_issues, dataset.get_commits).id))
    engine = InferenceEngine(repo_dir="/mnt/d/Personal/data/github-scrapper/repos/lightning-bolts",
                             commit_ids=commit_ids,
                             pickle_dir='./saved_models/',
                             refresh=True
    )
    for issue in dataset.get_issues_iter():
        data = match_issue_to_commit(issue, dataset.get_commits)
        result = engine.infer(data.body_code[0], data.body[0], str(data.id[0]))
        pprint.pprint(data.body[0])
        pprint.pprint(result)
        # import pdb; pdb.set_trace()