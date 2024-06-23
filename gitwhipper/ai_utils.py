# gitwhipper/ai_utils.py
import os
import re
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

load_dotenv()
anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def get_claude_response(prompt):
    completion = anthropic.completions.create(
        model="claude-2.1",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
    )
    return completion.completion

def clean_response(response):
    # Remove any leading phrases including "changes:"
    cleaned = re.sub(r'^.*?(changes:)?\s*', '', response, flags=re.DOTALL).strip()
    
    # Remove "Summary:" and "Description:" labels if present
    cleaned = re.sub(r'(Summary:|Description:)\s*', '', cleaned)
    
    return cleaned