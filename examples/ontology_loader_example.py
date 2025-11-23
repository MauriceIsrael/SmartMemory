"""
Example usage of the OntologyLoader.

This script demonstrates loading ontologies with intelligent caching.
"""

import logging
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS

from src.ontology import OntologyLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main example function."""
    logger.info("=== Ontology Loader Example ===")
    
    # Create an RDF graph
    graph = Graph()
    
    # Initialize the loader
    loader = OntologyLoader(
        graph=graph,
        cache_dir=Path("./cache"),
        offline_mode=False  # Set to True to skip remote validation
    )
    
    # Load all ontologies
    logger.info("\n--- Loading ontologies ---")
    results = loader.load_all()
    
    # Print results
    logger.info("\n--- Load Results ---")
    for name, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"{status} {name}: {'Success' if success else 'Failed'}")
    
    # Show cache status
    logger.info("\n--- Cache Status ---")
    cache_status = loader.get_cache_status()
    for name, status in cache_status.items():
        if status['cached']:
            logger.info(f"{name}:")
            logger.info(f"  Path: {status['local_path']}")
            logger.info(f"  Downloaded: {status['downloaded_at']}")
            logger.info(f"  ETag: {status.get('etag', 'N/A')}")
        else:
            logger.info(f"{name}: Not cached")
    
    # Query the graph for ontology terms
    logger.info("\n--- Querying Loaded Ontologies ---")
    
    # Define namespaces
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    
    # Check if FOAF Person class is loaded
    if (FOAF.Person, RDF.type, RDFS.Class) in graph:
        logger.info("✓ Found foaf:Person class")
    else:
        logger.info("✗ foaf:Person not found")
    
    # Check if SKOS Concept class is loaded
    if (SKOS.Concept, RDF.type, RDFS.Class) in graph or \
       (SKOS.Concept, RDF.type, None) in graph:
        logger.info("✓ Found skos:Concept class")
    else:
        logger.info("✗ skos:Concept not found")
    
    # Print graph statistics
    logger.info("\n--- Graph Statistics ---")
    logger.info(f"Total triples: {len(graph)}")
    logger.info(f"Loaded ontologies: {loader.get_loaded_ontologies()}")
    
    # Example: Refresh a specific ontology
    logger.info("\n--- Refresh Example ---")
    logger.info("To refresh FOAF ontology:")
    logger.info("  loader.refresh_ontology('foaf')")


if __name__ == "__main__":
    main()
