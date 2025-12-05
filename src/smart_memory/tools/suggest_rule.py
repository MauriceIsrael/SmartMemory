"""
suggest_rule MCP tool implementation.

Allows the LLM to propose SPARQL rules to formalize reasoning patterns.
"""

from typing import Any

from mcp.types import Tool, TextContent

from smart_memory.logging_config import get_logger

logger = get_logger(__name__)


# Tool definition
SUGGEST_RULE_TOOL = Tool(
    name="suggest_rule",
    description=(
        "**IMPORTANT: USER APPROVAL REQUIRED / APPROBATION REQUISE**\n"
        "Allows the LLM to propose SPARQL rules to formalize reasoning patterns.\n\n"
        "**CRITICAL WORKFLOW:**\n"
        "1.  **EXPLAIN & ASK:** You MUST explain the rule and ask for explicit permission FIRST.\n"
        "    *   *En Français:* \"Puis-je ajouter cette règle d'inférence ?\"\n"
        "    *   *In English:* \"May I add this inference rule?\"\n"
        "2.  **WAIT:** Do NOT call `suggest_rule` until the user says YES.\n"
        "3.  **SUGGEST:** Only after approval, call this tool.\n"
        "4.  **CONFIRM:** The user must then approve the pending rule using `approve_rule` (which you CANNOT call yourself).\n\n"
        "---\n\n"
        "**WHEN TO USE:**"
        "\n✓ After verify_inference() returns 'not proven' for logical deduction"
        "\n✓ When user explicitly states a rule (e.g., 'friends know each other')"
        "\n✓ When detecting recurring patterns in conversation"
        "\n✓ To convert YOUR soft reasoning into FORMAL guarantees"
        "\n\n**WORKFLOW EXAMPLE:**"
        "\n1. You: 'Voting implies age >= 18. Shall I formalize this?'"
        "\n2. User: 'Yes'"
        "\n3. **YOU CALL:** suggest_rule(...)"
        "\n4. System: Previews inferences, adds to pending approval"
        "\n5. **STOP:** You wait for user to review.\n"
        "\n\n**CRITICAL - DO NOT BYPASS THIS TOOL:**"
        "\n❌ NEVER edit .rq files directly"
        "\n❌ NEVER create rules outside this workflow"  
        "\n✓ ALWAYS use suggest_rule() → user approves → system activates"
        "\n\n**Best Practices:**"
        "\n- Use descriptive rule_id (snake_case)"
        "\n- SPARQL must be CONSTRUCT query"
        "\n- Set confidence < 1.0 for uncertain rules"
        "\n- Preview shows what WOULD be inferred"
        "\n\n**Rule goes to PENDING - User must approve!**"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "Unique identifier for this rule (e.g., 'acquaintance_from_knows')",
            },
            "description": {
                "type": "string",
                "description": "Human-readable description of what the rule does",
            },
            "sparql_pattern": {
                "type": "string",
                "description": "SPARQL CONSTRUCT query defining the inference rule",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence level (0.0-1.0) for facts inferred by this rule (default: 0.8)",
                "default": 0.8,
            },
        },
        "required": ["rule_id", "description", "sparql_pattern"],
    },
)


async def suggest_rule(
    arguments: dict[str, Any],
    graph,
    rule_engine,
) -> list[TextContent]:
    """
    Suggest a new SPARQL inference rule.

    Args:
        arguments: Tool arguments containing rule_id, description, sparql_pattern, confidence
        graph: ProvenanceGraph instance
        rule_engine: RuleEngine instance

    Returns:
        List of TextContent with suggestion result and preview
    """
    rule_id = arguments["rule_id"]
    description = arguments["description"]
    sparql_pattern = arguments["sparql_pattern"]
    confidence = arguments.get("confidence", 0.8)

    logger.info(f"suggest_rule called: {rule_id}")

    # Validate confidence range
    if not (0.0 <= confidence <= 1.0):
        return [
            TextContent(
                type="text",
                text=f"❌ Invalid confidence value: {confidence}. Must be between 0.0 and 1.0."
            )
        ]

    # Validate SPARQL syntax
    try:
        # Try to parse the SPARQL query
        graph.query(f"ASK {{ ?s ?p ?o }}")  # Simple validation query
        
        # Check if it's a CONSTRUCT query
        if "CONSTRUCT" not in sparql_pattern.upper():
            return [
                TextContent(
                    type="text",
                    text=f"❌ Invalid SPARQL rule. Must be a CONSTRUCT query.\n\n"
                         f"Your pattern: {sparql_pattern[:100]}..."
                )
            ]
        
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"❌ Invalid SPARQL syntax: {str(e)}\n\n"
                     f"Your pattern: {sparql_pattern}"
            )
        ]

    # Execute dry-run to preview inferences
    try:
        # Add common prefixes to the query if not present
        prefixes = """
        PREFIX : <http://semanticmemory.org/user#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX schema: <https://schema.org/>
        """
        
        full_query = prefixes + "\n" + sparql_pattern
        
        # Execute as dry-run
        preview_results = graph.query(full_query)
        
        # Count potential inferences
        if hasattr(preview_results, '__iter__'):
            preview_triples = list(preview_results)
            num_inferences = len(preview_triples)
        else:
            num_inferences = 0
            preview_triples = []
        
        # Format preview
        preview_text = f"\n\n📊 **Dry-run Preview:**\n"
        preview_text += f"This rule would infer {num_inferences} new facts.\n"
        
        if num_inferences > 0:
            preview_text += f"\n**Sample inferences (showing first 5):**"
            for i, triple in enumerate(preview_triples[:5], 1):
                s = str(triple[0]).replace('http://semanticmemory.org/user#', ':')
                p = str(triple[1]).replace('http://xmlns.com/foaf/0.1/', 'foaf:').replace('https://schema.org/', 'schema:')
                o = str(triple[2]).replace('http://semanticmemory.org/user#', ':')
                preview_text += f"\n  {i}. {s} {p} {o}"
            
            if num_inferences > 5:
                preview_text += f"\n  ... and {num_inferences - 5} more"
        
        # Build rule content for saving
        rule_content = f"""# {description}
# CONFIDENCE: {confidence}
# ID: {rule_id}
{sparql_pattern}
"""
        
        # Store rule in pending approvals
        from smart_memory.tools.pending_rules import add_pending_rule
        
        add_pending_rule(rule_id, {
            "description": description,
            "sparql_pattern": sparql_pattern,
            "confidence": confidence,
            "num_inferences": num_inferences,
            "preview": preview_text,
        })
        
        response_text = f"✨ **Rule Suggestion: '{rule_id}'**\n\n"
        response_text += f"**Description:** {description}\n"
        response_text += f"**Confidence:** {confidence}\n"
        response_text += preview_text
        response_text += f"\n\n⏳ **Status:** Rule added to pending approvals.\n"
        response_text += f"**Next Steps:**\n"
        response_text += f"1. User reviews the preview above\n"
        response_text += f"2. User calls approve_rule('{rule_id}') to activate, or reject_rule('{rule_id}') to discard\n"
        response_text += f"3. Use get_pending_rules() to see all pending rules\n"
        
        if confidence < 0.9:
            response_text += f"\n⚠️ **Note:** Confidence < 0.9 means inferred facts will require user verification."
        
        logger.info(f"Rule '{rule_id}' added to pending approvals with {num_inferences} potential inferences")
        
        return [
            TextContent(
                type="text",
                text=response_text
            )
        ]
        
    except Exception as e:
        logger.error(f"Error previewing rule: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"❌ Error previewing rule: {str(e)}\n\n"
                     f"SPARQL pattern may be invalid or incompatible with current graph."
            )
        ]


__all__ = ["SUGGEST_RULE_TOOL", "suggest_rule"]
