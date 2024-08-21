 # gitwhisper

gitwhisper is a Git workflow assistant that integrates Large Language Models (LLMs) to enhance the development process. It aids developers by providing automated documentation generation and intelligent recommendations to streamline common Git operations.

## Introduction

gitwhisper utilizes LLMs to provide automated assistance for typical Git workflows. It can generate commit messages, review pull requests, and enhance documentation to boost productivity. By integrating seamlessly with your existing Git setup, gitwhisper aims to make Git easier to use and collaborate with others more efficiently.

## Key Features

- Automated commit message generation
    - Leverages LLMs to generate clear, concise commit messages based on code changes
- Intelligent code review
    - Provides suggestions and feedback for pull requests using LLMs
- Enhanced documentation
    - Automatically generates and updates README documentation based on commit history
- Streamlined Git workflows
    - Assists with common workflows like branching, merging and diff reviews

## Installation

```
pip install gitwhisper
```

gitwhisper requires Python 3.6 or higher. It is compatible with any standard Git installation.

## Usage

Here is a simple example to generate a commit message:

```
gitwhisper commit
```

gitwhisper will analyze changes and prompt you to review and edit the generated commit message.

To utilize code review assistance