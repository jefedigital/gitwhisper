# gitwhipper/ui/app.py

import sys
import os
import git
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel,
                             QMessageBox, QGroupBox, QFormLayout, QListWidget, QSplitter,
                             QMenu, QMenuBar, QTabWidget, QTreeView, QAbstractItemView,
                             QInputDialog)
from PyQt6.QtCore import Qt, QDir, QModelIndex
from PyQt6.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem, QDragEnterEvent, QDropEvent, QTextCharFormat, QBrush, QTextCursor
from ..git_utils import (is_substantial_change, commit_changes, 
                         is_git_repo, git_add_all, git_push, get_unstaged_changes, 
                         get_staged_changes, get_commits, get_staged_files,
                         get_commit_details, get_modified_files, get_current_branch,
                         list_branches, create_branch, switch_branch, delete_branch,
                         merge_branch, rebase_branch, push_branch, pull_changes,
                         create_and_switch_branch, rename_branch, get_branch_history)
from ..commit_summary import generate_commit_summary
from ..readme_generator import generate_dynamic_readme

class FileSystemModel(QStandardItemModel):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.setHorizontalHeaderLabels(['Name'])
        self.populate_model()

    def populate_model(self):
        root_node = self.invisibleRootItem()
        self.add_files(root_node, self.root_path)

    def add_files(self, parent, path):
        for name in os.listdir(path):
            if name.startswith('.'):
                continue
            full_path = os.path.join(path, name)
            item = QStandardItem(name)
            item.setData(full_path, Qt.ItemDataRole.UserRole)
            parent.appendRow(item)
            if os.path.isdir(full_path):
                self.add_files(item, full_path)

class GitWhipperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitWhipper")
        self.setGeometry(100, 100, 1400, 800)
        self.current_dir = os.getcwd()
        self.modified_files = set()
        self.staged_files = set()

        self.setup_ui()

    def setup_ui(self):
        self.setup_menu_bar()
        
        main_layout = QVBoxLayout()

        # Project section
        project_group = QGroupBox("Project")
        project_layout = QVBoxLayout()
        
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(f"Current Directory: {self.current_dir}")
        dir_layout.addWidget(self.dir_label)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button)
        project_layout.addLayout(dir_layout)

        self.readme_button = QPushButton("Generate README")
        self.readme_button.clicked.connect(self.generate_readme)
        project_layout.addWidget(self.readme_button)

        project_group.setLayout(project_layout)
        main_layout.addWidget(project_group)

        # Git repo status
        self.git_status_label = QLabel()
        main_layout.addWidget(self.git_status_label)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Staging tab
        staging_tab = QWidget()
        staging_layout = QHBoxLayout(staging_tab)

        # Left column for Branching
        branching_group = QGroupBox("Branching")
        branching_layout = QVBoxLayout()

        # Current branch display
        self.current_branch_label = QLabel()
        branching_layout.addWidget(self.current_branch_label)

        # Branch list
        self.branch_list = QListWidget()
        self.branch_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.branch_list.customContextMenuRequested.connect(self.show_branch_context_menu)
        branching_layout.addWidget(self.branch_list)

        # Branch operations buttons
        branch_buttons_layout = QHBoxLayout()
        self.new_branch_button = QPushButton("New Branch")
        self.new_branch_button.clicked.connect(self.create_new_branch)
        branch_buttons_layout.addWidget(self.new_branch_button)

        self.delete_branch_button = QPushButton("Delete Branch")
        self.delete_branch_button.clicked.connect(self.delete_selected_branch)
        branch_buttons_layout.addWidget(self.delete_branch_button)

        self.merge_branch_button = QPushButton("Merge Branch")
        self.merge_branch_button.clicked.connect(self.merge_selected_branch)
        branch_buttons_layout.addWidget(self.merge_branch_button)

        branching_layout.addLayout(branch_buttons_layout)

        branching_group.setLayout(branching_layout)
        staging_layout.addWidget(branching_group)

        # Middle column for Files
        files_group = QGroupBox("Files")
        files_layout = QVBoxLayout()
        self.file_tree = QTreeView()
        self.file_tree.setDragEnabled(True)
        self.file_tree.setAcceptDrops(False)
        self.file_tree.setDropIndicatorShown(True)
        self.file_tree.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.file_model = FileSystemModel(self.current_dir)
        self.file_tree.setModel(self.file_model)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_file_context_menu)
        files_layout.addWidget(self.file_tree)
        
        self.stage_all_button = QPushButton("Stage All")
        self.stage_all_button.clicked.connect(self.git_add_all)
        files_layout.addWidget(self.stage_all_button)
        
        files_group.setLayout(files_layout)
        staging_layout.addWidget(files_group)

        # Right column for Staged Files
        staged_group = QGroupBox("Staged Files")
        staged_layout = QVBoxLayout()
        self.staged_list = QListWidget()
        self.staged_list.setAcceptDrops(True)
        self.staged_list.setDragEnabled(True)
        self.staged_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.staged_list.itemClicked.connect(self.show_staged_file_diff)
        self.staged_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.staged_list.customContextMenuRequested.connect(self.show_staged_file_context_menu)
        staged_layout.addWidget(self.staged_list)
        
        self.commit_button = QPushButton("Commit Changes")
        self.commit_button.clicked.connect(self.commit_changes)
        staged_layout.addWidget(self.commit_button)
        
        staged_group.setLayout(staged_layout)
        staging_layout.addWidget(staged_group)

        self.tab_widget.addTab(staging_tab, "Staging")

        # Commits tab
        commits_tab = QWidget()
        commits_layout = QHBoxLayout(commits_tab)

        # Left column for Commits list and Details
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)

        # Commits List
        commits_group = QGroupBox("Commits")
        commits_list_layout = QVBoxLayout()
        self.commits_list = QListWidget()
        self.commits_list.itemClicked.connect(self.show_commit_details)
        commits_list_layout.addWidget(self.commits_list)
        commits_group.setLayout(commits_list_layout)
        left_layout.addWidget(commits_group)

        # Commit Details
        details_group = QGroupBox("Details")
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

        # Buttons for Commits tab
        commits_button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Commit Message")
        self.generate_button.clicked.connect(self.generate_commit_message)
        commits_button_layout.addWidget(self.generate_button)

        self.push_button = QPushButton("Git Push")
        self.push_button.clicked.connect(self.git_push)
        commits_button_layout.addWidget(self.push_button)

        left_layout.addLayout(commits_button_layout)

        commits_layout.addWidget(left_column)

        # Right column for Diff View
        diff_group = QGroupBox("Diff")
        diff_layout = QVBoxLayout()
        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        diff_layout.addWidget(self.diff_text)
        diff_group.setLayout(diff_layout)
        commits_layout.addWidget(diff_group)

        self.tab_widget.addTab(commits_tab, "Commits")

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
            self.stage_all_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.commit_button.setEnabled(True)
            self.push_button.setEnabled(True)
            self.readme_button.setEnabled(True)
            self.update_commits_list()
            self.update_staged_files_list()
            self.update_file_tree()
            self.update_branching_panel()
        else:
            self.git_status_label.setText("Not a Git repository")
            self.git_status_label.setStyleSheet("color: red")
            self.stage_all_button.setEnabled(False)
            self.generate_button.setEnabled(False)
            self.commit_button.setEnabled(False)
            self.push_button.setEnabled(False)
            self.readme_button.setEnabled(False)
            self.clear_commit_details()
            self.commits_list.clear()
            self.staged_list.clear()

    def update_file_tree(self):
        self.modified_files = set(get_modified_files(self.current_dir))
        self.staged_files = set(get_staged_files(self.current_dir))
        self.file_model = FileSystemModel(self.current_dir)
        self.file_tree.setModel(self.file_model)
        self.highlight_files(self.file_model.invisibleRootItem())

    def highlight_files(self, parent_item):
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row)
            file_path = child_item.data(Qt.ItemDataRole.UserRole)
            if file_path in self.modified_files:
                child_item.setForeground(QColor('red'))
            if file_path in self.staged_files:
                child_item.setForeground(QColor('green'))
            if child_item.hasChildren():
                self.highlight_files(child_item)

    def git_add_file(self, file_path):
        try:
            repo = git.Repo(self.current_dir)
            repo.git.add(file_path)
            self.update_staged_files_list()
            self.update_file_tree()
            # Removed the confirmation popup
        except git.GitCommandError as e:
            QMessageBox.warning(self, "Error", f"Failed to add {file_path}: {str(e)}")

    def git_remove_file(self, file_path):
        try:
            repo = git.Repo(self.current_dir)
            repo.git.reset(file_path)
            self.update_staged_files_list()
            self.update_file_tree()
            # Removed the confirmation popup
        except git.GitCommandError as e:
            QMessageBox.warning(self, "Error", f"Failed to remove {file_path} from staging: {str(e)}")

    def git_add_all(self):
        try:
            repo = git.Repo(self.current_dir)
            repo.git.add(A=True)
            self.update_staged_files_list()
            self.update_file_tree()
        except git.GitCommandError as e:
            QMessageBox.warning(self, "Error", f"Failed to stage all files: {str(e)}")

    def show_file_context_menu(self, position):
        index = self.file_tree.indexAt(position)
        if not index.isValid():
            return

        item = self.file_model.itemFromIndex(index)
        file_path = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        stage_action = menu.addAction("Git Add")
        action = menu.exec(self.file_tree.viewport().mapToGlobal(position))

        if action == stage_action:
            self.git_add_file(file_path)

    def show_staged_file_context_menu(self, position):
        item = self.staged_list.itemAt(position)
        if item is None:
            return

        file_path = item.text()

        menu = QMenu()
        unstage_action = menu.addAction("Unstage")
        action = menu.exec(self.staged_list.viewport().mapToGlobal(position))

        if action == unstage_action:
            self.git_remove_file(file_path)

    def show_staged_file_context_menu(self, position):
        item = self.staged_list.itemAt(position)
        if item is None:
            return

        file_path = item.text()

        menu = QMenu()
        unstage_action = menu.addAction("Unstage")
        action = menu.exec(self.staged_list.viewport().mapToGlobal(position))

        if action == unstage_action:
            self.git_remove_file(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().text()
        if event.source() == self.file_tree:
            self.git_add_file(file_path)
        elif event.source() == self.staged_list:
            self.git_remove_file(file_path)
        event.acceptProposedAction()   

    def update_commits_list(self):
        self.commits_list.clear()
        commits = get_commits(self.current_dir)
        for commit in commits:
            self.commits_list.addItem(f"{commit['id'][:7]} - {commit['summary']}")

    def update_staged_files_list(self):
        self.staged_list.clear()
        staged_files = get_staged_files(self.current_dir)
        for file in staged_files:
            self.staged_list.addItem(file)

    def show_commit_details(self, item):
        commit_id = item.text().split(' - ')[0]
        details = get_commit_details(self.current_dir, commit_id)
        self.commit_id_label.setText(f"Commit ID: {commit_id}")
        self.summary_text.setPlainText(details['summary'])
        self.description_text.setPlainText(details['description'])
        self.diff_text.setPlainText(details['diff'])

    def show_staged_file_diff(self, item):
        file_name = item.text()
        diff = get_staged_changes(self.current_dir, file_name)
        self.diff_text.setPlainText(diff)

    def clear_commit_details(self):
        self.commit_id_label.setText("Commit ID:")
        self.summary_text.clear()
        self.description_text.clear()
        self.diff_text.clear()

    def git_add(self):
        success, message = git_add_all(self.current_dir)
        self.show_message(message)
        self.update_staged_files_list()

    def generate_commit_message(self):
        diff = get_staged_changes(self.current_dir)
        if not diff:
            QMessageBox.warning(self, "Warning", "No changes staged for commit message generation.")
            return

        ai_commit_message = generate_commit_summary(diff)
        self.summary_text.setPlainText(ai_commit_message.split('\n\n')[0])
        self.description_text.setPlainText('\n\n'.join(ai_commit_message.split('\n\n')[1:]))

    def commit_changes(self):
        # First, generate the AI commit message
        diff = get_staged_changes(self.current_dir)
        if not diff:
            QMessageBox.warning(self, "Warning", "No changes staged for commit.")
            return

        ai_commit_message = generate_commit_summary(diff)

        # Show the generated message to the user and allow them to edit it
        commit_message, ok = QInputDialog.getMultiLineText(
            self, 'Commit Message', 'Edit the commit message:', ai_commit_message)

        if ok and commit_message:
            try:
                repo = git.Repo(self.current_dir)
                repo.index.commit(commit_message)
                self.update_commits_list()
                self.update_staged_files_list()
                self.update_file_tree()
                QMessageBox.information(self, "Success", "Changes committed successfully.")
            except git.GitCommandError as e:
                QMessageBox.warning(self, "Error", f"Failed to commit changes: {str(e)}")
        else:
            QMessageBox.information(self, "Info", "Commit cancelled.")

    def git_push(self):
        success, message = git_push(self.current_dir)
        self.show_message(message)
        if success:
            self.update_commits_list()

    def generate_readme(self):
        if is_git_repo(self.current_dir):
            generate_dynamic_readme(self.current_dir, self)
        else:
            QMessageBox.warning(self, "Error", "Current directory is not a Git repository.")

    def show_message(self, message):
        QMessageBox.information(self, "GitWhipper", message)

    def update_commits_list(self):
        self.commits_list.clear()
        commits = get_commits(self.current_dir)
        for commit in commits:
            commit_date = datetime.datetime.fromtimestamp(commit['timestamp'])
            formatted_date = commit_date.strftime("%Y-%m-%d %H:%M:%S")
            self.commits_list.addItem(f"{formatted_date} - {commit['id'][:7]} - {commit['summary']}")

    def show_commit_details(self, item):
        commit_id = item.text().split(' - ')[1]  # Get the commit ID from the list item
        details = get_commit_details(self.current_dir, commit_id)
        self.commit_id_label.setText(f"Commit ID: {commit_id}")
        self.summary_text.setPlainText(details['summary'])
        self.description_text.setPlainText(details['description'])
        self.display_colored_diff(details['diff'])

    def display_colored_diff(self, diff_text):
        self.diff_text.clear()
        cursor = self.diff_text.textCursor()
        lines = diff_text.split('\n')
        for line in lines:
            format = QTextCharFormat()
            if line.startswith('+'):
                format.setForeground(QBrush(QColor('green')))
            elif line.startswith('-'):
                format.setForeground(QBrush(QColor('red')))
            else:
                format.setForeground(QBrush(QColor('white')))
            
            cursor.insertText(line, format)
            cursor.insertBlock()  # This inserts a new line

        # Scroll to the top of the diff view
        self.diff_text.moveCursor(QTextCursor.MoveOperation.Start)

    def update_branching_panel(self):
        # Update current branch display
        current_branch = get_current_branch(self.current_dir)
        self.current_branch_label.setText(f"Current Branch: {current_branch}")

        # Update branch list
        self.branch_list.clear()
        branches = list_branches(self.current_dir)
        self.branch_list.addItems(branches)

    def create_new_branch(self):
        branch_name, ok = QInputDialog.getText(self, "New Branch", "Enter branch name:")
        if ok and branch_name:
            success = create_branch(self.current_dir, branch_name)
            if success:
                self.update_branching_panel()
                QMessageBox.information(self, "Success", f"Branch '{branch_name}' created successfully.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to create branch '{branch_name}'.")

    def delete_selected_branch(self):
        selected_items = self.branch_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No branch selected.")
            return

        branch_name = selected_items[0].text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete branch '{branch_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = delete_branch(self.current_dir, branch_name)
            if success:
                self.update_branching_panel()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def merge_selected_branch(self):
        selected_items = self.branch_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No branch selected.")
            return

        branch_name = selected_items[0].text()
        reply = QMessageBox.question(self, "Confirm Merge", f"Are you sure you want to merge branch '{branch_name}' into the current branch?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = merge_branch(self.current_dir, branch_name)
            if success:
                self.update_branching_panel()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def show_branch_context_menu(self, position):
        menu = QMenu()
        switch_action = menu.addAction("Switch to Branch")
        rename_action = menu.addAction("Rename Branch")
        push_action = menu.addAction("Push Branch")
        pull_action = menu.addAction("Pull Changes")

        action = menu.exec(self.branch_list.mapToGlobal(position))
        if action:
            selected_items = self.branch_list.selectedItems()
            if not selected_items:
                return

            branch_name = selected_items[0].text()

            if action == switch_action:
                self.switch_to_branch(branch_name)
            elif action == rename_action:
                self.rename_branch(branch_name)
            elif action == push_action:
                self.push_branch(branch_name)
            elif action == pull_action:
                self.pull_changes(branch_name)

    def switch_to_branch(self, branch_name):
        success, message = switch_branch(self.current_dir, branch_name)
        if success:
            self.update_branching_panel()
            self.update_file_tree()
            self.update_staged_files_list()
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def rename_branch(self, old_name):
        new_name, ok = QInputDialog.getText(self, "Rename Branch", "Enter new branch name:")
        if ok and new_name:
            success, message = rename_branch(self.current_dir, old_name, new_name)
            if success:
                self.update_branching_panel()
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def push_branch(self, branch_name):
        success, message = push_branch(self.current_dir, branch_name)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def pull_changes(self, branch_name):
        success, message = pull_changes(self.current_dir, branch=branch_name)
        if success:
            self.update_branching_panel()
            self.update_file_tree()
            self.update_staged_files_list()
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

def apply_stylesheet(app):
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)

    css = """
    QMainWindow {
        border: 1px solid #76797C;
    }
    QToolTip {
        color: #ffffff;
        background-color: #2a82da;
        border: 1px solid white;
    }
    QStatusBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4D4D4D, stop:1 #292929);
    }
    QListWidget, QTextEdit {
        background-color: #1e1e1e;
        border: 1px solid #3A3939;
        color: #eff0f1;
    }
    QListWidget::item:selected {
        background-color: #2a82da;
    }
    QPushButton {
        border: 1px solid #455364;
        border-radius: 2px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #344a5f, stop: 1 #263845);
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3e5a7d, stop: 1 #2d4a63);
    }
    QPushButton:pressed {
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2d4a63, stop: 1 #3e5a7d);
    }
    QLineEdit {
        background-color: #1e1e1e;
        border: 1px solid #3A3939;
        color: #eff0f1;
    }
    """
    app.setStyleSheet(css)

def run_app():
    app = QApplication(sys.argv)
    apply_stylesheet(app)
    window = GitWhipperUI()
    window.show()
    sys.exit(app.exec())