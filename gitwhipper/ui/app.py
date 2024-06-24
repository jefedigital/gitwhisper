# gitwhipper/ui/app.py

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel,
                             QMessageBox, QGroupBox, QFormLayout, QListWidget, QSplitter,
                             QMenu, QMenuBar)
from PyQt6.QtCore import Qt
from ..git_utils import (is_substantial_change, commit_changes, 
                         is_git_repo, git_add_all, git_push, get_unstaged_changes, 
                         get_staged_changes, get_last_commit_id, get_staged_commits,
                         get_commit_details)
from ..commit_summary import generate_commit_summary
from ..readme_generator import generate_dynamic_readme

class GitWhipperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitWhipper")
        self.setGeometry(100, 100, 1200, 800)
        self.current_dir = os.getcwd()

        self.setup_ui()

    def setup_ui(self):
        self.setup_menu_bar()
        
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

        # Splitter for left and right columns
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Column
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)

        # Staged Commits List
        commits_group = QGroupBox("Staged Commits")
        commits_layout = QVBoxLayout()
        self.commits_list = QListWidget()
        self.commits_list.itemClicked.connect(self.show_commit_details)
        commits_layout.addWidget(self.commits_list)
        commits_group.setLayout(commits_layout)
        left_layout.addWidget(commits_group)

        # Commit Details (without Diff)
        details_group = QGroupBox("Commit Details")
        details_layout = QVBoxLayout()

        self.commit_id_label = QLabel("Commit ID:")
        details_layout.addWidget(self.commit_id_label)

        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(50)
        details_layout.addWidget(QLabel("Summary:"))
        details_layout.addWidget(self.summary_text)

        self.description_text = QTextEdit()
        details_layout.addWidget(QLabel("Description:"))
        details_layout.addWidget(self.description_text)

        details_group.setLayout(details_layout)
        left_layout.addWidget(details_group)

        splitter.addWidget(left_column)

        # Right Column (Diff)
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)

        diff_group = QGroupBox("Diff")
        diff_layout = QVBoxLayout()
        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        diff_layout.addWidget(self.diff_text)
        diff_group.setLayout(diff_layout)
        right_layout.addWidget(diff_group)

        splitter.addWidget(right_column)

        main_layout.addWidget(splitter)

        # Set the initial sizes of the splitter
        splitter.setSizes([400, 600])  # Adjust these values as needed

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

        # README Generation button
        self.readme_button = QPushButton("Generate README")
        self.readme_button.clicked.connect(self.generate_readme)
        main_layout.addWidget(self.readme_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_git_status()

    def setup_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # File menu
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        browse_action = file_menu.addAction("&Browse Directory")
        browse_action.triggered.connect(self.browse_directory)

        generate_readme_action = file_menu.addAction("&Generate README")
        generate_readme_action.triggered.connect(self.generate_readme)

        exit_action = file_menu.addAction("&Exit")
        exit_action.triggered.connect(self.close)

        # Git menu
        git_menu = QMenu("&Git", self)
        menu_bar.addMenu(git_menu)

        add_action = git_menu.addAction("&Add All")
        add_action.triggered.connect(self.git_add)

        commit_action = git_menu.addAction("&Commit")
        commit_action.triggered.connect(self.commit_changes)

        push_action = git_menu.addAction("&Push")
        push_action.triggered.connect(self.git_push)

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
            self.readme_button.setEnabled(True)
            self.update_staged_commits()
        else:
            self.git_status_label.setText("Not a Git repository")
            self.git_status_label.setStyleSheet("color: red")
            self.add_button.setEnabled(False)
            self.generate_button.setEnabled(False)
            self.commit_button.setEnabled(False)
            self.push_button.setEnabled(False)
            self.readme_button.setEnabled(False)
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

    def generate_readme(self):
        if is_git_repo(self.current_dir):
            generate_dynamic_readme(self.current_dir, self)
        else:
            QMessageBox.warning(self, "Error", "Current directory is not a Git repository.")

    def show_message(self, message):
        QMessageBox.information(self, "GitWhipper", message)

def run_app():
    app = QApplication(sys.argv)
    window = GitWhipperUI()
    window.show()
    sys.exit(app.exec())