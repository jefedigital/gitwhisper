# gitwhisper/commit_summary.py

from .ai_utils import generate_commit_message

def generate_commit_summary(diff):
    """
    Generate a commit summary based on the provided diff.
    This function serves as a wrapper around the AI-powered commit message generation.
    
    Args:
    diff (str): The Git diff of the changes to be committed.
    
    Returns:
    str: A generated commit summary, including a brief summary and a more detailed description.
    """
    return generate_commit_message(diff)

# You can add more commit-related utility functions here if needed in the future.
# For example:
# def parse_commit_summary(summary):
#     """Parse a commit summary into its components."""
#     lines = summary.split('\n', 1)
#     brief_summary = lines[0]
#     detailed_description = lines[1] if len(lines) > 1 else ""
#     return brief_summary, detailed_description