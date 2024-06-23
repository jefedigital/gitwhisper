# gitwhipper/commit_summary.py
from .git_utils import get_repo_changes, is_substantial_change, commit_changes
from .ai_utils import get_claude_response, clean_response

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
    cleaned_response = clean_response(response)
    
    lines = cleaned_response.split('\n')
    summary = lines[0].strip()
    description = '\n'.join(lines[1:]).strip()
    
    return f"{summary}\n\n{description}"