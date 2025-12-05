"""
CLI tool to load documents into SmartMemory.
"""

import asyncio
import argparse
import sys
from pathlib import Path

from smart_memory.config import config
from smart_memory.logging_config import get_logger
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.knowledge.persistence import get_persistence_backend
from smart_memory.inference.rule_engine import RuleEngine, load_rules
from smart_memory.tools.load_document import load_document

logger = get_logger(__name__)

async def main_async():
    parser = argparse.ArgumentParser(description="Load a document into SmartMemory")
    parser.add_argument("--file", help="Path to the file to load (PDF, TXT, MD)")
    parser.add_argument("--url", help="URL to load (not yet implemented)")
    parser.add_argument("--title", help="Title of the document")
    parser.add_argument("--store-content", action="store_true", help="Store full content in graph")
    parser.add_argument("--no-extract", action="store_true", help="Disable rule extraction")
    parser.add_argument("--batch", action="store_true", help="Treat file argument as glob pattern for batch loading")
    
    args = parser.parse_args()
    
    if not args.file and not args.url:
        parser.error("Must provide --file or --url")
        
    # Initialize components
    logger.info("Initializing SmartMemory...")
    graph = ProvenanceGraph()
    persistence = get_persistence_backend()
    
    # Load persistence
    try:
        persistence.load(graph)
        logger.info(f"Loaded {graph.get_triple_count()} triples")
    except Exception as e:
        logger.warning(f"Could not load persistence: {e}")
        
    # Load rules (needed for RuleEngine, even if just defaults)
    rules = load_rules([config.default_rules_dir, config.user_rules_dir])
    rule_engine = RuleEngine(rules)
    
    # Process files
    files_to_process = []
    if args.batch and args.file:
        import glob
        files_to_process = [Path(p) for p in glob.glob(args.file)]
    elif args.file:
        files_to_process = [Path(args.file)]
        
    if not files_to_process and args.file:
        print(f"No files found matching: {args.file}")
        sys.exit(1)
        
    print(f"\nProcessing {len(files_to_process)} document(s)...\n")
    
    for file_path in files_to_process:
        print(f"Loading: {file_path}")
        try:
            result = await load_document(
                {
                    "file_path": str(file_path),
                    "title": args.title,
                    "store_content": args.store_content,
                    "extract_rules": not args.no_extract
                },
                graph,
                rule_engine
            )
            
            for content in result:
                print(content.text)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    # Save persistence
    print("\nSaving knowledge graph...")
    try:
        persistence.save(graph)
        print("Done.")
    except Exception as e:
        print(f"Error saving persistence: {e}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
