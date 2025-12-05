"""
OWL-RL reasoner wrapper.

Applies OWL-RL reasoning to derive implicit facts from ontologies and data.
"""

from typing import Optional

import owlrl
from rdflib import Graph

from smart_memory.config import config
from smart_memory.logging_config import get_logger
from smart_memory.vocabulary import RDF, SOURCE, TIMESTAMP, CONFIDENCE
from datetime import datetime, timezone

logger = get_logger(__name__)


class Reasoner:
    """
    Wrapper around the owlrl library for OWL-RL reasoning.

    Applies deductive closure to derive implicit facts from ontological axioms.
    """

    def __init__(self, max_depth: Optional[int] = None):
        """
        Initialize the reasoner.

        Args:
            max_depth: Maximum inference depth (defaults to config.max_inference_depth)
        """
        self.max_depth = max_depth or config.max_inference_depth

    def apply_closure(self, provenance_graph) -> int:
        """
        Apply OWL-RL reasoning to the knowledge graph.

        Adds inferred triples directly to the graph with provenance metadata.

        Args:
            provenance_graph: ProvenanceGraph instance to reason over

        Returns:
            Number of new triples inferred
        """
        logger.info("Applying OWL-RL reasoning...")

        # Count triples before reasoning
        before_count = len(provenance_graph.graph)

        # Create a separate graph for reasoning to track what's inferred
        reasoning_graph = Graph()

        # Copy all triples from the main graph
        for triple in provenance_graph.graph:
            reasoning_graph.add(triple)

        # Apply OWL-RL reasoning
        # This modifies the graph in place, adding inferred triples
        try:
            owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(reasoning_graph)
        except Exception as e:
            logger.error(f"OWL-RL reasoning failed: {e}", exc_info=True)
            raise

        # Count triples after reasoning
        after_count = len(reasoning_graph)
        inferred_count = after_count - before_count

        logger.info(f"OWL-RL reasoning inferred {inferred_count} new triples")

        # Add inferred triples to the provenance graph with metadata
        if config.enable_provenance_tracking:
            for triple in reasoning_graph:
                if triple not in provenance_graph.graph:
                    # This is a newly inferred triple
                    s, p, o = triple
                    provenance_graph.add_triple_with_provenance(
                        subject=s,
                        predicate=p,
                        obj=o,
                        source="owlrl",
                        confidence=1.0,  # OWL-RL inferences are always high confidence
                        uncertain=False,
                    )
        else:
            # Fast path: just add triples without provenance
            for triple in reasoning_graph:
                if triple not in provenance_graph.graph:
                    provenance_graph.graph.add(triple)

        return inferred_count

    def apply_incremental_closure(self, provenance_graph, new_triples: list) -> int:
        """
        Apply OWL-RL reasoning incrementally on new triples only.

        This is more efficient than recomputing the full closure when only
        a few triples have been added.

        Args:
            provenance_graph: ProvenanceGraph instance
            new_triples: List of newly added triples to reason over

        Returns:
            Number of new triples inferred

        Note: For simplicity, this currently just calls apply_closure.
        A true incremental implementation would only reason over the new triples
        and their direct neighbors in the graph.
        """
        # TODO: Implement true incremental reasoning
        # For now, just apply full closure
        logger.debug(
            f"Incremental reasoning requested for {len(new_triples)} new triples, "
            "applying full closure"
        )
        return self.apply_closure(provenance_graph)

    def explain_inference(self, provenance_graph, subject, predicate, obj) -> list[str]:
        """
        Explain why a triple was inferred (debugging utility).

        Args:
            provenance_graph: ProvenanceGraph instance
            subject: Subject of the triple
            predicate: Predicate of the triple
            obj: Object of the triple

        Returns:
            List of explanation strings

        Note: This is a placeholder for future implementation.
        OWL-RL reasoning explanations require tracking the inference rules used.
        """
        # TODO: Implement explanation generation
        # This would require modifying the reasoning process to track
        # which ontology axioms were used for each inference

        explanations = [
            f"Triple ({subject}, {predicate}, {obj}) was inferred via OWL-RL reasoning",
            "Explanation details not yet implemented",
        ]

        return explanations


__all__ = ["Reasoner"]
