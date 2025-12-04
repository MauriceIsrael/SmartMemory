"""
Unit tests for SPARQL edge cases and error conditions.

Tests unusual inputs, special characters, and boundary conditions.
"""

import pytest
from rdflib import Namespace, Literal as RDFLiteral
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.vocabulary import FOAF

USER_NS = Namespace("http://semanticmemory.org/user#")


class TestEmptyAndNull:
    """Test empty and null inputs."""
    
    def test_empty_query_string(self):
        """Empty query should raise an error."""
        graph = ProvenanceGraph()
        
        with pytest.raises(Exception):
            graph.query("")
    
    def test_whitespace_only_query(self):
        """Whitespace-only query should raise an error."""
        graph = ProvenanceGraph()
        
        with pytest.raises(Exception):
            graph.query("   \n\t  ")
    
    def test_query_with_unicode_french(self):
        """Test queries with French characters."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Jérémie,
            FOAF.name,
            RDFLiteral("Jérémie"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            :Jérémie foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert "Jérémie" in str(results[0]["name"])
    
    def test_query_with_emoji(self):
        """Test queries with emoji characters."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice 😊"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
            FILTER(CONTAINS(?name, "😊"))
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1


class TestSpecialCharacters:
    """Test special characters in queries and data."""
    
    def test_query_with_quotes_in_literals(self):
        """Test literals containing quotes."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral('Alice "The Great"'),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert "Alice" in str(results[0]["name"])
    
    def test_query_with_escaped_quotes(self):
        """Test FILTER with escaped quotes."""
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
            ?person foaf:name ?name .
            FILTER(?name = "Alice")
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
    
    def test_query_with_newlines_in_string(self):
        """Test multi-line string literals."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice\nSmith"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1


class TestLargeResults:
    """Test handling of large result sets."""
    
    def test_large_result_set(self):
        """Test query returning many results."""
        graph = ProvenanceGraph()
        
        # Add 1000 people
        for i in range(1000):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.name,
                RDFLiteral(f"Person {i}"),
                source="user"
            )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?name WHERE {
            ?person foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1000
    
    def test_large_literal_values(self):
        """Test very long literal values."""
        graph = ProvenanceGraph()
        
        # Create a very long string
        long_text = "A" * 10000
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral(long_text),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            :Alice foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert len(str(results[0]["name"])) == 10000
    
    def test_many_variables(self):
        """Test query with many variables."""
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
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.mbox,
            RDFLiteral("alice@example.com"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?v1 ?v2 ?v3 ?v4 ?v5 ?v6 WHERE {
            :Alice foaf:name ?v1 .
            :Alice foaf:age ?v2 .
            :Alice foaf:mbox ?v3 .
            BIND(?v1 AS ?v4)
            BIND(?v2 AS ?v5)
            BIND(?v3 AS ?v6)
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert len(results[0]) == 6  # 6 variables


class TestNumericAndDataTypes:
    """Test different data types in SPARQL."""
    
    def test_integer_comparison(self):
        """Test integer comparisons in FILTER."""
        graph = ProvenanceGraph()
        
        for i in range(10):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.age,
                RDFLiteral(20 + i),
                source="user"
            )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
            FILTER(?age >= 25 && ?age <= 27)
        }
        """
        
        results = graph.query(query)
        assert len(results) == 3  # Ages 25, 26, 27
    
    def test_float_values(self):
        """Test floating point values."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Product,
            USER_NS.price,
            RDFLiteral(19.99),
            source="user"
        )
        
        query = """
        SELECT ?price WHERE {
            :Product :price ?price .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert float(results[0]["price"]) == 19.99
    
    def test_boolean_values(self):
        """Test boolean literals."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            USER_NS.isActive,
            RDFLiteral(True),
            source="user"
        )
        
        query = """
        SELECT ?active WHERE {
            :Alice :isActive ?active .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1


class TestComplexFilters:
    """Test complex FILTER expressions."""
    
    def test_filter_with_string_functions(self):
        """Test string functions in FILTER."""
        graph = ProvenanceGraph()
        
        names = ["Alice Smith", "Bob Jones", "Alice Johnson", "Charlie Smith"]
        for name in names:
            person_uri = USER_NS[name.replace(" ", "")]
            graph.add_triple_with_provenance(
                person_uri,
                FOAF.name,
                RDFLiteral(name),
                source="user"
            )
        
        # Find all names starting with "Alice"
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
            FILTER(STRSTARTS(?name, "Alice"))
        }
        """
        
        results = graph.query(query)
        assert len(results) == 2  # Alice Smith and Alice Johnson
    
    def test_filter_with_arithmetic(self):
        """Test arithmetic in FILTER."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.age,
            RDFLiteral(30),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?age ?doubled WHERE {
            :Alice foaf:age ?age .
            BIND(?age * 2 AS ?doubled)
            FILTER(?doubled > 50)
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert int(results[0]["doubled"]) == 60


class TestErrorRecovery:
    """Test error handling and recovery."""
    
    def test_invalid_uri_reference(self):
        """Test handling of invalid URI references."""
        graph = ProvenanceGraph()
        
        # Query with undefined prefix
        query = """
        SELECT ?s WHERE {
            ?s undefined:property ?o .
        }
        """
        
        with pytest.raises(Exception):
            graph.query(query)
    
    def test_malformed_filter(self):
        """Test malformed FILTER expression."""
        graph = ProvenanceGraph()
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
            FILTER(?age > )
        }
        """
        
        with pytest.raises(Exception):
            graph.query(query)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
