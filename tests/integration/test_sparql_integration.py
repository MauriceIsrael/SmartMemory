"""
Integration tests for SPARQL queries.

Tests comprehensive SPARQL functionality including advanced features.
"""

import pytest
from rdflib import Namespace, Literal as RDFLiteral
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.vocabulary import FOAF, SCHEMA

USER_NS = Namespace("http://semanticmemory.org/user#")


class TestSelectQueries:
    """Test SELECT query variations."""
    
    def test_select_with_aggregates_count(self):
        """Test COUNT aggregate function."""
        graph = ProvenanceGraph()
        
        for i in range(5):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.name,
                RDFLiteral(f"Person {i}"),
                source="user"
            )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT (COUNT(?person) AS ?count) WHERE {
            ?person foaf:name ?name .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert int(results[0]["count"]) == 5
    
    def test_select_with_group_by(self):
        """Test GROUP BY clause."""
        graph = ProvenanceGraph()
        
        # Add people with different ages
        ages = [25, 30, 25, 30, 35]
        for i, age in enumerate(ages):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.age,
                RDFLiteral(age),
                source="user"
            )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?age (COUNT(?person) AS ?count) WHERE {
            ?person foaf:age ?age .
        }
        GROUP BY ?age
        ORDER BY ?age
        """
        
        results = graph.query(query)
        assert len(results) == 3  # 3 distinct ages
        
        # Check counts
        age_counts = {int(r["age"]): int(r["count"]) for r in results}
        assert age_counts[25] == 2
        assert age_counts[30] == 2
        assert age_counts[35] == 1
    
    def test_select_with_order_by(self):
        """Test ORDER BY clause."""
        graph = ProvenanceGraph()
        
        ages = [30, 25, 35, 20, 40]
        for i, age in enumerate(ages):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.age,
                RDFLiteral(age),
                source="user"
            )
        
        # Ascending order
        query_asc = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
        }
        ORDER BY ASC(?age)
        """
        
        results = graph.query(query_asc)
        ages_result = [int(r["age"]) for r in results]
        assert ages_result == [20, 25, 30, 35, 40]
        
        # Descending order
        query_desc = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
        }
        ORDER BY DESC(?age)
        """
        
        results = graph.query(query_desc)
        ages_result = [int(r["age"]) for r in results]
        assert ages_result == [40, 35, 30, 25, 20]
    
    def test_select_with_limit_offset(self):
        """Test LIMIT and OFFSET for pagination."""
        graph = ProvenanceGraph()
        
        for i in range(10):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.name,
                RDFLiteral(f"Person {i}"),
                source="user"
            )
        
        # First page (LIMIT 3)
        query_page1 = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
        }
        ORDER BY ?name
        LIMIT 3
        """
        
        results = graph.query(query_page1)
        assert len(results) == 3
        
        # Second page (LIMIT 3 OFFSET 3)
        query_page2 = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
        }
        ORDER BY ?name
        LIMIT 3 OFFSET 3
        """
        
        results = graph.query(query_page2)
        assert len(results) == 3
    
    def test_select_with_bind(self):
        """Test BIND to create computed variables."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.age,
            RDFLiteral(30),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?age ?ageInMonths WHERE {
            ?person foaf:age ?age .
            BIND(?age * 12 AS ?ageInMonths)
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert int(results[0]["age"]) == 30
        assert int(results[0]["ageInMonths"]) == 360
    
    def test_select_distinct(self):
        """Test SELECT DISTINCT to eliminate duplicates."""
        graph = ProvenanceGraph()
        
        # Multiple people with same age
        for i in range(5):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.age,
                RDFLiteral(30),  # All same age
                source="user"
            )
        
        # Without DISTINCT
        query_all = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?age WHERE {
            ?person foaf:age ?age .
        }
        """
        
        results = graph.query(query_all)
        assert len(results) == 5
        
        # With DISTINCT
        query_distinct = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?age WHERE {
            ?person foaf:age ?age .
        }
        """
        
        results = graph.query(query_distinct)
        assert len(results) == 1
        assert int(results[0]["age"]) == 30
    
    def test_select_with_union(self):
        """Test UNION to combine patterns."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.knows,
            USER_NS.Bob,
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Charlie,
            FOAF.knows,
            USER_NS.Alice,
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person WHERE {
            { :Alice foaf:knows ?person }
            UNION
            { ?person foaf:knows :Alice }
        }
        """
        
        results = graph.query(query)
        assert len(results) == 2  # Bob and Charlie


class TestPropertyPaths:
    """Test SPARQL property paths."""
    
    def test_property_path_sequence(self):
        """Test sequential property paths (/)."""
        graph = ProvenanceGraph()
        
        # Alice knows Bob, Bob has name
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.knows,
            USER_NS.Bob,
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Bob,
            FOAF.name,
            RDFLiteral("Bob"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?friendName WHERE {
            :Alice foaf:knows/foaf:name ?friendName .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert str(results[0]["friendName"]) == "Bob"
    
    def test_property_path_alternative(self):
        """Test alternative property paths (|)."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.knows,
            USER_NS.Bob,
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            SCHEMA.colleague,
            USER_NS.Charlie,
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX schema: <https://schema.org/>
        SELECT ?person WHERE {
            :Alice foaf:knows|schema:colleague ?person .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 2  # Bob and Charlie
    
    def test_property_path_zero_or_more(self):
        """Test zero-or-more property paths (*)."""
        graph = ProvenanceGraph()
        
        # Chain: Alice -> Bob -> Charlie
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.knows,
            USER_NS.Bob,
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Bob,
            FOAF.knows,
            USER_NS.Charlie,
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person WHERE {
            :Alice foaf:knows* ?person .
        }
        """
        
        results = graph.query(query)
        # Should include Alice (zero hops), Bob (one hop), Charlie (two hops)
        assert len(results) >= 2  # At least Bob and Charlie
    
    def test_property_path_inverse(self):
        """Test inverse property paths (^)."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            SCHEMA.worksFor,
            USER_NS.Thales,
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Bob,
            SCHEMA.worksFor,
            USER_NS.Thales,
            source="user"
        )
        
        query = """
        PREFIX schema: <https://schema.org/>
        SELECT ?employee WHERE {
            ?employee ^schema:worksFor :Thales .
        }
        """
        
        # Note: This is equivalent to: :Thales schema:worksFor ?employee
        # But we want the inverse, so let's use a different query
        query = """
        PREFIX schema: <https://schema.org/>
        SELECT ?company WHERE {
            :Alice ^schema:worksFor ?company .
        }
        """
        
        # Actually, let's test the correct inverse pattern
        query = """
        PREFIX schema: <https://schema.org/>
        SELECT ?employee WHERE {
            :Thales ^schema:worksFor ?employee .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 2  # Alice and Bob


class TestComplexPatterns:
    """Test complex SPARQL patterns."""
    
    def test_nested_optional(self):
        """Test nested OPTIONAL clauses."""
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
        SELECT ?name ?age ?email WHERE {
            ?person foaf:name ?name .
            OPTIONAL {
                ?person foaf:age ?age .
                OPTIONAL {
                    ?person foaf:mbox ?email .
                }
            }
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert str(results[0]["name"]) == "Alice"
        assert int(results[0]["age"]) == 30
        assert results[0].get("email") is None
    
    def test_filter_with_regex(self):
        """Test FILTER with regex."""
        graph = ProvenanceGraph()
        
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            FOAF.name,
            RDFLiteral("Alice Smith"),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Bob,
            FOAF.name,
            RDFLiteral("Bob Jones"),
            source="user"
        )
        
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name WHERE {
            ?person foaf:name ?name .
            FILTER(REGEX(?name, "Smith"))
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1
        assert "Smith" in str(results[0]["name"])
    
    def test_filter_with_multiple_conditions(self):
        """Test FILTER with AND/OR conditions."""
        graph = ProvenanceGraph()
        
        people = [
            ("Alice", 25),
            ("Bob", 30),
            ("Charlie", 35),
            ("Diana", 28),
        ]
        
        for name, age in people:
            person_uri = USER_NS[name]
            graph.add_triple_with_provenance(
                person_uri,
                FOAF.name,
                RDFLiteral(name),
                source="user"
            )
            graph.add_triple_with_provenance(
                person_uri,
                FOAF.age,
                RDFLiteral(age),
                source="user"
            )
        
        # Age between 26 and 32
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?age WHERE {
            ?person foaf:name ?name .
            ?person foaf:age ?age .
            FILTER(?age > 25 && ?age < 33)
        }
        """
        
        results = graph.query(query)
        assert len(results) == 2  # Bob (30) and Diana (28)
        ages = [int(r["age"]) for r in results]
        assert 30 in ages
        assert 28 in ages


class TestSubqueries:
    """Test SPARQL subqueries."""
    
    def test_subquery_in_select(self):
        """Test subquery in SELECT."""
        graph = ProvenanceGraph()
        
        # Add people with ages
        for i in range(5):
            graph.add_triple_with_provenance(
                USER_NS[f"Person{i}"],
                FOAF.age,
                RDFLiteral(20 + i * 5),
                source="user"
            )
        
        # Find people older than average age
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
            {
                SELECT (AVG(?a) AS ?avgAge) WHERE {
                    ?p foaf:age ?a .
                }
            }
            FILTER(?age > ?avgAge)
        }
        """
        
        results = graph.query(query)
        # Average is 30, so should get people with age > 30
        assert len(results) >= 2


class TestThalesEmployees:
    """Test queries on Thales employees scenario."""
    
    def test_find_all_employees(self):
        """Test finding all employees of a company."""
        graph = ProvenanceGraph()
        
        employees = ["Gilles", "Jérémie", "Coralie", "Daniel"]
        for emp in employees:
            graph.add_triple_with_provenance(
                USER_NS[emp],
                SCHEMA.worksFor,
                USER_NS.Thales,
                source="user"
            )
        
        query = """
        PREFIX schema: <https://schema.org/>
        SELECT ?employee WHERE {
            ?employee schema:worksFor :Thales .
        }
        """
        
        results = graph.query(query)
        assert len(results) == 4
    
    def test_find_colleagues(self):
        """Test finding colleagues (people working at same company)."""
        graph = ProvenanceGraph()
        
        # Daniel and Gilles work at Thales
        graph.add_triple_with_provenance(
            USER_NS.Daniel,
            SCHEMA.worksFor,
            USER_NS.Thales,
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS.Gilles,
            SCHEMA.worksFor,
            USER_NS.Thales,
            source="user"
        )
        
        # Alice works at Google
        graph.add_triple_with_provenance(
            USER_NS.Alice,
            SCHEMA.worksFor,
            USER_NS.Google,
            source="user"
        )
        
        # Find Daniel's colleagues (same company, but not Daniel)
        query = """
        PREFIX schema: <https://schema.org/>
        SELECT ?colleague WHERE {
            :Daniel schema:worksFor ?company .
            ?colleague schema:worksFor ?company .
            FILTER(?colleague != :Daniel)
        }
        """
        
        results = graph.query(query)
        assert len(results) == 1  # Only Gilles
        assert str(results[0]["colleague"]) == str(USER_NS.Gilles)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
