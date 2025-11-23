"""
add_memory MCP tool implementation.

Adds natural language statements or explicit RDF triples to the knowledge graph.
"""

from typing import Any

from mcp.types import Tool, TextContent

from semantic_memory.logging_config import get_logger
from semantic_memory.nlp import TripleExtractor
from semantic_memory.config import config

logger = get_logger(__name__)


# Tool definition
ADD_MEMORY_TOOL = Tool(
    name="add_memory",
    description=(
        "Add a memory to the knowledge graph. "
        "Can accept natural language statements (e.g., 'Alice works at Google') "
        "or explicit RDF triples (e.g., ':Alice schema:worksFor :Google'). "
        "Automatically infers additional facts using OWL-RL reasoning and SPARQL rules."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Natural language statement or RDF triple to add",
            },
            "format": {
                "type": "string",
                "enum": ["natural_language", "triple_notation"],
                "default": "natural_language",
                "description": "Format of the input (auto-detected if not specified)",
            },
        },
        "required": ["input"],
    },
)


async def add_memory(
    arguments: dict[str, Any],
    graph,
    reasoner,
    triple_extractor: TripleExtractor,
) -> list[TextContent]:
    """
    Add a memory to the knowledge graph.

    Args:
        arguments: Tool arguments containing 'input' and optional 'format'
        graph: ProvenanceGraph instance
        reasoner: Reasoner instance for OWL-RL inference
        triple_extractor: TripleExtractor for NL processing

    Returns:
        List of TextContent with results
    """
    input_text = arguments["input"]
    format_type = arguments.get("format", "natural_language")

    logger.info(f"add_memory called with input: {input_text[:100]}...")

    # Extract triples from input
    if format_type == "triple_notation" or input_text.strip().startswith(":"):
        # Explicit triple notation
        extracted_triple = triple_extractor.parse_triple_notation(input_text)
        if extracted_triple:
            extracted_triples = [extracted_triple]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Failed to parse triple notation: {input_text}",
                )
            ]
    else:
        # Natural language
        extracted_triples = triple_extractor.extract(input_text)

    if not extracted_triples:
        return [
            TextContent(
                type="text",
                text=f"Could not extract any triples from: {input_text}",
            )
        ]

    # Add triples to graph with provenance
    added_count = 0
    for triple in extracted_triples:
        # Check confidence threshold
        if triple.confidence < 0.5:
            logger.debug(f"Skipping low-confidence triple: {triple}")
            continue

        try:
            graph.add_triple_with_provenance(
                subject=triple.subject,
                predicate=triple.predicate,
                obj=triple.object,
                source="user",
                confidence=triple.confidence,
                uncertain=(triple.confidence < config.auto_accept_threshold),
            )
            added_count += 1

            logger.debug(
                f"Added triple: ({triple.subject}, {triple.predicate}, {triple.object})"
            )

        except Exception as e:
            logger.error(f"Failed to add triple: {e}", exc_info=True)

    # Apply OWL-RL reasoning to derive new facts
    try:
        inferred_count = reasoner.apply_closure(graph)
        logger.info(f"Reasoning inferred {inferred_count} new triples")
    except Exception as e:
        logger.error(f"Reasoning failed: {e}", exc_info=True)
        inferred_count = 0

    # TODO: Apply SPARQL rules (will be implemented in Phase 4)
    # from semantic_memory.inference.rule_engine import RuleEngine
    # rule_engine = RuleEngine()
    # rule_inferred_count = await rule_engine.apply_rules(graph)

    # Save graph to persistence
    try:
        graph.save_to_file(config.persistence_path)
        logger.debug(f"Saved graph to {config.persistence_path}")
    except Exception as e:
        logger.error(f"Failed to save graph: {e}", exc_info=True)

    # Prepare response
    response_text = (
        f"✓ Added {added_count} explicit triple(s) from your input.\n"
        f"✓ Inferred {inferred_count} additional triple(s) via OWL-RL reasoning.\n"
        f"\nTotal triples in knowledge graph: {graph.get_triple_count()}"
    )

    # Check for uncertain inferences that need verification
    uncertain_query = """
    SELECT ?s ?p ?o
    WHERE {
        ?stmt a rdf:Statement ;
              rdf:subject ?s ;
              rdf:predicate ?p ;
              rdf:object ?o ;
              sem:uncertain true .
    }
    LIMIT 5
    """

    try:
        uncertain_results = graph.query(uncertain_query)
        if uncertain_results:
            response_text += f"\n\n⚠ {len(uncertain_results)} inference(s) need verification."
            response_text += "\nUse the verify_inference tool to confirm or reject them."
    except Exception as e:
        logger.warning(f"Failed to query for uncertain inferences: {e}")

    return [TextContent(type="text", text=response_text)]


__all__ = ["ADD_MEMORY_TOOL", "add_memory"]
