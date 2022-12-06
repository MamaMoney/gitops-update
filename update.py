import argparse
import logging
import tempfile
from retry import retry
import git
import ruamel.yaml
from git import GitCommandError

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()

parser.add_argument('--file', help='Filename', required=True)
parser.add_argument('--tag', help='New value as is. Add quotes if required', required=True)
parser.add_argument('--repo', help='The gitops repo', required=True)

args = parser.parse_args()
file = args.file
tag = args.tag
repo = args.repo


@retry(GitCommandError, delay=5, tries=3)
def git_commit(filename, repo, tag):
    logging.info(f"Checking out {repo}")
    with tempfile.TemporaryDirectory(dir=".") as tmpdir:
        path = tmpdir + "/" + filename
        git.Repo.clone_from(repo, tmpdir, depth=1)
        git_repo = git.Repo(tmpdir)
        git_repo.create_remote("upstream", url=repo)
        yaml = ruamel.yaml.YAML()
        with open(path) as opened_file:
            data = yaml.load(opened_file)
            if data["image"]["tag"] == tag:
                logging.warning(f"Tag already set, {tag}")
                return
            else:
                data["image"]["tag"] = tag
        with open(path, "w") as opened_file:
            yaml.dump(data, opened_file)
            git_repo.index.add('**')
            git_repo.index.commit(f"GitOps Update {tag}")
            git_repo.remotes.upstream.push().raise_if_error()


git_commit(file, repo, tag)
