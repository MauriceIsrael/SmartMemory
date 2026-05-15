"""
forget_memory MCP tool implementation.

Removes a fact from the knowledge graph, including its provenance metadata.
"""

from typing import Any

from mcp.types import Tool, TextContent

from smart_memory.logging_config import get_logger
from smart_memory.config import config

logger = get_logger(__name__)


FORGET_MEMORY_TOOL = Tool(
    name="forget_memory",
    description=(
        "Remove a fact from semantic memory, including its provenance metadata."
        "\n\n**CRITICAL RULES:**"
        "\n❌ NEVER remove facts without explicit user instruction"
        "\n❌ NEVER remove facts that are foundations for other inferences (check first with query_memory)"
        "\n✓ Use when user explicitly says 'forget', 'remove', 'that's wrong', 'delete that'"
        "\n✓ Always confirm with user before removing"
        "\n\n**What happens when you forget a fact:**"
        "\n1. The triple is removed from the graph"
        "\n2. Its provenance reification nodes (source, timestamp, confidence) are also removed"
        "\n3. Facts inferred FROM this fact are NOT automatically removed"
        "\n   → Use query_memory to check if dependent facts exist before forgetting"
        "\n\n**Format:** ':Subject predicate :Object'"
        "\n\n**Examples:**"
        "\n  forget_memory(':User foaf:knows :Alice')"
        "\n  forget_memory(':Bob schema:worksFor :AcmeCorp')"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "RDF triple to remove: ':Subject predicate :Object'",
            },
        },
        "required": ["input"],
    },
)


async def forget_memory(
    arguments: dict[str, Any],
    graph,
    triple_extractor,
) -> list[TextContent]:
    """
    Remove a memory from the knowledge graph.

    Args:
        arguments: Tool arguments containing 'input'
        graph: ProvenanceGraph instance
        triple_extractor: TripleExtractor for parsing the triple notation

    Returns:
        List of TextContent with results
    """
    input_text = arguments["input"]
    logger.info(f"forget_memory called with input: {input_text}")

    # Parse the triple
    extracted_triple = triple_extractor.parse_triple_notation(input_text)
    if not extracted_triple:
        return [TextContent(
            type="text",
            text=f"Failed to parse triple notation: {input_text}\n"
                 f"Expected format: ':Subject predicate :Object'"
        )]

    s, p, o = extracted_triple.subject, extracted_triple.predicate, extracted_triple.object

    # Check if the triple exists before attempting removal
    exists = (s, p, o) in graph.graph
    if not exists:
        return [TextContent(
            type="text",
            text=f"Fact not found in memory: {input_text}\n"
                 f"Nothing to remove."
        )]

    # Remove provenance reification nodes for this triple
    from rdflib.namespace import RDF
    provenance_nodes_to_remove = []
    for stmt in graph.graph.subjects(RDF.type, RDF.Statement):
        subj = graph.graph.value(stmt, RDF.subject)
        pred = graph.graph.value(stmt, RDF.predicate)
        obj = graph.graph.value(stmt, RDF.object)
        if subj == s and pred == p and obj == o:
            provenance_nodes_to_remove.append(stmt)

    # Remove provenance triples
    provenance_triples_removed = 0
    for stmt_node in provenance_nodes_to_remove:
        for triple in list(graph.graph.triples((stmt_node, None, None))):
            graph.graph.remove(triple)
            provenance_triples_removed += 1

    # Remove the main triple
    graph.graph.remove((s, p, o))
    graph._triple_count = max(0, graph._triple_count - 1)

    # Save updated graph
    try:
        graph.save_to_file(config.persistence_path)
        logger.debug(f"Saved graph after forget_memory")
    except Exception as e:
        logger.error(f"Failed to save graph: {e}", exc_info=True)

    logger.info(f"Removed triple: ({s}, {p}, {o}) + {provenance_triples_removed} provenance triples")

    s_label = str(s).replace('http://semanticmemory.org/user#', ':')
    p_label = str(p).replace('http://xmlns.com/foaf/0.1/', 'foaf:').replace('https://schema.org/', 'schema:')
    o_label = str(o).replace('http://semanticmemory.org/user#', ':')

    return [TextContent(
        type="text",
        text=f"🗑️ Forgotten: {s_label} {p_label} {o_label}\n"
             f"Removed {provenance_triples_removed} provenance metadata triples.\n\n"
             f"⚠️ Note: Facts inferred FROM this fact are not automatically removed. "
             f"Use query_memory to check for dependent facts."
    )]


__all__ = ["FORGET_MEMORY_TOOL", "forget_memory"]
