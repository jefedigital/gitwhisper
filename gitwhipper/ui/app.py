# gitwhipper/ui/app.py
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel)
from PyQt6.QtCore import Qt
from ..git_utils import get_repo_changes, is_substantial_change, commit_changes, is_git_repo
from ..commit_summary import generate_commit_summary

class GitWhipperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitWhipper")
        self.setGeometry(100, 100, 800, 600)
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

        self.commit_message = QTextEdit()
        main_layout.addWidget(self.commit_message)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Commit Message")
        self.generate_button.clicked.connect(self.generate_commit_message)
        button_layout.addWidget(self.generate_button)

        self.commit_button = QPushButton("Commit Changes")
        self.commit_button.clicked.connect(self.commit_changes)
        button_layout.addWidget(self.commit_button)

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
            self.generate_button.setEnabled(True)
            self.commit_button.setEnabled(True)
        else:
            self.git_status_label.setText("Not a Git repository")
            self.git_status_label.setStyleSheet("color: red")
            self.generate_button.setEnabled(False)
            self.commit_button.setEnabled(False)

    def generate_commit_message(self):
        diff = get_repo_changes(self.current_dir)
        if is_substantial_change(diff):
            suggested_commit_summary = generate_commit_summary(diff)
            self.commit_message.setPlainText(suggested_commit_summary)
        else:
            self.commit_message.setPlainText("No substantial changes detected.")

    def commit_changes(self):
        commit_message = self.commit_message.toPlainText()
        if commit_changes(self.current_dir, commit_message):
            self.commit_message.setPlainText("Changes committed successfully.")
        else:
            self.commit_message.setPlainText("Failed to commit changes.")

def run_app():
    app = QApplication(sys.argv)
    window = GitWhipperUI()
    window.show()
    sys.exit(app.exec())