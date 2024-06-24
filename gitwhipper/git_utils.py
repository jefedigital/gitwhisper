# gitwhipper/git_utils.py

import git
import os

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

def get_commit_details(repo_path='.', commit_id='staged'):
    """Get details (summary, description, diff) for a given commit or staged changes."""
    repo = git.Repo(repo_path)
    if commit_id == 'staged':
        diff = repo.git.diff('--staged')
        return {
            'summary': 'Staged changes',
            'description': '',
            'diff': diff
        }
    else:
        try:
            commit = repo.commit(commit_id)
            return {
                'summary': commit.summary,
                'description': commit.message[len(commit.summary):].strip(),
                'diff': repo.git.show(commit.hexsha)
            }
        except git.GitCommandError as e:
            print(f"Error getting commit details: {str(e)}")
            return {
                'summary': 'Error',
                'description': 'Could not retrieve commit details',
                'diff': ''
            }