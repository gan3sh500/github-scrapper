import os
import csv
import pathlib
import argparse
import datetime

from utils import dump_json, get_all_issues_in_repo


def make_dataset(owner, repo, dataset_dir):
    issues = get_all_issues_in_repo(owner, repo) 
    dump_path = os.path.join(dataset_dir, f'{owner}_{repo}.json')
    import pdb; pdb.set_trace()
    dump_json(issues, dump_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repos_list', required=True, type=str)
    parser.add_argument('--dataset_dir', required=True, type=str)
    args = parser.parse_args()

    csv_path = args.repos_list
    dataset_dir = args.dataset_dir

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
    timestamped_dataset_dir = pathlib.Path(dataset_dir) / timestamp
    timestamped_dataset_dir.mkdir(parents=True, exist_ok=True)
    with open(csv_path) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            owner, repo = row
            make_dataset(owner, repo, timestamped_dataset_dir)

if __name__ == '__main__':
    main()
