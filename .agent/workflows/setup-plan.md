---
description: Setup implementation plan for current feature
---

# Setup Implementation Plan

This workflow creates an implementation plan file for the current feature.

## Steps

// turbo
1. Ensure you're on a feature branch (e.g., `001-feature-name`)

// turbo
2. Run the setup-plan script:
```bash
bash .specify/scripts/bash/setup-plan.sh
```

The script will:
- Verify you're on a feature branch
- Create the feature directory if it doesn't exist
- Copy the plan template to `specs/<feature-name>/plan.md`

## Output

The script outputs:
- `FEATURE_SPEC`: Path to the spec.md file
- `IMPL_PLAN`: Path to the plan.md file
- `SPECS_DIR`: Path to the feature directory
- `BRANCH`: Current branch name
- `HAS_GIT`: Whether git is available

## Example

```bash
bash .specify/scripts/bash/setup-plan.sh
```

Output:
```
FEATURE_SPEC: /path/to/specs/001-feature-name/spec.md
IMPL_PLAN: /path/to/specs/001-feature-name/plan.md
SPECS_DIR: /path/to/specs/001-feature-name
BRANCH: 001-feature-name
HAS_GIT: true
```
