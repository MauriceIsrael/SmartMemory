# Using MCP Prompts in SmartMemory

MCP Prompts are **pre-defined conversation starters** that appear in your LLM client to help you interact with SmartMemory quickly and easily.

## What Are MCP Prompts?

Unlike MCP **Tools** (which the LLM calls automatically), MCP **Prompts** are shortcuts that **you** trigger to start common conversations.

## Available Prompts

SmartMemory provides 5 prompts:

### 1. `/remember-fact` - Store Information

**What it does**: Helps the LLM remember a new fact about you or your world.

**How to use in Claude Desktop**:
```
/remember-fact Alice works at Google
```

**What happens**:
- Claude will use the `add_memory` tool to store the fact
- Show you what was stored
- Report any automatic inferences (e.g., "Alice is a Person")
- Alert you if verification is needed

### 2. `/query-knowledge` - Search Memory

**What it does**: Helps you find information in your semantic memory.

**How to use**:
```
/query-knowledge Who works at tech companies?
```

**What happens**:
- Claude will construct an appropriate SPARQL query
- Execute it using `query_memory` or `search_entity`
- Present the results in a readable format
- Explain any relevant inferences

### 3. `/add-custom-rule` - Create Inference Rule

**What it does**: Helps you create custom logic for automatic inference.

**How to use**:
```
/add-custom-rule If someone teaches a course, they might be a mentor
```

**What happens**:
- Claude will create a SPARQL CONSTRUCT rule
- Use `load_custom_rule` to add it to the system
- Explain what the rule will infer
- Give examples of when it would trigger

### 4. `/show-stats` - View Statistics

**What it does**: Shows you what the system knows.

**How to use**:
```
/show-stats
```

**What happens**:
- Claude uses `get_graph_stats` tool
- Shows total facts stored
- Breakdown by source (your input vs. inferred)
- Number of active inference rules
- Pending verifications and conflicts

### 5. `/verify-inferences` - Review Uncertain Inferences

**What it does**: Helps you review and approve/reject uncertain automatic inferences.

**How to use**:
```
/verify-inferences
```

**What happens**:
- Claude checks for pending verifications
- Shows each uncertain inference with context
- Asks you to confirm or reject
- Uses `verify_inference` tool to record your decision

## How Prompts Appear in Different Clients

### Claude Desktop

Prompts appear when you type `/` in the chat:

```
/remember-fact [fact]
/query-knowledge [question]
/add-custom-rule [rule_description]
/show-stats
/verify-inferences
```

Just start typing `/` and you'll see autocomplete suggestions.

### Continue.dev (VS Code)

Prompts may appear in the prompt library or as slash commands depending on your version.

### Other MCP Clients

Check your client's documentation for how prompts are displayed. Most show them as:
- Slash commands (/ prefix)
- Prompt library/menu
- Quick actions menu

## Example Workflows

### Workflow 1: Building a Personal Knowledge Base

```bash
# Start by adding facts
/remember-fact I live in San Francisco

# Add more context
/remember-fact I work at Acme Corp as a software engineer

# Add relationships
/remember-fact I know Alice, and she's my colleague

# Check what you've stored
/show-stats

# Query your knowledge
/query-knowledge Who are my colleagues?
```

### Workflow 2: Smart Inference

```bash
# Add facts that trigger inference
/remember-fact Alice works at Acme Corp
/remember-fact Bob works at Acme Corp

# System might infer: "Alice and Bob might be colleagues"
# If confidence < 0.85, you'll need to verify:

/verify-inferences
# Claude shows: "Alice might be colleagues with Bob (both work at Acme)"
# You respond: "Yes, they work on the same team"
```

### Workflow 3: Custom Learning Rules

```bash
# Create a rule for tracking reading
/add-custom-rule If I read a book about a topic, I'm interested in that topic

# Add some reading history
/remember-fact I read "Clean Code" which is about software engineering

# System automatically infers: "You are interested in software engineering"

# Query to verify
/query-knowledge What am I interested in?
```

## Prompts vs. Tools

| Feature | MCP Tools | MCP Prompts |
|---------|-----------|-------------|
| **Who triggers** | LLM (automatically) | You (manually) |
| **Purpose** | LLM performs actions | Guide conversations |
| **Visibility** | Hidden from you | Visible as shortcuts |
| **Example** | `add_memory` tool | `/remember-fact` prompt |

**When to use Tools**: Let Claude decide when to use semantic memory naturally in conversation.

**When to use Prompts**: When you want to explicitly perform a semantic memory operation with guided help.

## Creating Your Own Prompts

If you want to add more prompts, edit [`src/semantic_memory/prompts.py`](../src/semantic_memory/prompts.py):

```python
Prompt(
    name="my-custom-prompt",
    description="Description of what this does",
    arguments=[
        PromptArgument(
            name="my_arg",
            description="What this argument is for",
            required=True
        )
    ]
)
```

Then add the handler in the `get_prompt()` function to define what Claude should do when the prompt is triggered.

## Troubleshooting

### Prompts Don't Appear

1. **Restart your MCP client** (e.g., Claude Desktop)
2. Check the server logs for "MCP prompts registered"
3. Verify you're using an up-to-date MCP client that supports prompts

### Prompts Trigger But Don't Work

Check that:
- The server is running correctly
- All 7 tools are available (`list_tools` should show them)
- No errors in the server logs

### Want More Prompts?

You can request additional prompts by:
1. Opening an issue on GitHub
2. Contributing your own (see [CONTRIBUTING.md](../CONTRIBUTING.md))
3. Editing `prompts.py` directly

---

**Next**: See [`quick-start.md`](quick-start.md) for a complete usage tutorial
