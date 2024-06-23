# gitwhipper/main.py
from .git_utils import get_repo_changes, is_substantial_change, commit_changes
from .commit_summary import generate_commit_summary

def main():
    print("GitWhipper initialized!")
    
    diff = get_repo_changes()
    
    if is_substantial_change(diff):
        print("Substantial changes detected. Generating commit summary...")
        suggested_commit_summary = generate_commit_summary(diff)
        print("\nSuggested Commit Message:")
        print(suggested_commit_summary)
        # User interaction will be handled by the GUI
    else:
        print("No substantial changes detected.")

if __name__ == "__main__":
    main()