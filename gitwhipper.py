import os
import git
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Load environment variables
load_dotenv()

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def get_claude_response(prompt):
    completion = anthropic.completions.create(
        model="claude-2.1",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
    )
    return completion.completion

def get_repo_changes(repo_path='.'):
    repo = git.Repo(repo_path)
    diff = repo.git.diff('--staged')
    return diff

def is_substantial_change(diff, threshold=10):
    # Simple heuristic: consider it substantial if more than 10 lines changed
    return diff.count('\n') > threshold

def generate_commit_summary(diff):
    prompt = f"""
    Analyze the following Git diff and create a concise, informative commit message. The message should summarize the main changes and their purpose.

    Here's the diff:

    {diff}

    Provide ONLY the commit message in the following format, without any additional text or explanations:

    [A brief one-line summary of the changes]

    [A more detailed explanation of what was changed and why (2-3 sentences)]
    """
    response = get_claude_response(prompt)
    
    # Process the response
    lines = response.strip().split('\n')
    summary = lines[0].strip()
    description = '\n'.join(lines[1:]).strip()
    
    return f"{summary}\n\n{description}"

def get_user_choice(options):
    while True:
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        choice = input("Enter your choice (number): ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print("Invalid choice. Please try again.")

def user_interaction(commit_summary):
    print("\nSuggested Commit Message:")
    print(commit_summary)
    
    choice = get_user_choice(["Accept", "Modify", "Reject"])
    
    if choice == 1:  # Accept
        return commit_summary
    elif choice == 2:  # Modify
        print("\nPlease enter your modified commit message.")
        print("Enter 'END' on a new line when you're finished.")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        return "\n".join(lines)
    else:  # Reject
        return None

def commit_changes(repo_path='.', commit_message=None):
    if commit_message:
        repo = git.Repo(repo_path)
        repo.git.commit('-m', commit_message)
        print("Changes committed successfully.")
    else:
        print("Commit aborted.")

def main():
    print("GitWhipper initialized!")
    
    # Get changes from the Git repository
    diff = get_repo_changes()
    
    # Check if changes are substantial
    if is_substantial_change(diff):
        print("Substantial changes detected. Generating commit summary...")
        suggested_commit_summary = generate_commit_summary(diff)
        
        final_commit_message = user_interaction(suggested_commit_summary)
        
        if final_commit_message:
            commit_changes(commit_message=final_commit_message)
    else:
        print("No substantial changes detected.")

if __name__ == "__main__":
    main()