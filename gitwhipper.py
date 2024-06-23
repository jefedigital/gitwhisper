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

def main():
    print("GitWhipper initialized!")
    response = get_claude_response("What's the main purpose of version control?")
    print(f"Claude says: {response}")

if __name__ == "__main__":
    main()