from dataset_iterate import Dataset
from inference import InferenceEngine, match_issue_to_commit
import pprint
from pathlib import Path
from evaluator import precision_calc, recall_calc
import pdb
import subprocess
import csv
import argparse
from utils import dump_json



def evaluate_repo(repo_json, repo_dir):
    dataset = Dataset(repo_json)
    commit_ids = list(str(x) for x in set(match_issue_to_commit(dataset.get_issues, dataset.get_commits).id))
    repo_dir = Path(repo_dir)
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

        precision = precision_calc(retrieved_files, relevant_files)
        recall = recall_calc(retrieved_files, relevant_files)
        precision_total.append(precision)
        recall_total.append(recall)

    return precision_total, recall_total


def clone_repo(owner, repo, path):
    subprocess.run(f'git clone https://github.com/{owner}/{repo}.git'.split(' '), cwd=path)


def main(repo_csv, jsons_dir, repos_path, save_dir):
    jsons_dir = Path(jsons_dir)
    repos_path = Path(repos_path)
    save_dir = Path(save_dir)
    results = {}
    with open(repo_csv) as f:
        csvreader = csv.reader(f)
        for owner, repo in csvreader:
            json_file = jsons_dir / f'{owner}_{repo}.json'
            output_repo_path = repos_path / f'{repo}/'
            if not output_repo_path.exists():
                clone_repo(owner, repo, repos_path)
            precision, recall = evaluate_repo(json_file, output_repo_path)
            results[f'{owner}_{repo}'] = {
                'precision': precision,
                'recall': recall
            }
    save_dir.mkdir(exist_ok=True, parents=True)
    dump_json(results, save_path/f'{jsons_dir.stem}.json')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repos_file', type=Path)
    parser.add_argument('--json_dir', type=Path)
    parser.add_argument('--repos_path', type=Path)
    parser.add_argument('--results_dir', type=Path)
    return parser.parse_args()
if __name__ == '__main__':
    args = parse_args()
    main(args.repos_file, 
         args.json_dir,
         args.repos_path,
         args.results_dir)