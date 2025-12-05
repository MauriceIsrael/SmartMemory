#!/usr/bin/env python3
"""
SmartMemory Quick Demo
======================

Demonstrates the core capabilities:
1. Adding facts to the knowledge graph
2. Querying with SPARQL
3. Provenance tracking
"""

from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.inference.rule_engine import RuleEngine, load_rules
from rdflib import URIRef, Namespace
import os

# Define namespaces
USER = Namespace("http://semanticmemory.org/user#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("https://schema.org/")


def main():
    print("🧠 SmartMemory v0.1 - Quick Demo\n")
    
    # Initialize knowledge graph
    graph = ProvenanceGraph()
    
    # Load default rules
    # Assuming running from project root
    from pathlib import Path
    rules_dir = Path("src/rules/defaults")
    if not rules_dir.exists():
        # Fallback if running from examples/
        rules_dir = Path("../src/rules/defaults")
        
    rules = load_rules([rules_dir])
    rule_engine = RuleEngine(rules)
    print(f"✓ Knowledge graph initialized with {len(rules)} default rules\n")
    
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
    
    # Step 3: Conversational Rule Learning
    print("\nStep 3: Conversational Rule Learning (The 'Magic' Part)")
    print("-" * 50)
    print("Scenario: User teaches the system a new business rule.")
    
    # 1. User Statement
    print("\n1. User says: 'Driving a car requires a license'")
    print("   LLM analyzes this and proposes a SPARQL rule...")
    
    # 2. Rule Proposal (Simulated)
    rule_id = "driving_requires_license"
    sparql_rule = """
    PREFIX : <http://semanticmemory.org/user#>
    CONSTRUCT { ?person :requires :DrivingLicense }
    WHERE { ?person :usesTransportOption :Car }
    """
    print(f"   → Proposed Rule '{rule_id}':")
    print(f"     IF ?person uses :Car THEN ?person requires :DrivingLicense")
    
    # 3. User Approval
    print("\n2. User approves the rule via approve_rule('driving_requires_license')")
    from smart_memory.inference.rule_engine import InferenceRule
    from pathlib import Path
    
    new_rule = InferenceRule(
        id=rule_id,
        file_path=Path(f"user_rules/{rule_id}.rq"),
        sparql_query=sparql_rule,
        source="user",
        description="Infers license requirement from car usage"
    )
    rule_engine.rules.append(new_rule)
    print("   ✓ Rule activated and added to engine")
    
    # 4. New Fact triggers Rule
    print("\n3. User says: 'Charlie drives to work'")
    graph.add_triple_with_provenance(
        subject=USER.Charlie,
        predicate=USER.usesTransportOption,
        obj=USER.Car,
        source="user",
        confidence=1.0
    )
    print("   ✓ Added fact: Charlie uses Car")
    
    # 5. Automatic Inference
    print("\n4. System automatically infers consequences...")
    # Use execute_rules instead of run_all_rules
    count = rule_engine.execute_rules(graph)
    print(f"   ✓ Inference engine finished (inferred {count} new triples)")
    
    # Check if inference happened
    # We need to query the graph to see the new triple
    check_query = """
    PREFIX : <http://semanticmemory.org/user#>
    ASK { :Charlie :requires :DrivingLicense }
    """
    is_inferred = graph.query(check_query)
    
    if is_inferred:
        print("   ✨ INFERENCE CONFIRMED: Charlie requires DrivingLicense")
    else:
        print("   (No new inferences found in this pass - rule might need re-run)")

    print("\nNext steps:")
    print("  • See docs/getting-started.md for MCP setup")
    print("  • Try with Claude Desktop or Gemini")
    print("  • Create custom rules in user_rules/")


if __name__ == "__main__":
    main()
