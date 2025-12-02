#!/usr/bin/env python3
"""
SmartMemory Quick Demo
======================

Demonstrates the core capabilities:
1. Adding facts to the knowledge graph
2. Querying with SPARQL
3. Provenance tracking
"""

from semantic_memory.knowledge.graph import ProvenanceGraph
from rdflib import URIRef, Namespace

# Define namespaces
USER = Namespace("http://semanticmemory.org/user#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("https://schema.org/")


def main():
    print("🧠 SmartMemory v0.1 - Quick Demo\n")
    
    # Initialize knowledge graph
    graph = ProvenanceGraph()
    print("✓ Knowledge graph initialized\n")
    
    # Step 1: Add facts with provenance
    print("Step 1: Adding facts")
    print("-" * 50)
    
    # Alice knows Bob
    graph.add_triple_with_provenance(
        subject=USER.Alice,
        predicate=FOAF.knows,
        obj=USER.Bob,
        source="user",
        confidence=1.0,
    )
    print("  ✓ Alice knows Bob")
    
    # Alice works at Google
    graph.add_triple_with_provenance(
        subject=USER.Alice,
        predicate=SCHEMA.worksFor,
        obj=USER.Google,
        source="user",
        confidence=1.0,
    )
    print("  ✓ Alice works at Google")
    
    # Bob works at Google
    graph.add_triple_with_provenance(
        subject=USER.Bob,
        predicate=SCHEMA.worksFor,
        obj=USER.Google,
        source="user",
        confidence=1.0,
    )
    print("  ✓ Bob works at Google")
    
    print(f"\nTriples in graph: {len(graph)}\n")
    
    # Step 2: Query the graph
    print("Step 2: Querying the graph")
    print("-" * 50)
    
    # Query: Who works at Google?
    query1 = """
    PREFIX : <http://semanticmemory.org/user#>
    PREFIX schema: <https://schema.org/>
    
    SELECT ?person
    WHERE {
        ?person schema:worksFor :Google .
    }
    """
    
    results = graph.query(query1)
    print("Query: Who works at Google?")
    for row in results:
        person = str(row['person']).replace('http://semanticmemory.org/user#', ':')
        print(f"  ✓ {person}")
    
    # Query: Who does Alice know?
    query2 = """
    PREFIX : <http://semanticmemory.org/user#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?friend
    WHERE {
        :Alice foaf:knows ?friend .
    }
    """
    
    results = graph.query(query2)
    print("\nQuery: Who does Alice know?")
    for row in results:
        friend = str(row['friend']).replace('http://semanticmemory.org/user#', ':')
        print(f"  ✓ {friend}")
    
    print(f"\n✨ Demo complete!")
    print("\nWhat SmartMemory adds:")
    print("  ✓ Provenance tracking (who added, when, confidence)")
    print("  ✓ SPARQL inference rules (automatic deductions)")
    print("  ✓ Human-in-the-loop (approve/reject uncertain facts)")
    print("  ✓ MCP integration (use with Claude, Gemini, etc.)")
    print("\nNext steps:")
    print("  • See docs/getting-started.md for MCP setup")
    print("  • Try with Claude Desktop or Gemini")
    print("  • Create custom rules in user_rules/")


if __name__ == "__main__":
    main()
