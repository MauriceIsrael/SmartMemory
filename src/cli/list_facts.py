"""CLI tool to list recent facts from the knowledge graph."""

import argparse
from pathlib import Path
from rdflib import Graph


def main():
    """List the most recent facts from the knowledge graph."""
    parser = argparse.ArgumentParser(
        description='List recent facts from the knowledge graph.'
    )
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=5,
        help='Number of recent facts to display (default: 5)'
    )
    parser.add_argument(
        '--graph-file',
        type=str,
        default='knowledge_graph.ttl',
        help='Path to the knowledge graph file (default: knowledge_graph.ttl)'
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
    
    # Display total count
    total = len(triples)
    display_count = min(args.count, total)
    
    print(f"📊 Knowledge Graph Statistics")
    print(f"   Total facts: {total}")
    print(f"   Showing: {display_count} most recent\n")
    
    # Display recent facts (last N triples)
    # Note: RDF doesn't have inherent ordering, so we show the "last" ones
    # based on how they're stored in the file
    recent_triples = triples[-display_count:]
    
    print(f"Recent Facts:\n")
    for i, (subject, predicate, obj) in enumerate(recent_triples, 1):
        # Format the triple nicely
        s = _format_term(subject)
        p = _format_term(predicate)
        o = _format_term(obj)
        
        print(f"[{i}] {s} {p} {o}")
    
    if total > display_count:
        print(f"\n... and {total - display_count} more fact(s)")
        print(f"Use --count {total} to see all facts")


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
