"""CLI tool to show statistics about the knowledge graph."""

import argparse
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from collections import defaultdict


def main():
    """Display statistics about the knowledge graph."""
    parser = argparse.ArgumentParser(
        description='Show statistics about the knowledge graph.'
    )
    parser.add_argument(
        '--graph-file',
        type=str,
        default='knowledge_graph.ttl',
        help='Path to the knowledge graph file (default: knowledge_graph.ttl)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed statistics including predicate breakdown'
    )
    
    args = parser.parse_args()
    
    graph_path = Path(args.graph_file)
    
    if not graph_path.exists():
        print(f"✗ Knowledge graph file not found: {graph_path}")
        print("No facts have been added yet.")
        return
    
    # Load the graph
    graph = Graph()
    try:
        graph.parse(str(graph_path), format='turtle')
    except Exception as e:
        print(f"✗ Failed to load knowledge graph: {e}")
        return
    
    # Get all triples
    triples = list(graph)
    
    if not triples:
        print("✓ Knowledge graph is empty.")
        print("No facts have been added yet.")
        return
    
    # Collect statistics
    total_triples = len(triples)
    subjects = set()
    predicates = set()
    objects = set()
    predicate_counts = defaultdict(int)
    
    uri_count = 0
    literal_count = 0
    blank_node_count = 0
    
    for s, p, o in triples:
        subjects.add(s)
        predicates.add(p)
        objects.add(o)
        predicate_counts[p] += 1
        
        # Count types
        for term in [s, p, o]:
            if isinstance(term, URIRef):
                uri_count += 1
            elif isinstance(term, Literal):
                literal_count += 1
            elif isinstance(term, BNode):
                blank_node_count += 1
    
    # Calculate unique entities
    unique_subjects = len(subjects)
    unique_predicates = len(predicates)
    unique_objects = len(objects)
    unique_entities = len(subjects | objects)
    
    # Display statistics
    print("📊 Knowledge Graph Statistics\n")
    print(f"{'=' * 50}")
    print(f"  Total Facts (Triples):     {total_triples}")
    print(f"{'=' * 50}")
    print(f"  Unique Subjects:           {unique_subjects}")
    print(f"  Unique Predicates:         {unique_predicates}")
    print(f"  Unique Objects:            {unique_objects}")
    print(f"  Unique Entities (S∪O):     {unique_entities}")
    print(f"{'=' * 50}")
    print(f"  URI References:            {uri_count}")
    print(f"  Literals:                  {literal_count}")
    print(f"  Blank Nodes:               {blank_node_count}")
    print(f"{'=' * 50}")
    
    # Verbose mode: show predicate breakdown
    if args.verbose:
        print("\n📋 Predicate Breakdown:\n")
        sorted_predicates = sorted(
            predicate_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (pred, count) in enumerate(sorted_predicates, 1):
            pred_str = _format_term(pred)
            percentage = (count / total_triples) * 100
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = '█' * bar_length
            
            print(f"  [{i}] {pred_str}")
            print(f"      Count: {count} ({percentage:.1f}%)")
            print(f"      {bar}")
            print()
    
    # Additional tips
    if not args.verbose and unique_predicates > 5:
        print("\n💡 Use --verbose to see detailed predicate breakdown")


def _format_term(term):
    """Format an RDF term for display."""
    term_str = str(term)
    
    # Shorten common namespaces
    replacements = {
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf:',
        'http://www.w3.org/2000/01/rdf-schema#': 'rdfs:',
        'http://xmlns.com/foaf/0.1/': 'foaf:',
        'http://www.w3.org/2004/02/skos/core#': 'skos:',
        'http://schema.org/': 'schema:',
    }
    
    for full_ns, short_ns in replacements.items():
        if term_str.startswith(full_ns):
            return term_str.replace(full_ns, short_ns)
    
    return term_str


if __name__ == '__main__':
    main()
