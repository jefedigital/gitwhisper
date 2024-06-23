import os
import git
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI API client
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    print("GitWhipper initialized!")

if __name__ == "__main__":
    main()