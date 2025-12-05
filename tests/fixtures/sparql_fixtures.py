"""
Reusable fixtures for SPARQL tests.

Provides pre-configured graphs and query templates for testing.
"""

import pytest
from rdflib import Namespace, Literal as RDFLiteral
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.vocabulary import FOAF, SCHEMA

USER_NS = Namespace("http://semanticmemory.org/user#")


@pytest.fixture
def empty_graph():
    """Empty ProvenanceGraph for testing."""
    return ProvenanceGraph()


@pytest.fixture
def small_graph():
    """Small graph with basic test data (10-20 triples)."""
    graph = ProvenanceGraph()
    
    # Add some basic entities
    graph.add_triple_with_provenance(
        USER_NS.Alice,
        FOAF.name,
        RDFLiteral("Alice"),
        source="user"
    )
    
    graph.add_triple_with_provenance(
        USER_NS.Bob,
        FOAF.name,
        RDFLiteral("Bob"),
        source="user"
    )
    
    graph.add_triple_with_provenance(
        USER_NS.Alice,
        FOAF.knows,
        USER_NS.Bob,
        source="user"
    )
    
    graph.add_triple_with_provenance(
        USER_NS.Alice,
        FOAF.age,
        RDFLiteral(30),
        source="user"
    )
    
    graph.add_triple_with_provenance(
        USER_NS.Bob,
        FOAF.age,
        RDFLiteral(25),
        source="user"
    )
    
    return graph


@pytest.fixture
def medium_graph():
    """Medium graph with test data (100-200 triples)."""
    graph = ProvenanceGraph()
    
    # Create a network of people
    people = [f"Person{i}" for i in range(20)]
    
    for person in people:
        person_uri = USER_NS[person]
        
        # Add name
        graph.add_triple_with_provenance(
            person_uri,
            FOAF.name,
            RDFLiteral(person),
            source="user"
        )
        
        # Add age (random-ish)
        age = 20 + (hash(person) % 50)
        graph.add_triple_with_provenance(
            person_uri,
            FOAF.age,
            RDFLiteral(age),
            source="user"
        )
        
        # Add email
        graph.add_triple_with_provenance(
            person_uri,
            FOAF.mbox,
            RDFLiteral(f"{person.lower()}@example.com"),
            source="user"
        )
    
    # Add some relationships
    for i in range(len(people) - 1):
        graph.add_triple_with_provenance(
            USER_NS[people[i]],
            FOAF.knows,
            USER_NS[people[i + 1]],
            source="user"
        )
    
    return graph


@pytest.fixture
def large_graph():
    """Large graph with test data (1000+ triples)."""
    graph = ProvenanceGraph()
    
    # Create a large network
    num_people = 200
    
    for i in range(num_people):
        person_uri = USER_NS[f"Person{i}"]
        
        # Add name
        graph.add_triple_with_provenance(
            person_uri,
            FOAF.name,
            RDFLiteral(f"Person {i}"),
            source="user"
        )
        
        # Add age
        age = 20 + (i % 60)
        graph.add_triple_with_provenance(
            person_uri,
            FOAF.age,
            RDFLiteral(age),
            source="user"
        )
        
        # Add email
        graph.add_triple_with_provenance(
            person_uri,
            FOAF.mbox,
            RDFLiteral(f"person{i}@example.com"),
            source="user"
        )
        
        # Add some knows relationships (creates a network)
        if i > 0:
            graph.add_triple_with_provenance(
                person_uri,
                FOAF.knows,
                USER_NS[f"Person{i-1}"],
                source="user"
            )
        
        if i % 10 == 0 and i > 10:
            graph.add_triple_with_provenance(
                person_uri,
                FOAF.knows,
                USER_NS[f"Person{i-10}"],
                source="user"
            )
    
    return graph


@pytest.fixture
def acmecorp_employees_graph():
    """Graph with AcmeCorp employees (Alice, Bob, Charlie, Dave)."""
    graph = ProvenanceGraph()
    
    employees = ["Alice", "Bob", "Charlie", "Dave"]
    
    for employee in employees:
        employee_uri = USER_NS[employee]
        
        # Add name
        graph.add_triple_with_provenance(
            employee_uri,
            FOAF.name,
            RDFLiteral(employee),
            source="user"
        )
        
        # Add worksFor relationship
        graph.add_triple_with_provenance(
            employee_uri,
            SCHEMA.worksFor,
            USER_NS.AcmeCorp,
            source="user"
        )
    
    # Add User knows Alice
    graph.add_triple_with_provenance(
        USER_NS.User,
        FOAF.knows,
        USER_NS.Alice,
        source="user"
    )
    
    return graph


# Query template collections
SELECT_QUERIES = {
    "simple_pattern": """
        SELECT ?s ?p ?o WHERE {
            ?s ?p ?o .
        }
    """,
    
    "with_filter": """
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
            FILTER(?age > 25)
        }
    """,
    
    "with_optional": """
        SELECT ?person ?name ?email WHERE {
            ?person foaf:name ?name .
            OPTIONAL { ?person foaf:mbox ?email }
        }
    """,
    
    "with_union": """
        SELECT ?person WHERE {
            { ?person foaf:knows :Alice }
            UNION
            { :Alice foaf:knows ?person }
        }
    """,
    
    "with_count": """
        SELECT (COUNT(?person) AS ?count) WHERE {
            ?person foaf:name ?name .
        }
    """,
    
    "with_group_by": """
        SELECT ?age (COUNT(?person) AS ?count) WHERE {
            ?person foaf:age ?age .
        }
        GROUP BY ?age
    """,
    
    "with_order_by": """
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
        }
        ORDER BY DESC(?age)
    """,
    
    "with_limit": """
        SELECT ?person ?name WHERE {
            ?person foaf:name ?name .
        }
        LIMIT 10
    """,
}

ASK_QUERIES = {
    "triple_exists": """
        ASK {
            :Alice foaf:knows :Bob
        }
    """,
    
    "with_filter": """
        ASK {
            ?person foaf:age ?age .
            FILTER(?age > 100)
        }
    """,
}

CONSTRUCT_QUERIES = {
    "simple": """
        CONSTRUCT {
            ?person a foaf:Person .
        }
        WHERE {
            ?person foaf:name ?name .
        }
    """,
    
    "transformation": """
        CONSTRUCT {
            ?person :hasEmail ?email .
        }
        WHERE {
            ?person foaf:mbox ?email .
        }
    """,
}


# Assertion helpers
def assert_query_result_count(results, expected_count):
    """Assert that query results have the expected count."""
    if isinstance(results, bool):
        raise ValueError("Cannot check count on ASK query (returns boolean)")
    
    if isinstance(results, list):
        actual_count = len(results)
    else:
        # Assume it's an iterable
        actual_count = len(list(results))
    
    assert actual_count == expected_count, \
        f"Expected {expected_count} results, got {actual_count}"


def assert_query_contains(results, key, value):
    """Assert that query results contain a specific key-value pair."""
    if isinstance(results, bool):
        raise ValueError("Cannot check contains on ASK query (returns boolean)")
    
    found = False
    for row in results:
        if isinstance(row, dict):
            if key in row and str(row[key]) == str(value):
                found = True
                break
    
    assert found, f"Expected to find {key}={value} in results"


def assert_query_performance(execution_time_ms, max_time_ms):
    """Assert that query executed within the expected time."""
    assert execution_time_ms <= max_time_ms, \
        f"Query took {execution_time_ms:.2f}ms, expected <= {max_time_ms}ms"


__all__ = [
    "empty_graph",
    "small_graph",
    "medium_graph",
    "large_graph",
    "acmecorp_employees_graph",
    "SELECT_QUERIES",
    "ASK_QUERIES",
    "CONSTRUCT_QUERIES",
    "assert_query_result_count",
    "assert_query_contains",
    "assert_query_performance",
]
