# gitwhipper/ui/app.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from ..git_utils import get_repo_changes, is_substantial_change, commit_changes
from ..commit_summary import generate_commit_summary

class GitWhipperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitWhipper")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.commit_message = QTextEdit()
        layout.addWidget(self.commit_message)

        self.generate_button = QPushButton("Generate Commit Message")
        self.generate_button.clicked.connect(self.generate_commit_message)
        layout.addWidget(self.generate_button)

        self.commit_button = QPushButton("Commit Changes")
        self.commit_button.clicked.connect(self.commit_changes)
        layout.addWidget(self.commit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def generate_commit_message(self):
        print("Generating commit message...")
        diff = get_repo_changes()
        if is_substantial_change(diff):
            suggested_commit_summary = generate_commit_summary(diff)
            self.commit_message.setPlainText(suggested_commit_summary)
        else:
            self.commit_message.setPlainText("No substantial changes detected.")

    def commit_changes(self):
        print("Committing changes...")
        commit_message = self.commit_message.toPlainText()
        if commit_changes(commit_message=commit_message):
            self.commit_message.setPlainText("Changes committed successfully.")
        else:
            self.commit_message.setPlainText("Failed to commit changes.")

def run_app():
    print("Initializing QApplication...")
    app = QApplication(sys.argv)
    print("Creating GitWhipperUI...")
    window = GitWhipperUI()
    print("Showing window...")
    window.show()
    print("Entering Qt event loop...")
    sys.exit(app.exec())