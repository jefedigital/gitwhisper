# gitwhipper/ui/app.py

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel,
                             QMessageBox, QGroupBox, QFormLayout, QListWidget, QSplitter)
from PyQt6.QtCore import Qt
from ..git_utils import (is_substantial_change, commit_changes, 
                         is_git_repo, git_add_all, git_push, get_unstaged_changes, 
                         get_staged_changes, get_last_commit_id, get_staged_commits,
                         get_commit_details)
from ..commit_summary import generate_commit_summary

class GitWhipperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitWhipper")
        self.setGeometry(100, 100, 1200, 800)
        self.current_dir = os.getcwd()

        main_layout = QVBoxLayout()

        # Directory navigation
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(f"Current Directory: {self.current_dir}")
        dir_layout.addWidget(self.dir_label)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button)
        main_layout.addLayout(dir_layout)

        # Git repo status
        self.git_status_label = QLabel()
        main_layout.addWidget(self.git_status_label)

        # Splitter for commits list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Staged Commits List
        commits_group = QGroupBox("Staged Commits")
        commits_layout = QVBoxLayout()
        self.commits_list = QListWidget()
        self.commits_list.itemClicked.connect(self.show_commit_details)
        commits_layout.addWidget(self.commits_list)
        commits_group.setLayout(commits_layout)
        splitter.addWidget(commits_group)

        # Commit Details
        details_group = QGroupBox("Commit Details")
        details_layout = QVBoxLayout()
        
        self.commit_id_label = QLabel("Commit ID:")
        details_layout.addWidget(self.commit_id_label)

        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        details_layout.addWidget(QLabel("Diff:"))
        details_layout.addWidget(self.diff_text)

        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(50)
        details_layout.addWidget(QLabel("Summary:"))
        details_layout.addWidget(self.summary_text)

        self.description_text = QTextEdit()
        details_layout.addWidget(QLabel("Description:"))
        details_layout.addWidget(self.description_text)

        details_group.setLayout(details_layout)
        splitter.addWidget(details_group)

        main_layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Git Add")
        self.add_button.clicked.connect(self.git_add)
        button_layout.addWidget(self.add_button)

        self.generate_button = QPushButton("Generate Commit Message")
        self.generate_button.clicked.connect(self.generate_commit_message)
        button_layout.addWidget(self.generate_button)

        self.commit_button = QPushButton("Commit Changes")
        self.commit_button.clicked.connect(self.commit_changes)
        button_layout.addWidget(self.commit_button)

        self.push_button = QPushButton("Git Push")
        self.push_button.clicked.connect(self.git_push)
        button_layout.addWidget(self.push_button)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Update git status after all UI elements are created
        self.update_git_status()

    def browse_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if new_dir:
            self.current_dir = new_dir
            os.chdir(self.current_dir)
            self.dir_label.setText(f"Current Directory: {self.current_dir}")
            self.update_git_status()

    def update_git_status(self):
        if is_git_repo(self.current_dir):
            self.git_status_label.setText("Git repository detected")
            self.git_status_label.setStyleSheet("color: green")
            self.add_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.commit_button.setEnabled(True)
            self.push_button.setEnabled(True)
            self.update_staged_commits()
        else:
            self.git_status_label.setText("Not a Git repository")
            self.git_status_label.setStyleSheet("color: red")
            self.add_button.setEnabled(False)
            self.generate_button.setEnabled(False)
            self.commit_button.setEnabled(False)
            self.push_button.setEnabled(False)
            self.clear_commit_details()
            self.commits_list.clear()

    def update_staged_commits(self):
        self.commits_list.clear()
        staged_commits = get_staged_commits(self.current_dir)
        for commit in staged_commits:
            self.commits_list.addItem(f"{commit['id'][:7]} - {commit['summary']}")

    def show_commit_details(self, item):
        commit_id = item.text().split(' - ')[0]
        details = get_commit_details(self.current_dir, commit_id)
        self.commit_id_label.setText(f"Commit ID: {commit_id}")
        self.diff_text.setPlainText(details['diff'])
        self.summary_text.setPlainText(details['summary'])
        self.description_text.setPlainText(details['description'])

    def clear_commit_details(self):
        self.commit_id_label.setText("Commit ID:")
        self.diff_text.clear()
        self.summary_text.clear()
        self.description_text.clear()

    def git_add(self):
        success, message = git_add_all(self.current_dir)
        self.show_message(message)
        self.update_staged_commits()

    def generate_commit_message(self):
        diff = get_staged_changes(self.current_dir)
        if is_substantial_change(diff):
            suggested_commit_summary = generate_commit_summary(diff)
            summary, description = suggested_commit_summary.split('\n\n', 1)
            self.summary_text.setPlainText(summary)
            self.description_text.setPlainText(description)
        else:
            self.show_message("No substantial changes detected.")

    def commit_changes(self):
        summary = self.summary_text.toPlainText()
        description = self.description_text.toPlainText()
        commit_message = f"{summary}\n\n{description}"
        if commit_changes(self.current_dir, commit_message):
            self.show_message("Changes committed successfully.")
            self.update_staged_commits()
            self.clear_commit_details()
        else:
            self.show_message("Failed to commit changes.")

    def git_push(self):
        success, message = git_push(self.current_dir)
        self.show_message(message)

    def show_message(self, message):
        QMessageBox.information(self, "GitWhipper", message)

def run_app():
    app = QApplication(sys.argv)
    window = GitWhipperUI()
    window.show()
    sys.exit(app.exec())