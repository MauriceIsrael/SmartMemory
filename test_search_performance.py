#!/usr/bin/env python3
"""
Test script to measure search_entity performance before/after optimization.
"""

import asyncio
import time
from pathlib import Path
from rdflib import Graph

# Import the optimized search_entity
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from semantic_memory.tools.search_entity import search_entity


async def test_search_performance():
    """Test search performance with the current graph."""
    print("🔍 Testing search_entity performance...\n")
    
    # Load the knowledge graph
    graph_path = Path("knowledge_graph.ttl")
    if not graph_path.exists():
        print("❌ knowledge_graph.ttl not found")
        return
    
    print(f"📂 Loading graph from {graph_path}...")
    g = Graph()
    load_start = time.time()
    g.parse(str(graph_path), format='turtle')
    load_time = time.time() - load_start
    
    triple_count = len(list(g))
    print(f"✅ Loaded {triple_count:,} triples in {load_time:.2f}s\n")
    
    # Test cases
    test_cases = [
        {"search_term": "user", "limit": 10},
        {"search_term": "person", "limit": 5},
        {"search_term": "test", "limit": 10},
    ]
    
    print("=" * 60)
    for i, test_args in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: search_term='{test_args['search_term']}', limit={test_args.get('limit', 10)}")
        print("-" * 60)
        
        start = time.time()
        result = await search_entity(test_args, g)
        elapsed = time.time() - start
        
        # Extract result text
        result_text = result[0].text if result else "No results"
        result_lines = result_text.split('\n')
        
        # Print first few lines
        print(f"⏱️  Execution time: {elapsed:.3f}s")
        print(f"📊 Result preview (first 5 lines):")
        for line in result_lines[:5]:
            print(f"   {line}")
        
        if len(result_lines) > 5:
            print(f"   ... ({len(result_lines) - 5} more lines)")
        
        print()
    
    print("=" * 60)
    print("\n✅ Performance test completed!")
    print("\n💡 Check /tmp/smartmemory.log for detailed timing logs")


if __name__ == "__main__":
    asyncio.run(test_search_performance())
