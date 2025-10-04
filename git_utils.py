# git_utils.py
from git import Repo, GitCommandError
from typing import Optional, Dict, List
import os

def open_local_repo(path: str) -> Repo:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Repo path '{path}' does not exist.")
    return Repo(path)

def get_file_content_at_commit(repo: Repo, commit_sha: str, file_path: str) -> str:
    """
    Return file contents at a specific commit. Raises if file not present.
    """
    try:
        # 'git show {commit_sha}:{file_path}'
        blob = repo.git.show(f"{commit_sha}:{file_path}")
        return blob
    except GitCommandError as e:
        raise FileNotFoundError(f"File '{file_path}' not found at commit {commit_sha}") from e

def list_files_changed_between_commits(repo: Repo, commit_a: str, commit_b: str) -> List[str]:
    """
    Return a list of files that are different between commit_a and commit_b.
    We'll use git diff --name-only
    """
    diff = repo.git.diff('--name-only', commit_a, commit_b)
    if not diff:
        return []
    return diff.splitlines()

def get_all_tracked_files_at_commit(repo: Repo, commit_sha: str) -> List[str]:
    # List all files tracked at a commit using "git ls-tree -r --name-only <commit>"
    out = repo.git.ls_tree('-r', '--name-only', commit_sha)
    if not out:
        return []
    return out.splitlines()
