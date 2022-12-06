import ruamel.yaml
import git
import tempfile
import logging
import argparse

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()

parser.add_argument('--file', help='Filename', required=True)
parser.add_argument('--tag', help='New value as is. Add quotes if required', required=True)
parser.add_argument('--repo', help='The gitops repo', required=True)

args = parser.parse_args()


def git_commit(filename, repo, value):
    logging.info(f"Checking out {repo}")
    with tempfile.TemporaryDirectory(dir=".", prefix=value) as tmpdir:
        git.Repo.clone_from(repo, tmpdir, depth=1)
        git_repo = git.Repo(tmpdir)
        git_repo.create_remote("upstream", url=repo)
        yaml = ruamel.yaml.YAML()
        try:
            with open(filename) as opened_file:
                data = yaml.load(opened_file)
                if data["image"]["tag"] == value:
                    logging.warning(f"Tag already set, {value}")
                    return
                else:
                    data["image"]["tag"] = value
            with open(filename, "w") as opened_file:
                yaml.dump(data, opened_file)
                repo.index.add([filename])
                repo.index.commit(f"GitOps tag update : {value}")
                repo.remotes.upstream.pull()
                repo.remotes.upstream.push().raise_if_error()
        except FileNotFoundError as e:
            logging.error(e)


git_commit(args.filename, args.repo, args.tag)
