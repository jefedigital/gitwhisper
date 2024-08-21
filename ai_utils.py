# gitwhipper/ai_utils.py

import os
import re
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Load environment variables
load_dotenv()

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def get_claude_response(prompt):
    """
    Send a prompt to Claude and get the response.
    """
    completion = anthropic.completions.create(
        model="claude-2.1",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
    )
    return completion.completion

def clean_response(response):
    """
    Clean the response from Claude by removing any leading phrases and labels.
    """
    # Remove common leading phrases
    patterns = [
        r'^Here is a suggested commit message.*?:\s*',
        r'^Based on the provided diff.*?:\s*',
        r'^Here\'s a commit message.*?:\s*',
        r'^The commit message.*?:\s*',
        r'^Suggested commit message.*?:\s*',
    ]
    for pattern in patterns:
        response = re.sub(pattern, '', response, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove any remaining leading whitespace
    response = response.lstrip()
    
    # Remove "Summary:" and "Description:" labels if present
    response = re.sub(r'(Summary:|Description:)\s*', '', response)
    
    return response

def generate_commit_message(diff):
    """
    Generate a commit message based on the provided diff.
    """
    prompt = f"""
    Analyze the following Git diff and create a concise, informative commit message. 
    The message should summarize the main changes and their purpose.

    Here's the diff:

    {diff}

    Provide ONLY the commit message in the following format, without any additional text, explanations, or labels:

    [A brief one-line summary of the changes]

    [A more detailed explanation of what was changed and why (2-3 sentences)]
    """
    response = get_claude_response(prompt)
    cleaned_response = clean_response(response)
    
    return cleaned_response