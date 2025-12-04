"""
Unit tests for ProvenanceGraph.query() method.

Tests different SPARQL query types and result formats.
"""

import pytest
from rdflib import Namespace, Literal as RDFLiteral, Graph
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.vocabulary import FOAF

USER_NS = Namespace("http://semanticmemory.org/user#")


class TestQueryTypes:
    """Test different SPARQL query types return correct result types."""
    
    def test_select_query_returns_list_of_dicts(self):
        """SELECT queries should return a list of dictionaries."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            :Alice foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        
        assert isinstance(results, list), "SELECT should return a list"
        assert len(results) == 1, "Should have one result"
        assert isinstance(results[0], dict), "Each result should be a dict"
        assert "name" in results[0], "Result should have 'name' key"
        assert str(results[0]["name"]) == "Alice"
    
    def test_ask_query_returns_boolean(self):
        """ASK queries should return a boolean."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.knows,
            USER_NS.Bob,
            source="user"
        )
        
        # Query that should return True
        query_true = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        ASK {
            :Alice foaf:knows :Bob .
        }
        """
        
        result = graph.query(query_true)
        assert isinstance(result, bool), "ASK should return a boolean"
        assert result is True, "Should return True when triple exists"
        
        # Query that should return False
        query_false = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        ASK {
            :Alice foaf:knows :Charlie .
        }
        """
        
        result = graph.query(query_false)
        assert isinstance(result, bool), "ASK should return a boolean"
        assert result is False, "Should return False when triple doesn't exist"
    
    def test_construct_query_returns_graph(self):
        """CONSTRUCT queries should return a Graph."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        CONSTRUCT {
            ?person a foaf:Person .
        }
        WHERE {
            ?person foaf:name ?name .
        }
        """
        
        result = graph.query(query)
        
        assert isinstance(result, Graph), "CONSTRUCT should return a Graph"
        assert len(result) > 0, "Constructed graph should have triples"
    
    def test_describe_query(self):
        """DESCRIBE queries should work correctly."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.age,
            RDFLiteral(30),
            source="user"
        )
        
        query = """
        DESCRIBE :Alice
        """
        
        result = graph.query(query)
        
        # DESCRIBE returns a Graph
        assert isinstance(result, Graph), "DESCRIBE should return a Graph"


class TestQueryTypeDetection:
    """Test that query type detection works correctly."""
    
    def test_query_type_detection_with_prefixes(self):
        """Query type detection should work with PREFIX declarations."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        
        # ASK with PREFIX
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        ASK {
            :Alice foaf:name ?name .
        }
        """
        
        result = graph.query(query)
        assert isinstance(result, bool), "Should detect ASK query with PREFIX"
    
    def test_query_type_detection_case_insensitive(self):
        """Query type detection should be case-insensitive."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        
        # Lowercase 'ask'
        query = """
        ask {
            :Alice <http://xmlns.com/foaf/0.1/name> ?name .
        }
        """
        
        result = graph.query(query)
        assert isinstance(result, bool), "Should detect lowercase 'ask'"
    
    def test_query_type_detection_with_comments(self):
        """Query type detection should work with SPARQL comments."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        
        # Query with comments
        query = """
        # This is a comment
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        # Another comment
        ASK {
            :Alice foaf:name ?name .
        }
        """
        
        result = graph.query(query)
        assert isinstance(result, bool), "Should detect ASK with comments"


class TestEmptyResults:
    """Test queries that return empty results."""
    
    def test_empty_select_results(self):
        """SELECT with no matching triples should return empty list."""
        graph = ProvenanceGraph()
        
        query = """
        SELECT ?s ?p ?o WHERE {
            ?s ?p ?o .
        }
        """
        
        results = graph.query(query)
        
        assert isinstance(results, list), "Should return a list"
        assert len(results) == 0, "Should be empty"
    
    def test_ask_false_result(self):
        """ASK that doesn't match should return False."""
        graph = ProvenanceGraph()
        
        query = """
        ASK {
            :NonExistent :property :value .
        }
        """
        
        result = graph.query(query)
        
        assert isinstance(result, bool), "Should return boolean"
        assert result is False, "Should be False"
    
    def test_empty_construct_result(self):
        """CONSTRUCT with no matching triples should return empty graph."""
        graph = ProvenanceGraph()
        
        query = """
        CONSTRUCT {
            ?s ?p ?o .
        }
        WHERE {
            ?s ?p ?o .
        }
        """
        
        result = graph.query(query)
        
        assert isinstance(result, Graph), "Should return a Graph"
        assert len(result) == 0, "Should be empty"


class TestMultipleResults:
    """Test queries that return multiple results."""
    
    def test_select_multiple_rows(self):
        """SELECT should return all matching rows."""
        graph = ProvenanceGraph()
        
        # Add multiple people
        for name in ["Alice", "Bob", "Charlie"]:
            graph.add_triple_with_provenance(
                USER_NS[name],
                FOAF.name,
                RDFLiteral(name),
                source="user"
            )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?name WHERE {
            ?person foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        
        assert len(results) == 3, "Should return 3 results"
        names = [str(r["name"]) for r in results]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names
    
    def test_select_multiple_columns(self):
        """SELECT should return all requested columns."""
        graph = ProvenanceGraph()
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.age,
            RDFLiteral(30),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?age WHERE {
            :Alice foaf:name ?name .
            :Alice foaf:age ?age .
        }
        """
        
        results = graph.query(query)
        
        assert len(results) == 1
        assert "name" in results[0]
        assert "age" in results[0]
        assert str(results[0]["name"]) == "Alice"
        assert int(results[0]["age"]) == 30


class TestComplexQueries:
    """Test more complex SPARQL features."""
    
    def test_filter_clause(self):
        """Test FILTER clause in SELECT."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.age,
            RDFLiteral(30),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Bob,
            FOAF.age,
            RDFLiteral(20),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
            FILTER(?age > 25)
        }
        """
        
        results = graph.query(query)
        
        assert len(results) == 1, "Should only return Alice (age > 25)"
        assert int(results[0]["age"]) == 30
    
    def test_optional_clause(self):
        """Test OPTIONAL clause in SELECT."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice"),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.mbox,
            RDFLiteral("alice@example.com"),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Bob,
            FOAF.name,
            RDFLiteral("Bob"),
            source="user"
        )
        # Bob has no email
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?email WHERE {
            ?person foaf:name ?name .
            OPTIONAL { ?person foaf:mbox ?email }
        }
        """
        
        results = graph.query(query)
        
        assert len(results) == 2, "Should return both Alice and Bob"
        
        # Find Alice's result
        alice_result = [r for r in results if str(r["name"]) == "Alice"][0]
        assert "email" in alice_result
        
        # Find Bob's result
        bob_result = [r for r in results if str(r["name"]) == "Bob"][0]
        # Bob should have None or not have the email key
        assert bob_result.get("email") is None or "email" not in bob_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
