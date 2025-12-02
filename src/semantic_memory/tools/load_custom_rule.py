"load_custom_rule MCP tool implementation."
from typing import Any, List
from pathlib import Path
from mcp.types import Tool, TextContent
from semantic_memory.inference.rule_engine import RuleEngine, InferenceRule, validate_rule
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.config import config

LOAD_CUSTOM_RULE_TOOL = Tool(
    name="load_custom_rule",
    description=(
        "Loads a new custom SPARQL CONSTRUCT rule from text. "
        "\n\nThe rule should be a SPARQL CONSTRUCT query that infers new triples. "
        "\n\n**PREFIX declarations are optional** - common prefixes (rdf, schema, foaf, etc.) "
        "will be auto-added if not present."
        "\n\nExample rule content:"
        "\nCONSTRUCT { ?person rdf:type :Engineer . }"
        "\nWHERE { ?person schema:worksFor :Company . }"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "A unique ID for the new rule (lowercase, underscores only).",
            },
            "rule_content": {
                "type": "string",
                "description": "The SPARQL CONSTRUCT query (PREFIX declarations optional).",
            },
            "description": {
                "type": "string",
                "description": "A short description of what the rule does.",
            }
        },
        "required": ["rule_id", "rule_content"],
    },
)

async def load_custom_rule(
    arguments: dict[str, Any],
    rule_engine: RuleEngine,
    graph: ProvenanceGraph,
) -> List[TextContent]:
    """
    Loads a custom SPARQL rule and optionally re-executes the rule engine.
    """
    rule_id = arguments["rule_id"]
    rule_content = arguments["rule_content"]
    description = arguments.get("description")

    # Check if rule ID is unique
    if any(r.id == rule_id for r in rule_engine.rules):
        return [TextContent(type="text", text=f"Error: Rule with ID '{rule_id}' already exists.")]

    # Save the rule to a file in the user_rules directory
    rule_path = config.user_rules_dir / f"{rule_id}.rq"
    with open(rule_path, "w") as f:
        if description:
            f.write(f"# {description}\n")
        f.write(rule_content)

    # Auto-prepend common prefixes if not already present (match rule_engine.load_rules logic)
    final_rule_content = rule_content
    if "PREFIX" not in rule_content.upper():
        common_prefixes = """PREFIX : <http://semanticmemory.org/user#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

"""
        final_rule_content = common_prefixes + rule_content

    # Create and validate the new rule
    new_rule = InferenceRule(
        id=rule_id,
        file_path=rule_path,
        sparql_query=final_rule_content,  # Use prefix-injected version
        source="custom",
        description=description,
    )
    validate_rule(new_rule)

    if not new_rule.is_active:
        return [TextContent(type="text", text=f"Error validating rule: {new_rule.validation_error}")]

    # Add the rule to the engine and re-execute
    rule_engine.rules.append(new_rule)
    rule_engine.execute_rules(graph)

    return [TextContent(type="text", text=f"Successfully loaded and activated new rule '{rule_id}'.")]

__all__ = ["LOAD_CUSTOM_RULE_TOOL", "load_custom_rule"]
