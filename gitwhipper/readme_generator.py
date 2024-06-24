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
    Based on the following information about a Git repository, generate a comprehensive and professional README.md file. 
    This project is a Git workflow assistant that integrates Large Language Models (LLMs) to enhance the development process.

    The README should include:
    1. Title: Use the repository name as the main title.
    
    2. Introduction: 
       - Provide a concise overview of the project's purpose and primary features.
       - Highlight the integration of LLMs in Git workflow assistance without using marketing language.
       - Briefly mention how it aids in documentation generation and workflow enhancement.

    3. Key Features:
       - List and briefly explain the main functionalities of the tool.
       - Describe how LLMs are utilized in specific features (e.g., commit message generation, code review assistance).
       - Mention any unique aspects that set this tool apart from traditional Git clients.

    4. Installation:
       - Provide clear, step-by-step installation instructions.
       - Include any dependencies or prerequisites.

    5. Usage:
       - Offer concise examples of how to use the main features.
       - Include code snippets or command-line examples where appropriate.
       - Explain how to leverage the LLM-assisted features in a typical workflow.

    6. Project Structure:
       - List the main files and directories.
       - Provide a brief description of each component's purpose.

    7. Recent Changes:
       - If available, summarize recent updates or changes based on the provided commit messages.

    8. Contributing:
       - Outline how others can contribute to the project.
       - Mention any coding standards or guidelines to follow.

    9. License:
       - State the project's license (suggest MIT License if not evident from the repository information).

    Maintain a professional and informative tone throughout the document. Focus on providing clear, factual information about the project's capabilities and benefits, avoiding overly enthusiastic or marketing-like language.

    Repository Information:
    {repo_info}

    Please provide ONLY the content for the README.md file, formatted in Markdown. Ensure the document is well-structured, informative, and presents the project in a professional manner.
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