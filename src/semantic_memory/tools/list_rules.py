"""
list_rules MCP tool implementation.
"""
from typing import Any, List
from mcp.types import Tool, TextContent
from semantic_memory.inference.rule_engine import RuleEngine

LIST_RULES_TOOL = Tool(
    name="list_rules",
    description="Lists all available SPARQL inference rules, their sources, and their status.",
    inputSchema={
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "enum": ["all", "default", "custom"],
                "default": "all",
                "description": "Filter rules by source.",
            }
        },
    },
)

async def list_rules(
    arguments: dict[str, Any],
    rule_engine: RuleEngine,
) -> List[TextContent]:
    """
    Lists all available SPARQL inference rules.
    """
    source_filter = arguments.get("source", "all")
    
    rules_info = []
    for rule in rule_engine.rules:
        if source_filter != "all" and rule.source != source_filter:
            continue
            
        rules_info.append(
            {
                "id": rule.id,
                "source": rule.source,
                "description": rule.description,
                "is_active": rule.is_active,
                "validation_error": rule.validation_error,
                "execution_count": rule.execution_count,
                "triples_generated": rule.triples_generated,
            }
        )

    return [TextContent(type="text", text=str(rules_info))]

__all__ = ["LIST_RULES_TOOL", "list_rules"]
