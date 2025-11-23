---
description: Create a new feature branch and spec directory
---

# Create New Feature

This workflow creates a new feature branch with a corresponding spec directory using spec-kit.

## Steps

// turbo
1. Run the create-new-feature script with your feature description:
```bash
bash .specify/scripts/bash/create-new-feature.sh "Your feature description here"
```

The script will:
- Generate a feature number (e.g., 001, 002, etc.)
- Create a branch name from your description
- Create a new git branch (if git is available)
- Create a spec directory under `specs/`
- Copy the spec template to the new directory

## Options

You can customize the feature creation with these options:

- `--short-name <name>`: Provide a custom short name (2-4 words) for the branch
- `--number N`: Specify branch number manually (overrides auto-detection)
- `--json`: Output in JSON format

## Examples

Create a feature with auto-generated name:
```bash
bash .specify/scripts/bash/create-new-feature.sh "Add user authentication system"
```

Create a feature with custom short name:
```bash
bash .specify/scripts/bash/create-new-feature.sh "Add user authentication system" --short-name "user-auth"
```

Create a feature with specific number:
```bash
bash .specify/scripts/bash/create-new-feature.sh "Implement OAuth2 integration" --number 5
```
