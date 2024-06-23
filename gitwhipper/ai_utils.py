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
    cleaned = re.sub(r'^.*?(?=\w+:)', '', response, flags=re.DOTALL).strip()
    cleaned = re.sub(r'(Summary:|Description:)\s*', '', cleaned)
    return cleaned