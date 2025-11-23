---
description: Update agent context files from plan.md
---

# Update Agent Context

This workflow updates agent context files (GEMINI.md, CLAUDE.md, etc.) with information from the current feature's plan.md.

## Steps

// turbo
1. Ensure you're on a feature branch and have a plan.md file

// turbo
2. Run the update-agent-context script:
```bash
bash .specify/scripts/bash/update-agent-context.sh
```

Or update a specific agent:
```bash
bash .specify/scripts/bash/update-agent-context.sh gemini
```

The script will:
- Parse plan.md to extract project metadata (language, framework, database, etc.)
- Update or create agent context files
- Add technology stack information
- Update recent changes section
- Update the last modified timestamp

## Supported Agents

You can update context for these agents:
- `claude` - Claude Code (CLAUDE.md)
- `gemini` - Gemini CLI (GEMINI.md)
- `copilot` - GitHub Copilot (.github/agents/copilot-instructions.md)
- `cursor-agent` - Cursor IDE (.cursor/rules/specify-rules.mdc)
- `qwen` - Qwen Code (QWEN.md)
- `windsurf` - Windsurf (.windsurf/rules/specify-rules.md)
- `kilocode` - Kilo Code (.kilocode/rules/specify-rules.md)
- `auggie` - Auggie CLI (.augment/rules/specify-rules.md)
- `roo` - Roo Code (.roo/rules/specify-rules.md)
- `codebuddy` - CodeBuddy CLI (CODEBUDDY.md)
- `shai` - SHAI (SHAI.md)
- `q` - Amazon Q Developer CLI (AGENTS.md)

## Examples

Update all existing agent files:
```bash
bash .specify/scripts/bash/update-agent-context.sh
```

Update only Gemini context:
```bash
bash .specify/scripts/bash/update-agent-context.sh gemini
```

Update only Claude context:
```bash
bash .specify/scripts/bash/update-agent-context.sh claude
```
