from dataset_iterate import Dataset
from inference import InferenceEngine, match_issue_to_commit
import pprint
from pathlib import Path
from evaluator import precision_calc, recall_calc
import pdb

if __name__ == '__main__':

    dataset = Dataset("../2021_04_06_20_13_23/PyTorchLightning_lightning-bolts.json")
    commit_ids = list(str(x) for x in set(match_issue_to_commit(dataset.get_issues, dataset.get_commits).id))
    repo_dir = Path('../repos/lightning-bolts')
    engine = InferenceEngine(repo_dir=repo_dir,
                             commit_ids=commit_ids,
                             pickle_dir='./saved_models/',
                             refresh=False
    )
    precision_total = []
    recall_total = []

    for issue in dataset.get_issues_iter():
        data = match_issue_to_commit(issue, dataset.get_commits)
        issue_id = data.issue[0]
        relevant_files = dataset.get_relevant_files_for_issue(str(issue_id))
        if len(relevant_files) == 0 or len(data.body_code[0]) == 0:
            continue
        result = engine.infer(data.body_code[0], data.body[0], str(data.id[0]))
        retrieved_files = [str(x.relative_to(repo_dir)) for x in result.keys()]
        

        print('Body')
        pprint.pprint(data.body[0])
        print('Retrieved')
        pprint.pprint(retrieved_files)
        print('Relevant') 
        pprint.pprint(relevant_files)

        precision = precision_calc(retrieved_files, relevant_files)
        recall = recall_calc(retrieved_files, relevant_files)
        precision_total.append(precision)
        recall_total.append(recall)
