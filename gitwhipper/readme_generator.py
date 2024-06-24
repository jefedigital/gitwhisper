# gitwhipper/readme_generator.py

import os
import git
from gitwhipper import ai_utils
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QMessageBox

class ReadmeReviewDialog(QDialog):
    def __init__(self, readme_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review Generated README")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(readme_content)
        layout.addWidget(self.text_edit)

        save_button = QPushButton("Save README")
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def get_edited_content(self):
        return self.text_edit.toPlainText()
    
def get_default_branch(repo):
    """Determine the default branch of the repository."""
    try:
        return repo.active_branch.name
    except TypeError:
        # Detached HEAD state, try common branch names
        for branch in ['main', 'master', 'develop']:
            try:
                repo.refs[branch]
                return branch
            except IndexError:
                continue
    return None  # If no default branch could be determined

def generate_dynamic_readme(repo_path='.', parent=None):
    """Generate a README.md file for the current Git repository with user review."""
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        QMessageBox.warning(parent, "Error", f"{repo_path} is not a valid Git repository.")
        return

    # Get repository information
    repo_name = os.path.basename(repo.working_tree_dir)
    try:
        remote_url = repo.remotes.origin.url
    except AttributeError:
        remote_url = "No remote URL found"

    # Get list of files (excluding .git directory)
    files = [f for f in os.listdir(repo_path) if os.path.isfile(os.path.join(repo_path, f)) and '.git' not in f]

    # Get commit history (last 5 commits)
    default_branch = get_default_branch(repo)
    if default_branch:
        try:
            commits = list(repo.iter_commits(default_branch, max_count=5))
        except git.exc.GitCommandError:
            commits = []
            QMessageBox.warning(parent, "Warning", f"Could not retrieve commit history for branch '{default_branch}'.")
    else:
        commits = []
        QMessageBox.warning(parent, "Warning", "Could not determine the default branch.")

    # Prepare information for AI to generate README
    repo_info = f"""
    Repository Name: {repo_name}
    Remote URL: {remote_url}
    
    Files in repository:
    {', '.join(files)}
    
    Recent commits:
    {' '.join(commit.message.split('\n')[0] for commit in commits) if commits else "No recent commits found."}
    """

    # Use Claude AI to generate README content
    prompt = f"""
    Based on the following information about a Git repository, generate a comprehensive README.md file. 
    The README should include:
    1. A title (the repository name)
    2. A brief description of the project (infer from the file list and commit messages)
    3. Installation instructions (if applicable, based on the types of files present)
    4. Usage instructions (if applicable, based on the types of files present)
    5. A list of main files/directories and their purposes
    6. Recent changes (based on the commit messages provided, if any)
    7. Contributing guidelines (a generic version)
    8. License information (suggest MIT License if not evident)

    Repository Information:
    {repo_info}

    Please provide ONLY the content for the README.md file, formatted in Markdown.
    """

    readme_content = ai_utils.get_claude_response(prompt)

    # Show dialog for user review and editing
    dialog = ReadmeReviewDialog(readme_content, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        final_content = dialog.get_edited_content()
        
        # Write the README.md file
        readme_path = os.path.join(repo_path, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(final_content)
        
        QMessageBox.information(parent, "Success", f"README.md has been generated and saved to {readme_path}")
    else:
        QMessageBox.information(parent, "Cancelled", "README generation was cancelled.")

if __name__ == "__main__":
    # This is for testing purposes only. In the actual app, it will be called from the main UI.
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    generate_dynamic_readme()
    sys.exit(app.exec())