 # gitwhipper

## Introduction

gitwhipper is a Git workflow assistant that integrates Large Language Models (LLMs) to enhance the development process. It aids developers by automating various Git commands and generating helpful documentation like commit messages and code reviews. By leveraging LLMs, gitwhipper can provide intelligent suggestions to boost productivity.

## Key Features

- Automated commit message generation
    - LLMs review changes and propose descriptive commit messages
- Assisted code review
    - LLMs analyze pull requests and provide feedback
- Enhanced workflow with post-commit actions
    - Flexible scripts to execute tasks after commits
- Lightweight PyQt6 dashboard
    - Track repos and view Git status

## Installation

Clone the repo:

```
git clone https://github.com/jefedigital/gitwhipper.git
```

Install dependencies:

```
pip install -r requirements.txt
```

## Usage

Here is an example workflow using gitwhipper:

```
# Make changes to project
git add .

# Generate commit message
gitwhipper commit

# Push changes  
git push
```

The commit command will use LLMs to analyze changes and suggest a commit message.

## Project Structure

    .
    ├── dashboard.py         # Main PyQt6 application
    ├──