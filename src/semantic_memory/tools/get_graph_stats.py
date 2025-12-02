from typing import Any
from mcp.types import Tool, TextContent
from semantic_memory.logging_config import get_logger
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.inference.rule_engine import RuleEngine
from semantic_memory.knowledge.conflicts import ContradictoryLiteralDetector, DisjointClassDetector, FunctionalPropertyDetector

logger = get_logger(__name__)

GET_GRAPH_STATS_TOOL = Tool(
    name="get_graph_stats",
    description="Retrieve statistics about the knowledge graph.",
    inputSchema={"type": "object", "properties": {}},
)

async def get_graph_stats(
    arguments: dict[str, Any],
    graph: ProvenanceGraph,
    rule_engine: RuleEngine,
) -> list[TextContent]:
    
    total_triples = graph.get_triple_count()
    provenance_stats = graph.get_provenance_stats()
    explicit_triples = provenance_stats.get("user", 0)
    inferred_owlrl = provenance_stats.get("owlrl", 0)
    inferred_sparql = provenance_stats.get("sparql-rule", 0)
    inferred_triples = inferred_owlrl + inferred_sparql

    pending_verifications = len(graph.pending_verifications_graph)
    rejected_verifications = len(graph.rejected_verifications_graph)

    # Detect conflicts
    detectors = [ContradictoryLiteralDetector(), DisjointClassDetector(), FunctionalPropertyDetector()]
    all_conflicts = []
    for detector in detectors:
        all_conflicts.extend(detector.detect_conflicts(graph))
    conflict_count = len(all_conflicts)

    ontologies_loaded = [] # Add logic to get this
    
    rules_loaded = {
        "default_count": len([r for r in rule_engine.rules if r.source == "default"]),
        "custom_count": len([r for r in rule_engine.rules if r.source == "custom"]),
        "active_count": len([r for r in rule_engine.rules if r.is_active]),
    }
    
    # Add more stats as needed
    
    response_text = (
        f"**Knowledge Graph Stats**\n"
        f"- Total Triples: {total_triples}\n"
        f"- Explicit Triples: {explicit_triples}\n"
        f"- Inferred Triples: {inferred_triples}\n"
        f"  - OWL-RL: {inferred_owlrl}\n"
        f"  - SPARQL: {inferred_sparql}\n"
        f"- Rules Loaded: {rules_loaded['active_count']} active\n"
        f"- Pending Verifications: {pending_verifications}\n"
        f"- Rejected Verifications: {rejected_verifications}\n"
        f"- Conflicts Detected: {conflict_count}"
    )
    
    return [TextContent(type="text", text=response_text)]
