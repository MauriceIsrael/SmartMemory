"""
MCP prompts for SmartMemory.

Prompts are pre-defined conversation starters that help users interact with
the semantic memory system.
"""

from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent

# Prompt definitions
PROMPTS = [
    Prompt(
        name="remember-fact",
        description="Store a new fact or piece of information in semantic memory",
        arguments=[
            PromptArgument(
                name="fact",
                description="The fact or information to remember (e.g., 'Alice works at Google')",
                required=True
            )
        ]
    ),
    Prompt(
        name="query-knowledge",
        description="Search for information in semantic memory",
        arguments=[
            PromptArgument(
                name="question",
                description="What you want to know (e.g., 'Who works at Google?')",
                required=True
            )
        ]
    ),
    Prompt(
        name="add-custom-rule",
        description="Create a custom inference rule to automatically derive new knowledge",
        arguments=[
            PromptArgument(
                name="rule_description",
                description="Describe what the rule should infer (e.g., 'If two people work at the same company, they might be colleagues')",
                required=True
            )
        ]
    ),
    Prompt(
        name="show-stats",
        description="Show statistics about the knowledge graph (how much is known, inference activity, etc.)",
        arguments=[]
    ),
    Prompt(
        name="verify-inferences",
        description="Review and confirm/reject uncertain inferences that need user verification",
        arguments=[]
    ),
]


async def get_prompt(name: str, arguments: dict[str, str] | None) -> dict:
    """
    Get a prompt message for the given prompt name and arguments.
    
    Args:
        name: Name of the prompt
        arguments: Arguments provided for the prompt
        
    Returns:
        GetPromptResult dict with the prompt message
    """
    arguments = arguments or {}
    
    if name == "remember-fact":
        fact = arguments.get("fact", "")
        message = PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Please remember this fact: {fact}\n\n"
                     f"Use the add_memory tool to store this information in my semantic memory. "
                     f"Tell me what was stored and if any new facts were automatically inferred."
            )
        )
        return {"messages": [message]}
    
    elif name == "query-knowledge":
        question = arguments.get("question", "")
        message = PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"I want to know: {question}\n\n"
                     f"Please search my semantic memory using the query_memory or search_entity tools. "
                     f"Show me what you find and explain any relevant inferences."
            )
        )
        return {"messages": [message]}
    
    elif name == "add-custom-rule":
        rule_desc = arguments.get("rule_description", "")
        message = PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Create a custom inference rule: {rule_desc}\n\n"
                     f"Use the load_custom_rule tool to create a SPARQL CONSTRUCT rule that implements this logic. "
                     f"Explain what the rule will do and show me an example of what it would infer."
            )
        )
        return {"messages": [message]}
    
    elif name == "show-stats":
        message = PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text="Show me statistics about my semantic memory.\n\n"
                     "Use the get_graph_stats tool to show:\n"
                     "- How many facts are stored\n"
                     "- How many were inferred automatically\n"
                     "- Active inference rules\n"
                     "- Any conflicts or pending verifications"
            )
        )
        return {"messages": [message]}
    
    elif name == "verify-inferences":
        message = PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text="Show me any uncertain inferences that need my confirmation.\n\n"
                     "First use get_pending_verifications to see if there are pending verifications, "
                     "then help me review and either accept or reject each one using the verify_inference tool."
            )
        )
        return {"messages": [message]}
    
    else:
        raise ValueError(f"Unknown prompt: {name}")


__all__ = ["PROMPTS", "get_prompt"]
