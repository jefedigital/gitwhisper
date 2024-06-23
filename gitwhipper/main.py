# gitwhipper/main.py
from .git_utils import get_repo_changes, is_substantial_change
from .commit_summary import generate_commit_summary
from .ui.app import run_app

def core_functionality():
    print("GitWhipper initialized!")
    
    diff = get_repo_changes()
    
    if is_substantial_change(diff):
        print("Substantial changes detected. Generating commit summary...")
        suggested_commit_summary = generate_commit_summary(diff)
        print("\nSuggested Commit Message:")
        print(suggested_commit_summary)
    else:
        print("No substantial changes detected.")

def main():
    print("Running core functionality...")
    core_functionality()
    
    print("Starting GUI...")
    run_app()

if __name__ == "__main__":
    main()