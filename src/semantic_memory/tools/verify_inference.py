"""
verify_inference MCP tool implementation.
"""
from typing import Any, List
from mcp.types import Tool, TextContent
from rdflib.namespace import RDF
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.nlp.triple_extractor import TripleExtractor

VERIFY_INFERENCE_TOOL = Tool(
    name="verify_inference",
    description="Verifies or rejects an uncertain inference.",
    inputSchema={
        "type": "object",
        "properties": {
            "triple": {
                "type": "string",
                "description": "The triple to verify, in ':subject :predicate :object' format.",
            },
            "action": {
                "type": "string",
                "enum": ["accept", "reject"],
                "description": "Whether to accept or reject the inference.",
            },
        },
        "required": ["triple", "action"],
    },
)

async def verify_inference(
    arguments: dict[str, Any],
    graph: ProvenanceGraph,
) -> List[TextContent]:
    """
    Verifies or rejects an uncertain inference.
    """
    triple_str = arguments["triple"]
    action = arguments["action"]

    extractor = TripleExtractor()
    extracted_triple = extractor.parse_triple_notation(triple_str)

    if not extracted_triple:
        return [TextContent(type="text", text=f"Error: Could not parse triple string '{triple_str}'.")]

    s, p, o = extracted_triple.subject, extracted_triple.predicate, extracted_triple.object
    
    # Find the reified statement in the pending graph
    statement_node = None
    for stmt in graph.pending_verifications_graph.subjects(RDF.type, RDF.Statement):
        if (graph.pending_verifications_graph.value(stmt, RDF.subject) == s and
            graph.pending_verifications_graph.value(stmt, RDF.predicate) == p and
            graph.pending_verifications_graph.value(stmt, RDF.object) == o):
            statement_node = stmt
            break
            
    if not statement_node:
        return [TextContent(type="text", text=f"Error: Triple not found in pending verifications.")]

    # Remove the statement and its properties from the pending graph
    graph.pending_verifications_graph.remove((statement_node, None, None))

    if action == "accept":
        graph.add_triple_with_provenance(
            subject=s,
            predicate=p,
            obj=o,
            source="user-verified",
            confidence=1.0,
            uncertain=False
        )
        return [TextContent(type="text", text="Inference accepted and added to the knowledge graph.")]
    
    elif action == "reject":
        # Add to rejected graph
        graph.rejected_verifications_graph.add((s, p, o))
        return [TextContent(type="text", text="Inference rejected.")]

    return [TextContent(type="text", text="Invalid action.")]

__all__ = ["VERIFY_INFERENCE_TOOL", "verify_inference"]
