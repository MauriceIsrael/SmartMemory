"""
list_rules MCP tool implementation.
"""
from typing import Any, List
from mcp.types import Tool, TextContent
from smart_memory.inference.rule_engine import RuleEngine

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
    
    response_lines = [f"Available SPARQL Inference Rules (Filter: {source_filter}):\n"]
    
    for rule in rule_engine.rules:
        if source_filter != "all" and rule.source != source_filter:
            continue
            
        status = "✅ Active" if rule.is_active else "❌ Inactive"
        response_lines.append(f"• {rule.id} [{status}]")
        response_lines.append(f"  Source: {rule.source}")
        if rule.version:
            response_lines.append(f"  Version: {rule.version}")
        if rule.author:
            response_lines.append(f"  Author: {rule.author}")
        if rule.date:
            response_lines.append(f"  Date: {rule.date}")
        if rule.description:
            response_lines.append(f"  Description: {rule.description}")
        
        response_lines.append(f"  Execution count: {rule.execution_count}")
        response_lines.append(f"  Triples generated: {rule.triples_generated}")
        
        if rule.validation_error:
            response_lines.append(f"  ⚠️ Error: {rule.validation_error}")
        
        response_lines.append("")  # Blank line between rules

    return [TextContent(type="text", text="\n".join(response_lines))]


__all__ = ["LIST_RULES_TOOL", "list_rules"]
