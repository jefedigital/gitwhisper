# gitwhipper/git_utils.py

import git
import os
from typing import List, Tuple

def is_git_repo(path):
    """Check if the given path is a Git repository."""
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

def get_unstaged_changes(repo_path='.'):
    """Get unstaged changes in the repository."""
    repo = git.Repo(repo_path)
    return repo.git.diff()

def get_staged_changes(repo_path='.'):
    """Get staged changes in the repository."""
    repo = git.Repo(repo_path)
    return repo.git.diff('--staged')

def is_substantial_change(diff, threshold=10):
    """Determine if changes are substantial based on the number of lines changed."""
    return diff.count('\n') > threshold

def git_add_all(repo_path='.'):
    """Stage all changes in the repository."""
    try:
        repo = git.Repo(repo_path)
        repo.git.add(A=True)
        return True, "All changes staged successfully."
    except git.GitCommandError as e:
        return False, f"Error staging changes: {str(e)}"

def commit_changes(repo_path='.', commit_message=None):
    """Commit staged changes with the given message."""
    if commit_message:
        try:
            repo = git.Repo(repo_path)
            repo.git.commit('-m', commit_message)
            return True
        except git.GitCommandError as e:
            print(f"Error committing changes: {str(e)}")
            return False
    return False

def git_push(repo_path='.'):
    """Push committed changes to the remote repository."""
    try:
        repo = git.Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.push()
        return True, "Changes pushed successfully."
    except git.GitCommandError as e:
        return False, f"Error pushing changes: {str(e)}"

def get_last_commit_id(repo_path='.'):
    """Get the ID of the last commit."""
    try:
        repo = git.Repo(repo_path)
        return repo.head.object.hexsha[:7]  # Return first 7 characters of the commit hash
    except Exception as e:
        print(f"Error getting last commit ID: {str(e)}")
        return "No commits yet"

def get_staged_commits(repo_path='.'):
    """Get information about staged changes (as a pseudo-commit)."""
    repo = git.Repo(repo_path)
    staged_files = repo.index.diff("HEAD")
    if not staged_files:
        return []

    # Get the last commit hash
    last_commit_hash = repo.head.object.hexsha[:7]

    # Since we can't get actual commits for staged changes, we'll create a pseudo-commit
    diff = repo.git.diff('--staged')
    return [{
        'id': last_commit_hash,
        'summary': 'Staged changes',
        'description': '',
        'diff': diff
    }]

def get_commit_details(repo_path='.', commit_id='HEAD'):
    """Get details of a specific commit."""
    repo = git.Repo(repo_path)
    commit = repo.commit(commit_id)
    return {
        'id': commit.hexsha,
        'summary': commit.summary,
        'description': commit.message[len(commit.summary):].strip(),
        'diff': repo.git.show(commit.hexsha),
        'timestamp': commit.committed_date
    }

def get_commits(repo_path='.', count=10):
    """Get a list of recent commits."""
    repo = git.Repo(repo_path)
    commits = []
    for commit in repo.iter_commits(max_count=count):
        commits.append({
            'id': commit.hexsha,
            'summary': commit.summary,
            'description': commit.message[len(commit.summary):].strip(),
            'timestamp': commit.committed_date
        })
    return commits

def get_staged_files(repo_path='.'):
    """Get a list of staged files."""
    repo = git.Repo(repo_path)
    return [item.a_path for item in repo.index.diff('HEAD')]

def get_modified_files(repo_path='.'):
    """Get a list of modified and untracked files."""
    repo = git.Repo(repo_path)
    return [item.a_path for item in repo.index.diff(None)] + repo.untracked_files

# New branching operations

def get_current_branch(repo_path: str = '.') -> str:
    """Get the name of the current active branch."""
    repo = git.Repo(repo_path)
    return repo.active_branch.name

def list_branches(repo_path: str = '.') -> List[str]:
    """List all local branches."""
    repo = git.Repo(repo_path)
    return [branch.name for branch in repo.branches]

def create_branch(repo_path: str = '.', branch_name: str = None, start_point: str = 'HEAD') -> bool:
    """Create a new branch."""
    repo = git.Repo(repo_path)
    try:
        if branch_name is None:
            raise ValueError("Branch name must be provided")
        repo.git.branch(branch_name, start_point)
        return True
    except git.GitCommandError:
        return False

def switch_branch(repo_path: str = '.', branch_name: str = None) -> Tuple[bool, str]:
    """Switch to a different branch."""
    repo = git.Repo(repo_path)
    try:
        repo.git.checkout(branch_name)
        return True, f"Switched to branch '{branch_name}'"
    except git.GitCommandError as e:
        return False, str(e)

def delete_branch(repo_path: str = '.', branch_name: str = None, force: bool = False) -> Tuple[bool, str]:
    """Delete a local branch."""
    repo = git.Repo(repo_path)
    try:
        if force:
            repo.git.branch('-D', branch_name)
        else:
            repo.git.branch('-d', branch_name)
        return True, f"Deleted branch '{branch_name}'"
    except git.GitCommandError as e:
        return False, str(e)

def merge_branch(repo_path: str = '.', branch_name: str = None) -> Tuple[bool, str]:
    """Merge a branch into the current branch."""
    repo = git.Repo(repo_path)
    try:
        repo.git.merge(branch_name)
        return True, f"Merged branch '{branch_name}' into current branch"
    except git.GitCommandError as e:
        return False, str(e)

def rebase_branch(repo_path: str = '.', onto_branch: str = None) -> Tuple[bool, str]:
    """Rebase the current branch onto another branch."""
    repo = git.Repo(repo_path)
    try:
        repo.git.rebase(onto_branch)
        return True, f"Rebased current branch onto '{onto_branch}'"
    except git.GitCommandError as e:
        return False, str(e)

def push_branch(repo_path: str = '.', branch_name: str = None, remote: str = 'origin') -> Tuple[bool, str]:
    """Push a branch to a remote repository."""
    repo = git.Repo(repo_path)
    try:
        if branch_name:
            repo.git.push(remote, branch_name)
        else:
            repo.git.push()
        return True, f"Pushed {'current' if not branch_name else branch_name} branch to {remote}"
    except git.GitCommandError as e:
        return False, str(e)

def pull_changes(repo_path: str = '.', remote: str = 'origin', branch: str = None) -> Tuple[bool, str]:
    """Pull changes from the remote counterpart of the current or specified branch."""
    repo = git.Repo(repo_path)
    try:
        if branch:
            repo.git.pull(remote, branch)
        else:
            repo.git.pull()
        return True, f"Pulled changes from {remote}"
    except git.GitCommandError as e:
        return False, str(e)

def create_and_switch_branch(repo_path: str = '.', branch_name: str = None) -> Tuple[bool, str]:
    """Create a new branch and immediately switch to it."""
    repo = git.Repo(repo_path)
    try:
        repo.git.checkout('-b', branch_name)
        return True, f"Created and switched to new branch '{branch_name}'"
    except git.GitCommandError as e:
        return False, str(e)

def rename_branch(repo_path: str = '.', old_name: str = None, new_name: str = None) -> Tuple[bool, str]:
    """Rename an existing branch."""
    repo = git.Repo(repo_path)
    try:
        repo.git.branch('-m', old_name, new_name)
        return True, f"Renamed branch '{old_name}' to '{new_name}'"
    except git.GitCommandError as e:
        return False, str(e)

def get_branch_history(repo_path: str = '.', branch_name: str = None, max_count: int = 10) -> List[dict]:
    """Get the commit history of a branch."""
    repo = git.Repo(repo_path)
    try:
        if branch_name:
            commits = list(repo.iter_commits(branch_name, max_count=max_count))
        else:
            commits = list(repo.iter_commits(max_count=max_count))
        return [{'sha': commit.hexsha, 'message': commit.message.strip(), 'author': str(commit.author), 'date': commit.committed_datetime} for commit in commits]
    except git.GitCommandError as e:
        return []

def create_tag(repo_path: str = '.', tag_name: str = None, message: str = None) -> Tuple[bool, str]:
    """Create a new tag."""
    repo = git.Repo(repo_path)
    try:
        if message:
            repo.create_tag(tag_name, message=message)
        else:
            repo.create_tag(tag_name)
        return True, f"Created tag '{tag_name}'"
    except git.GitCommandError as e:
        return False, str(e)

def list_tags(repo_path: str = '.') -> List[str]:
    """List all tags."""
    repo = git.Repo(repo_path)
    return [tag.name for tag in repo.tags]

def delete_tag(repo_path: str = '.', tag_name: str = None) -> Tuple[bool, str]:
    """Delete a tag."""
    repo = git.Repo(repo_path)
    try:
        repo.delete_tag(tag_name)
        return True, f"Deleted tag '{tag_name}'"
    except git.GitCommandError as e:
        return False, str(e)