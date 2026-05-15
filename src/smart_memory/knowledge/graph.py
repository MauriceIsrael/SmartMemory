"""
Provenance-aware RDF graph wrapper.

Extends RDFLib's Graph with automatic provenance tracking for all triples.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional, Any

from rdflib import Graph, URIRef, Literal as RDFLiteral, BNode
from rdflib.namespace import RDF, XSD

from smart_memory.config import config
from smart_memory.vocabulary import (
    SEM,
    SOURCE,
    SOURCE_RULE,
    TIMESTAMP,
    CONFIDENCE,
    UNCERTAIN,
    get_provenance_predicates,
)


class ProvenanceGraph:
    """
    RDF graph with automatic provenance tracking.

    Wraps rdflib.Graph and adds metadata about the source, confidence,
    and timestamp for every triple added to the graph.
    """

    def __init__(self, identifier: Optional[str] = None):
        """
        Initialize a new provenance-aware graph.

        Args:
            identifier: Optional identifier for the graph (useful for named graphs)
        """
        self.graph = Graph(identifier=identifier)
        self.pending_verifications_graph = Graph()
        self.rejected_verifications_graph = Graph()
        self._triple_count: int = 0  # O(1) counter for non-provenance triples
        self._bind_namespaces()
        self._bind_namespaces(graph=self.pending_verifications_graph)
        self._bind_namespaces(graph=self.rejected_verifications_graph)

    def _bind_namespaces(self, graph: Optional[Graph] = None) -> None:
        """Bind common namespaces for readable serialization."""
        from smart_memory.vocabulary import FOAF, RDFS, SKOS, OWL, SCHEMA
        
        target_graph = graph if graph is not None else self.graph
        # Bind default namespace (empty prefix) for ':Entity' syntax
        target_graph.bind("", config.user_namespace)
        target_graph.bind("sem", SEM)
        target_graph.bind("foaf", FOAF)
        target_graph.bind("rdfs", RDFS)
        target_graph.bind("skos", SKOS)
        target_graph.bind("owl", OWL)
        target_graph.bind("schema", SCHEMA)
        target_graph.bind("rdf", RDF)
        target_graph.bind("xsd", XSD)
    
    def add_pending_verification(self, verification_request) -> None:
        """Adds a verification request to the pending graph."""
        graph = self.pending_verifications_graph
        s, p, o = verification_request.triple
        statement_node = BNode()
        graph.add((statement_node, RDF.type, RDF.Statement))
        graph.add((statement_node, RDF.subject, s))
        graph.add((statement_node, RDF.predicate, p))
        graph.add((statement_node, RDF.object, o))
        graph.add((statement_node, SEM.sourceRule, RDFLiteral(verification_request.source_rule)))
        graph.add((statement_node, SEM.confidence, RDFLiteral(verification_request.confidence, datatype=XSD.decimal)))

    def accept_verification(self, triple: tuple) -> bool:
        """
        Accept a pending verification and move it to the main graph.
        
        Args:
            triple: Tuple of (subject, predicate, object) as URIRefs/Literals
            
        Returns:
            bool: True if found and moved, False otherwise
        """
        s, p, o = triple
        found = False
        # Look for the statement in the pending graph
        for stmt in self.pending_verifications_graph.subjects(RDF.subject, s):
            if (stmt, RDF.predicate, p) in self.pending_verifications_graph and \
               (stmt, RDF.object, o) in self.pending_verifications_graph:
                found = True
                # Extract metadata
                confidence_val = self.pending_verifications_graph.value(stmt, SEM.confidence)
                confidence = float(confidence_val) if confidence_val else 1.0
                rule = self.pending_verifications_graph.value(stmt, SEM.sourceRule)
                
                # Add to main graph with provenance
                self.add_triple_with_provenance(
                    s, p, o,
                    source="user-verified",
                    confidence=confidence,
                    source_rule=str(rule) if rule else None
                )
                
                # Remove from pending graph
                self.pending_verifications_graph.remove((stmt, None, None))
                break
        return found

    def reject_verification(self, triple: tuple) -> bool:
        """
        Reject a pending verification and move it to the rejected graph.
        
        Args:
            triple: Tuple of (subject, predicate, object)
            
        Returns:
            bool: True if found and moved, False otherwise
        """
        s, p, o = triple
        found = False
        for stmt in self.pending_verifications_graph.subjects(RDF.subject, s):
            if (stmt, RDF.predicate, p) in self.pending_verifications_graph and \
               (stmt, RDF.object, o) in self.pending_verifications_graph:
                found = True
                # Move everything related to this statement to the rejected graph
                for p_attr, o_attr in self.pending_verifications_graph.predicate_objects(stmt):
                    self.rejected_verifications_graph.add((stmt, p_attr, o_attr))
                
                # ALSO add the original triple to the rejected graph for easy lookup/testing
                self.rejected_verifications_graph.add((s, p, o))
                
                # Remove from pending graph
                self.pending_verifications_graph.remove((stmt, None, None))
                break
        return found




    def add_triple_with_provenance(
        self,
        subject: URIRef | BNode,
        predicate: URIRef,
        obj: URIRef | BNode | RDFLiteral,
        source: Literal["user", "owlrl", "sparql-rule", "user-verified"],
        confidence: float = 1.0,
        source_rule: Optional[str] = None,
        uncertain: bool = False,
    ) -> None:
        """
        Add a triple to the graph with provenance metadata.

        Args:
            subject: Subject of the triple
            predicate: Predicate of the triple
            obj: Object of the triple
            source: Origin of the triple (user/owlrl/sparql-rule)
            confidence: Confidence score (0.0-1.0)
            source_rule: Optional URI of the SPARQL rule that generated this
            uncertain: Whether this triple needs verification
        """
        if not config.enable_provenance_tracking:
            # Fast path: just add the triple without metadata
            self.graph.add((subject, predicate, obj))
            self._triple_count += 1
            return

        # Add the main triple
        self.graph.add((subject, predicate, obj))
        self._triple_count += 1

        # Create a reification node for provenance
        # Using blank node to avoid polluting the main namespace
        provenance_node = BNode()

        # Link provenance to the triple using RDF reification
        self.graph.add((provenance_node, RDF.type, RDF.Statement))
        self.graph.add((provenance_node, RDF.subject, subject))
        self.graph.add((provenance_node, RDF.predicate, predicate))
        self.graph.add((provenance_node, RDF.object, obj))

        # Add provenance metadata
        self.graph.add((provenance_node, SOURCE, RDFLiteral(source)))
        self.graph.add(
            (
                provenance_node,
                TIMESTAMP,
                RDFLiteral(datetime.now(timezone.utc).isoformat(), datatype=XSD.dateTime),
            )
        )
        self.graph.add(
            (provenance_node, CONFIDENCE, RDFLiteral(confidence, datatype=XSD.decimal))
        )
        self.graph.add((provenance_node, UNCERTAIN, RDFLiteral(uncertain, datatype=XSD.boolean)))

        if source_rule:
            self.graph.add((provenance_node, SOURCE_RULE, URIRef(source_rule)))

    def add_triple(
        self,
        subject: URIRef | BNode,
        predicate: URIRef,
        obj: URIRef | BNode | RDFLiteral,
    ) -> None:
        """
        Add a triple without provenance tracking (for internal use).

        Args:
            subject: Subject of the triple
            predicate: Predicate of the triple
            obj: Object of the triple
        """
        self.graph.add((subject, predicate, obj))
        self._triple_count += 1

    def query(self, sparql: str) -> Any:
        """
        Execute a SPARQL query against the graph.

        Args:
            sparql: SPARQL query string

        Returns:
            List of result bindings (SELECT), boolean (ASK), or Graph (CONSTRUCT/DESCRIBE)
        """
        from typing import Any
        import re
        
        results = self.graph.query(sparql)
        
        # Detect query type by checking the SPARQL string
        # Remove comments (lines starting with #) and collapse whitespace
        query_no_comments = re.sub(r'#[^\n]*', '', sparql)
        query_upper = ' '.join(query_no_comments.split()).upper()
        
        # Handle ASK queries - return boolean
        if re.search(r'\bASK\b', query_upper):
            return bool(results)
            
        # Handle CONSTRUCT queries - return Graph
        if re.search(r'\bCONSTRUCT\b', query_upper):
            return results.graph if hasattr(results, 'graph') else results
            
        # Handle DESCRIBE queries - return Graph
        if re.search(r'\bDESCRIBE\b', query_upper):
            return results.graph if hasattr(results, 'graph') else results
            
        # Handle SELECT queries - return list of dicts
        return [dict(row.asdict()) for row in results]

    def serialize(self, format: str = "turtle", destination: Optional[Path] = None) -> str:
        """
        Serialize the graph to a string or file.

        Args:
            format: Serialization format (turtle, xml, json-ld, etc.)
            destination: Optional file path to write to

        Returns:
            Serialized graph as string (if destination is None)
        """
        if destination:
            self.graph.serialize(destination=str(destination), format=format)
            return ""
        return self.graph.serialize(format=format)

    def parse(self, source: Path | str, format: str = "turtle") -> None:
        """
        Parse RDF data from a file or string.

        Args:
            source: File path or RDF string
            format: RDF format (turtle, xml, json-ld, etc.)
        """
        if isinstance(source, Path):
            self.graph.parse(str(source), format=format)
        else:
            self.graph.parse(data=source, format=format)

    def load_from_file(self, path: Path) -> None:
        """
        Load graph from persistence file.

        Args:
            path: Path to the main RDF file
        """
        if path.exists():
            format = "turtle" if path.suffix == ".ttl" else "xml"
            self.parse(source=path, format=format)
        
        # Load pending verifications graph
        pending_path = path.with_stem(f"{path.stem}_pending")
        if pending_path.exists():
            format = "turtle" if path.suffix == ".ttl" else "xml"
            self.pending_verifications_graph.parse(str(pending_path), format=format)
        
        # Load rejected verifications graph
        rejected_path = path.with_stem(f"{path.stem}_rejected")
        if rejected_path.exists():
            self.rejected_verifications_graph.parse(str(rejected_path), format=format)

        # Recompute the O(1) counter once after loading (only time we do the O(n) scan)
        provenance_predicates = set(get_provenance_predicates())
        provenance_predicates.update([RDF.type, RDF.subject, RDF.predicate, RDF.object])
        self._triple_count = sum(
            1 for _, p, _ in self.graph if p not in provenance_predicates
        )

    def save_to_file(self, path: Path) -> None:
        """
        Save all graphs to persistence files.

        Args:
            path: Path to save the main RDF file
        """
        format = "turtle" if path.suffix == ".ttl" else "xml"
        
        # Save main graph
        self.serialize(format=format, destination=path)
        
        # Save pending verifications graph
        pending_path = path.with_stem(f"{path.stem}_pending")
        self.pending_verifications_graph.serialize(destination=str(pending_path), format=format)
        
        # Save rejected verifications graph
        rejected_path = path.with_stem(f"{path.stem}_rejected")
        self.rejected_verifications_graph.serialize(destination=str(rejected_path), format=format)

    def get_triple_count(self) -> int:
        """Return the number of triples in the graph (excluding provenance). O(1)."""
        return self._triple_count

    def get_provenance_stats(self) -> dict[str, int]:
        """
        Get statistics about triple sources.

        Returns:
            Dictionary with counts per source type
        """
        query = """
        SELECT ?source (COUNT(?source) AS ?count)
        WHERE {
            ?stmt a rdf:Statement ;
                  sem:source ?source .
        }
        GROUP BY ?source
        """
        results = self.query(query)
        return {str(row["source"]): int(row["count"]) for row in results}

    def __len__(self) -> int:
        """Return total number of triples including provenance."""
        return len(self.graph)

    def __repr__(self) -> str:
        return f"ProvenanceGraph(triples={self.get_triple_count()}, total_with_provenance={len(self)})"


__all__ = ["ProvenanceGraph"]
