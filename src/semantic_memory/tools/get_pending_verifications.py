"""
MCP tool for listing pending verifications (uncertain inferences).

This tool allows Gemini to check if there are any inferences that require
user verification before being accepted into the knowledge graph.
"""

from typing import Any
from mcp.types import Tool, TextContent
from semantic_memory.config import config

import logging

logger = logging.getLogger(__name__)


# Tool schema
GET_PENDING_VERIFICATIONS_TOOL = Tool(
    name="get_pending_verifications",
    description=(
        "List all pending verifications (uncertain inferences that need user confirmation). "
        "Returns a list of inferred triples with their confidence scores and source rules. "
        "Use verify_inference tool to accept or reject them."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of pending verifications to return (default: 10)",
                "default": 10,
            }
        },
    },
)


async def get_pending_verifications(
    arguments: dict[str, Any],
    graph,
) -> list[TextContent]:
    """
    List pending verifications.

    Args:
        arguments: Tool arguments with optional 'limit'
        graph: ProvenanceGraph instance

    Returns:
        List of TextContent with pending verifications or message if none
    """
    limit = arguments.get("limit", 10)
    
    logger.info(f"get_pending_verifications called with limit={limit}")

    # Query for uncertain inferences
    query = f"""
    PREFIX sem: <http://example.org/semanticmemory/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?id ?s ?p ?o ?confidence ?source_rule
    WHERE {{
        ?stmt a rdf:Statement ;
              rdf:subject ?s ;
              rdf:predicate ?p ;
              rdf:object ?o ;
              sem:uncertain true ;
              sem:confidence ?confidence ;
              sem:verification_id ?id .
        OPTIONAL {{ ?stmt sem:source_rule ?source_rule }}
    }}
    ORDER BY DESC(?confidence)
    LIMIT {limit}
    """

    try:
        results = list(graph.query(query))
        
        if not results:
            return [
                TextContent(
                    type="text",
                    text="✓ No pending verifications. All inferences have been accepted or rejected.",
                )
            ]

        # Format results
        response_text = f"📋 **{len(results)} Pending Verification(s)**\n\n"
        
        for i, row in enumerate(results, 1):
            verification_id = str(row.id)
            subject = str(row.s).replace(config.user_namespace, ":")
            predicate = str(row.p).replace("http://xmlns.com/foaf/0.1/", "foaf:")
            obj = str(row.o).replace(config.user_namespace, ":")
            confidence = float(row.confidence)
            source_rule = str(row.source_rule) if row.source_rule else "unknown"
            
            response_text += f"**{i}. Verification ID: `{verification_id}`**\n"
            response_text += f"   - Triple: `{subject} {predicate} {obj}`\n"
            response_text += f"   - Confidence: {confidence:.2f}\n"
            response_text += f"   - Source rule: {source_rule}\n\n"

        response_text += (
            "\n💡 **Next step**: Use `verify_inference` tool to accept or reject these inferences.\n"
            "Example: verify_inference(verification_id='...', accepted=true)"
        )

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Failed to get pending verifications: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"❌ Error retrieving pending verifications: {e}",
            )
        ]


__all__ = ["GET_PENDING_VERIFICATIONS_TOOL", "get_pending_verifications"]
