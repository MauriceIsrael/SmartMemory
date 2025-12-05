"""
verify_inference MCP tool implementation.

Allows the LLM to verify if a fact is formally proven in the knowledge graph.
"""

from typing import Any

from mcp.types import Tool, TextContent

from smart_memory.logging_config import get_logger

logger = get_logger(__name__)


# Tool definition
VERIFY_INFERENCE_TOOL = Tool(
    name="verify_inference",
    description=(
        "Verify if a fact is FORMALLY PROVEN in the knowledge graph. "
        "This is THE KEY TOOL for collaborative LLM-Formal reasoning."
        "\n\n**WHEN TO USE (CRITICAL):**"
        "\n✓ BEFORE stating a deduction as fact"
        "\n✓ When user asks 'Is X true?' or 'Does Y hold?'"
        "\n✓ After making a soft reasoning step"
        "\n✓ To distinguish your intuition from formal proof"
        "\n\n**WORKFLOW:**"
        "\n1. User asks: 'Is Alice my friend?'"
        "\n2. You check: query_memory('ASK { :User foaf:knows :Alice }')"
        "\n3. Result: True (they know each other)"
        "\n4. Your soft reasoning: 'knows → maybe friends?'"
        "\n5. **YOU MUST CALL:** verify_inference(':User', ':isFriendOf', ':Alice')"
        "\n6. Result: 'Not proven'"
        "\n7. You respond: 'You know Alice, but friendship isn't formally established.'"
        "\n8. If user confirms: Call suggest_rule() to formalize"
        "\n\n**Returns:**"
        "\n- If proven: Source (user/rule), confidence, explanation, rule name"
        "\n- If not proven: Suggestion to either add explicitly or create rule"
        "\n\n**Example:**"
        "\n  verify_inference(subject=':Alice', predicate='foaf:knows', object=':User')"
        "\n  → Returns proof chain if fact is formally established"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Subject of the triple (e.g., ':Alice', ':User')",
            },
            "predicate": {
                "type": "string",
                "description": "Predicate/property (e.g., 'foaf:knows', 'schema:worksFor')",
            },
            "object": {
                "type": "string",
                "description": "Object of the triple (e.g., ':AcmeCorp', ':Bob')",
            },
        },
        "required": ["subject", "predicate", "object"],
    },
)


async def verify_inference(
    arguments: dict[str, Any],
    graph,
) -> list[TextContent]:
    """
    Verify if a fact is formally proven.

    Args:
        arguments: Tool arguments containing subject, predicate, object
        graph: ProvenanceGraph instance

    Returns:
        List of TextContent with verification result
    """
    subject = arguments["subject"]
    predicate = arguments["predicate"]
    obj = arguments["object"]

    logger.info(f"verify_inference called for: {subject} {predicate} {obj}")

    # Build SPARQL query to check if triple exists and get provenance
    # Note: The graph uses RDF reification (rdf:Statement with rdf:subject/predicate/object)
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sem: <http://semanticmemory.org/vocab#>
    PREFIX : <http://semanticmemory.org/user#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX schema: <https://schema.org/>
    
    SELECT ?source ?confidence ?rule ?timestamp
    WHERE {{
        # Find reification node for this triple
        ?stmt rdf:type rdf:Statement ;
              rdf:subject {subject} ;
              rdf:predicate {predicate} ;
              rdf:object {obj} ;
              sem:source ?source .
        
        OPTIONAL {{ ?stmt sem:confidence ?confidence }}
        OPTIONAL {{ ?stmt sem:sourceRule ?rule }}
        OPTIONAL {{ ?stmt sem:timestamp ?timestamp }}
    }}
    LIMIT 1
    """

    try:
        results = graph.query(query)
        
        if not results or len(results) == 0:
            # Fact not found in graph
            response = {
                "proven": False,
                "exists_in_graph": False,
                "message": f"No formal proof found for: {subject} {predicate} {obj}",
                "suggestion": "This inference is not formally established. Consider:\n"
                             "  1. Adding it as an explicit fact (add_memory)\n"
                             "  2. Creating a rule to infer it (suggest_rule)"
            }
            logger.info(f"Fact not proven: {subject} {predicate} {obj}")
        else:
            # Fact found - extract provenance
            row = results[0]
            source = str(row.get('source', 'unknown'))
            confidence = float(row.get('confidence', 1.0)) if row.get('confidence') else 1.0
            rule = str(row.get('rule', '')) if row.get('rule') else None
            timestamp = str(row.get('timestamp', '')) if row.get('timestamp') else None
            
            # Build explanation
            if source == "user":
                explanation = "Explicitly added by user"
            elif source == "sparql-rule":
                rule_name = rule.split('#')[-1] if rule else "unknown rule"
                explanation = f"Inferred by rule '{rule_name}'"
            else:
                explanation = f"Source: {source}"
            
            if timestamp:
                explanation += f" on {timestamp}"
            
            response = {
                "proven": True,
                "exists_in_graph": True,
                "confidence": confidence,
                "source": source,
                "rule": rule.split('#')[-1] if rule else None,
                "explanation": explanation,
                "message": f"✓ Formally proven: {subject} {predicate} {obj}\n{explanation}"
            }
            
            if confidence < 1.0:
                response["message"] += f"\n⚠️ Confidence: {confidence:.2f} (may require verification)"
            
            logger.info(f"Fact proven: {subject} {predicate} {obj} (source: {source}, confidence: {confidence})")
        
        # Format response as readable text
        text_response = response["message"]
        if not response["proven"]:
            text_response += f"\n\n{response['suggestion']}"
        
        return [
            TextContent(
                type="text",
                text=text_response
            )
        ]
        
    except Exception as e:
        logger.error(f"Error verifying inference: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error verifying inference: {str(e)}"
            )
        ]


__all__ = ["VERIFY_INFERENCE_TOOL", "verify_inference"]
