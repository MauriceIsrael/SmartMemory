#!/usr/bin/env python3
"""
CLI tool to list inferred facts from the knowledge graph.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.config import config


def main():
    """List all inferred facts with their provenance."""
    print("🧠 Inferred Facts\n")
    print("=" * 80)
    
    # Load the knowledge graph
    graph = ProvenanceGraph()
    persistence_path = Path(config.persistence_path)
    
    if not persistence_path.exists():
        print("\n✗ No knowledge graph found.")
        print(f"Expected at: {persistence_path}")
        return
    
    graph.load_from_file(persistence_path)
    
    # SPARQL query to find inferred facts
    query = """
    PREFIX sem: <http://example.org/semanticmemory/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX schema: <https://schema.org/>
    
    SELECT ?s ?p ?o ?source ?confidence ?rule
    WHERE {
        ?stmt a rdf:Statement ;
              rdf:subject ?s ;
              rdf:predicate ?p ;
              rdf:object ?o ;
              sem:source ?source ;
              sem:confidence ?confidence .
        
        # Filter for inferred facts (not user-provided)
        FILTER(CONTAINS(STR(?source), "inference") || CONTAINS(STR(?source), "rule"))
        
        OPTIONAL { ?stmt sem:sourceRule ?rule }
    }
    ORDER BY DESC(?confidence)
    """
    
    results = graph.query(query)
    
    if not results:
        print("\n✓ No inferred facts found.")
        print("\nInferred facts are created by inference rules when new information is added.")
        return
    
    print(f"\nFound {len(results)} inferred fact(s):\n")
    
    # Group by source rule
    by_rule = {}
    for row in results:
        rule = str(row.get('rule', 'unknown')) if 'rule' in row else 'unknown'
        if rule not in by_rule:
            by_rule[rule] = []
        by_rule[rule].append(row)
    
    for rule, facts in by_rule.items():
        print(f"\n📌 {rule} ({len(facts)} facts)")
        print("-" * 80)
        
        for fact in facts[:10]:  # Limit to 10 per rule
            s = str(fact['s']).replace(config.user_namespace, ":")
            p = str(fact['p'])
            p = p.replace("http://xmlns.com/foaf/0.1/", "foaf:")
            p = p.replace("https://schema.org/", "schema:")
            p = p.replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
            o = str(fact['o']).replace(config.user_namespace, ":")
            conf = float(fact['confidence'])
            
            print(f"  {s} {p} {o}")
            print(f"    Confidence: {conf:.2f}")
        
        if len(facts) > 10:
            print(f"  ... and {len(facts) - 10} more")
    
    print("\n" + "=" * 80)
    print(f"\nTotal inferred facts: {len(results)}")
    print(f"Rules that inferred: {len(by_rule)}")


if __name__ == "__main__":
    main()
