 # gitwhipper

## Introduction

gitwhipper is a Git workflow assistant that integrates Large Language Models (LLMs) to enhance the development process. It aids developers by providing automated documentation generation and by enhancing typical Git workflows. 

By leveraging LLMs, gitwhipper can generate commit messages, assist with code reviews, and improve project documentation. Despite the integration with AI, the core purpose remains focused on making Git easier and more efficient to use.

## Key Features

- Automated commit message generation
    - LLMs review changes in each commit to draft clear, concise commit messages
- Assisted code review
    - LLMs analyze pull requests to highlight areas for review and potential improvements  
- Enhanced documentation
    - LLMs generate and update documentation based on code changes
- Workflow automation
    - Rules and alerts around branching, merging, issues management and more

## Installation

1. Ensure Python 3.6+ and Git are installed
2. Clone the repository: `git clone https://github.com/jefedigital/gitwhipper.git`
3. Navigate into the project directory: `cd gitwhipper`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables: `cp .env.example .env` and edit as needed

## Usage

To generate a commit message: