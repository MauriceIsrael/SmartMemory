from abc import ABC, abstractmethod
from typing import List
from smart_memory.knowledge.graph import ProvenanceGraph
from collections import defaultdict
from datetime import datetime, UTC
from smart_memory.vocabulary import OWL
from smart_memory.logging_config import get_logger
from rdflib import Literal
from rdflib.namespace import RDF

logger = get_logger(__name__)

class Conflict:
    def __init__(self, type: str, triples: List, provenance: List, detected_at: str, resolved: bool = False):
        self.id = ""
        self.type = type
        self.triples = triples
        self.provenance = provenance
        self.detected_at = detected_at
        self.resolved = resolved

class ConflictDetector(ABC):
    @abstractmethod
    def detect_conflicts(self, graph: ProvenanceGraph) -> List[Conflict]:
        pass

class ContradictoryLiteralDetector(ConflictDetector):
    def detect_conflicts(self, graph: ProvenanceGraph) -> List[Conflict]:
        query = """
        SELECT ?subject ?predicate (GROUP_CONCAT(?object; separator="||") AS ?objects)
        WHERE {
            ?subject ?predicate ?object .
            FILTER(isLiteral(?object))
        }
        GROUP BY ?subject ?predicate
        HAVING (COUNT(DISTINCT ?object) > 1) # Ensure distinct objects
        """
        results = graph.query(query)
        logger.debug(f"ContradictoryLiteralDetector query results: {results}")
        
        conflicts = []
        for row in results:
            objects = set(row["objects"].split("||")) # Use set to handle distinct objects
            logger.debug(f"ContradictoryLiteralDetector row objects: {objects}")
            
            # Re-fetch the actual triples from the graph for precise representation
            conflicting_triples = []
            for obj_val in objects:
                # Need to convert string back to Literal for matching if necessary
                # This is a simplification; a full solution would re-parse the literal
                # For now, we assume the string is enough to identify the conflict.
                # The query already filters for literals, so obj_val is a string representation.
                # We need the rdflib.Literal object for assertion
                # This makes the test slightly brittle if literal representations differ
                conflicting_triples.append((row["subject"], row["predicate"], Literal(obj_val)))

            conflict = Conflict(
                type="contradictory_literal",
                triples=conflicting_triples,
                provenance=[], # Add provenance information
                detected_at=datetime.now(UTC).isoformat(),
            )
            conflicts.append(conflict)
        return conflicts

class DisjointClassDetector(ConflictDetector):
    def detect_conflicts(self, graph: ProvenanceGraph) -> List[Conflict]:
        query = f"""
        SELECT ?subject ?class1 ?class2
        WHERE {{
            ?class1 <{OWL.disjointWith}> ?class2 .
            ?subject a ?class1 .
            ?subject a ?class2 .
        }}
        """
        results = graph.query(query)
        
        conflicts = []
        for row in results:
            conflict = Conflict(
                type="disjoint_class",
                triples=[
                    (row["subject"], RDF.type, row["class1"]),
                    (row["subject"], RDF.type, row["class2"]),
                ],
                provenance=[], # Add provenance information
                detected_at=datetime.now(UTC).isoformat(),
            )
            conflicts.append(conflict)
        return conflicts

class FunctionalPropertyDetector(ConflictDetector):
    def detect_conflicts(self, graph: ProvenanceGraph) -> List[Conflict]:
        query = f"""
        SELECT ?subject ?predicate (GROUP_CONCAT(?object; separator="||") AS ?objects)
        WHERE {{
            ?predicate a <{OWL.FunctionalProperty}> .
            ?subject ?predicate ?object .
        }}
        GROUP BY ?subject ?predicate
        HAVING (COUNT(?object) > 1)
        """
        results = graph.query(query)
        
        conflicts = []
        for row in results:
            objects = set(row["objects"].split("||"))
            if len(objects) > 1: # Check for more than one distinct object
                conflicting_triples = []
                for obj_val in objects:
                    conflicting_triples.append((row["subject"], row["predicate"], Literal(obj_val)))

                conflict = Conflict(
                    type="functional_property",
                    triples=conflicting_triples,
                    provenance=[], # Add provenance information
                    detected_at=datetime.now(UTC).isoformat(),
                )
                conflicts.append(conflict)
        return conflicts
