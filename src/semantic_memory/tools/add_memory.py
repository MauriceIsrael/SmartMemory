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
    rule_engine,
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

    # Apply OWL-RL reasoning to derive new facts (if enabled)
    owl_inferred_count = 0
    if config.enable_owl_reasoning:
        try:
            owl_inferred_count = reasoner.apply_closure(graph)
            logger.info(f"Reasoning inferred {owl_inferred_count} new triples")
        except Exception as e:
            logger.error(f"Reasoning failed: {e}", exc_info=True)
    else:
        logger.debug("OWL-RL reasoning disabled, skipping")

    # Apply SPARQL rules
    sparql_inferred_count = 0
    if rule_engine:
        try:
            sparql_inferred_count = rule_engine.execute_rules(graph)
            logger.info(f"SPARQL rules inferred {sparql_inferred_count} new triples")
        except Exception as e:
            logger.error(f"Rule engine failed: {e}", exc_info=True)

    # Detect conflicts (only in user data, not ontologies)
    from semantic_memory.knowledge.conflicts import ContradictoryLiteralDetector, DisjointClassDetector, FunctionalPropertyDetector
    
    # Only check user-added triples for conflicts, not ontology triples
    # We do this by creating a temporary subgraph with only user data
    # This prevents false positives from ontologies having multiple comments/notes
    user_triples_query = """
    PREFIX sem: <http://example.org/semanticmemory/>
    
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
        ?stmt a <http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement> ;
              <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?s ;
              <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> ?p ;
              <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?o ;
              sem:source "user" .
    }
    """
    
    detectors = [ContradictoryLiteralDetector(), DisjointClassDetector(), FunctionalPropertyDetector()]
    all_conflicts = []
    
    # Only run conflict detection if there are user triples
    try:
        user_results = list(graph.query(user_triples_query))
        if user_results:
            # For now, run on full graph but this could be optimized
            # to only check user triples in the future
            for detector in detectors:
                conflicts = detector.detect_conflicts(graph)
                # Filter out conflicts where all involved subjects are ontology URIs
                filtered_conflicts = []
                for conflict in conflicts:
                    # Check if conflict involves user data (URIs in user namespace)
                    involves_user_data = any(
                        str(config.user_namespace) in str(triple[0])  # subject
                        for triple in conflict.triples
                    )
                    if involves_user_data:
                        filtered_conflicts.append(conflict)
                all_conflicts.extend(filtered_conflicts)
        
        logger.debug(f"Found {len(all_conflicts)} conflicts in user data (ontology conflicts filtered)")
    except Exception as e:
        logger.warning(f"Conflict detection failed: {e}")

    # Save graph to persistence
    try:
        graph.save_to_file(config.persistence_path)
        logger.debug(f"Saved graph to {config.persistence_path}")
    except Exception as e:
        logger.error(f"Failed to save graph: {e}", exc_info=True)

    # Prepare response
    total_inferred = owl_inferred_count + sparql_inferred_count
    response_text = (
        f"✓ Added {added_count} explicit triple(s) from your input.\n"
        f"✓ Inferred {total_inferred} additional triple(s) "
        f"({owl_inferred_count} via OWL-RL, {sparql_inferred_count} via SPARQL rules).\n"
        f"\nTotal triples in knowledge graph: {graph.get_triple_count()}"
    )


    if all_conflicts:
        response_text += f"\n\n⚠ Found {len(all_conflicts)} conflicts."
        for conflict in all_conflicts:
            response_text += f"\n- {conflict.type}: {conflict.triples}"

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
        uncertain_results = list(graph.query(uncertain_query))  # Convert to list to avoid consuming generator
        if uncertain_results:
            response_text += f"\n\n⚠ {len(uncertain_results)} inference(s) need verification."
            response_text += "\nUse the verify_inference tool to confirm or reject them."
    except Exception as e:
        logger.warning(f"Failed to query for uncertain inferences: {e}")

    return [TextContent(type="text", text=response_text)]


__all__ = ["ADD_MEMORY_TOOL", "add_memory"]
