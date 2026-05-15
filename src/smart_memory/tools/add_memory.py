"""
add_memory MCP tool implementation.

Adds natural language statements or explicit RDF triples to the knowledge graph.
"""

from typing import Any

from mcp.types import Tool, TextContent

from smart_memory.logging_config import get_logger
from smart_memory.tools.forget_memory import forget_memory
from smart_memory.nlp.triple_extractor import TripleExtractor
from smart_memory.config import config

logger = get_logger(__name__)


# Tool definition
ADD_MEMORY_TOOL = Tool(
    name="add_memory",
    description=(
        "Store a fact in semantic memory using RDF triple notation."
        "\n\n**CRITICAL - ANTI-HALLUCINATION RULES:**"
        "\n❌ NEVER suggest example facts and then add them as if user confirmed"
        "\n❌ NEVER assume user response validates your examples"
        "\n❌ NEVER invent names, relationships, dates, or any entities"
        "\n❌ NEVER add facts based on your assumptions or knowledge"
        "\n✓ ONLY add facts that user EXPLICITLY and UNAMBIGUOUSLY stated"
        "\n✓ If unsure what user meant, ASK for clarification before adding"
        "\n✓ If user says 'I don't know', do NOT add anything"
        "\n\n**Example of INCORRECT behavior (HALLUCINATION):**"
        "\nUser: 'Who is Alice's father?'"
        "\nYou: 'I don't know. Can you tell me? Example: :Alice :hasFather :Bob'"
        "\nUser: 'ok' [or any vague response]"
        "\nYou: add_memory(':Alice :hasFather :Bob') ← WRONG! User never said this!"
        "\n\n**Example of CORRECT behavior:**"
        "\nUser: 'Alice's father is Bob'"
        "\nYou: add_memory(':Alice :hasFather :Bob') ← CORRECT!"
        "\n\n**What happens when you add a fact:**"
        "\n1. Fact is stored with confidence=1.0 (explicit user fact)"
        "\n2. SPARQL inference rules automatically run in background"
        "\n3. New facts may be inferred (e.g., symmetry, transitivity)"
        "\n4. Check get_pending_verifications() for inferred facts needing approval"
        "\n\n**Supported predicates:**"
        "\n- foaf:knows, foaf:friend - Social relationships"
        "\n- schema:worksFor, schema:colleague - Work relationships"  
        "\n- rdf:type - Classifications"
        "\n- :customPredicate - Any custom predicate (user namespace)"
        "\n\n**Format:** ':Subject predicate:name :Object'"
        "\n\n**Examples:**"
        "\n  add_memory(':User foaf:knows :Alice')"
        "\n  add_memory(':User :isFriendOf :Bob')  # Custom predicate"
        "\n  add_memory(':Charlie schema:worksFor :AcmeCorp')"
       "\n\n**Note:** Use ':User' for current user, ':' prefix for all user entities."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "RDF triple: ':Subject predicate :Object'",
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
    inference_manager: Any = None,
) -> list[TextContent]:
    """
    Add a memory to the knowledge graph.

    Args:
        arguments: Tool arguments containing 'input' and optional 'format'
        graph: ProvenanceGraph instance
        reasoner: Reasoner instance for OWL-RL inference
        triple_extractor: TripleExtractor for NL processing
        rule_engine: RuleEngine instance
        inference_manager: InferenceManager instance for background reasoning

    Returns:
        List of TextContent with results
    """
    input_text = arguments["input"]
    format_type = arguments.get("format", "natural_language")

    logger.info(f"add_memory called with input: {input_text[:100]}...")

    # Extract triples from input
    # Detect triple notation by checking for common patterns:
    # - Starts with ':' (e.g., ":Alice foaf:knows :Bob")
    # - Starts with '<' (e.g., "<http://...> predicate <http://...>")
    # - Contains ' : ' or ' foaf:' or ' schema:' (explicit predicates)
    # Heuristic: is it triple notation?
    # Must have 3 parts if we detect triple-like characters
    input_parts = input_text.strip().split()
    is_triple_notation = (
        format_type == "triple_notation" 
        or (len(input_parts) == 3 and (
            input_text.strip().startswith(":")
            or input_text.strip().startswith("<")
            or " foaf:" in input_text
            or " schema:" in input_text
            or " rdf:" in input_text
            or " :" in input_text
        ))
    )

    
    if is_triple_notation:
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

    # Capture graph size before inference
    triples_before = graph.get_triple_count()
    
    # Trigger background inference and wait for completion
    inferred_facts_text = ""
    if inference_manager:
        logger.info("Triggering background inference...")
        inference_manager.trigger_inference()
        
        # Wait briefly for inference to complete (max 2 seconds)
        # This allows us to report what was inferred
        import asyncio
        try:
            await asyncio.wait_for(inference_manager.wait_until_idle(), timeout=2.0)
            
            # Capture graph size after inference
            triples_after = graph.get_triple_count()
            inferred_count = triples_after - triples_before - added_count
            
            if inferred_count > 0:
                # Query the most recently added triples (provenance = sparql-rule)
                inferred_triples_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX sem: <http://semanticmemory.org/vocab#>
                SELECT ?s ?p ?o WHERE {
                    ?stmt a rdf:Statement ;
                          rdf:subject ?s ;
                          rdf:predicate ?p ;
                          rdf:object ?o ;
                          sem:source ?source .
                    FILTER(?source = "sparql-rule")
                }
                LIMIT 10
                """
                try:
                    results = graph.query(inferred_triples_query)
                    if results:
                        inferred_facts_text = f"\n\n✨ **Inferred {inferred_count} new facts:**"
                        for i, row in enumerate(results[:5], 1):  # Show max 5
                            s = str(row['s']).replace('http://semanticmemory.org/user#', ':')
                            p = str(row['p']).replace('http://xmlns.com/foaf/0.1/', 'foaf:').replace('https://schema.org/', 'schema:')
                            o = str(row['o']).replace('http://semanticmemory.org/user#', ':')
                            inferred_facts_text += f"\n  • {s} {p} {o}"
                        if inferred_count > 5:
                            inferred_facts_text += f"\n  ... and {inferred_count - 5} more"
                except Exception as e:
                    logger.warning(f"Failed to query inferred triples: {e}")
                    inferred_facts_text = f"\n\n✨ Inferred {inferred_count} new facts."
        except asyncio.TimeoutError:
            logger.debug("Inference still running (async)")
            inferred_facts_text = "\n\n⏳ Background inference in progress..."
    else:
        logger.warning("InferenceManager not provided, skipping background inference trigger")

    # Check for conflicts after adding
    from smart_memory.knowledge.conflicts import ContradictoryLiteralDetector
    conflict_detector = ContradictoryLiteralDetector()
    conflicts = conflict_detector.detect_conflicts(graph)
    
    conflict_warning = ""
    if conflicts:
        conflict_warning = f"\n\n⚠️ **Found {len(conflicts)} potential conflicts!**"
        for conflict in conflicts[:3]: # Show max 3
            conflict_warning += f"\n  • Conflicting fact detected for type '{conflict.type}'"

    # Save graph to persistence using the configured backend
    from smart_memory.knowledge.persistence import get_persistence_backend
    try:
        persistence = get_persistence_backend()
        persistence.save(graph)
        logger.debug(f"Saved graph using {type(persistence).__name__}")
    except Exception as e:
        logger.error(f"Failed to save graph: {e}", exc_info=True)

    return [
        TextContent(
            type="text",
            text=f"Added {added_count} triples to memory.{inferred_facts_text}{conflict_warning}"
        )
    ]


__all__ = ["ADD_MEMORY_TOOL", "add_memory"]

