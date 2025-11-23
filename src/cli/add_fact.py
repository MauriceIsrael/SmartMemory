import argparse
from src.models.knowledge_graph import KnowledgeGraph
from src.models.triple import Triple
from src.services.persistence_service import PersistenceService
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='Add a fact to the knowledge graph.')
    parser.add_argument('subject', type=str, help='The subject of the fact.')
    parser.add_argument('predicate', type=str, help='The predicate of the fact.')
    parser.add_argument('object', type=str, help='The object of the fact.')
    args = parser.parse_args()

    try:
        logging.info("Adding fact...")
        persistence_service = PersistenceService('knowledge_graph.ttl')
        knowledge_graph = persistence_service.load()

        triple = Triple(subject=args.subject, predicate=args.predicate, object=args.object)
        knowledge_graph.add_explicit(triple)

        persistence_service.save(knowledge_graph)
        logging.info(f"Fact added: {triple}")
    except Exception as e:
        logging.error(f"Failed to add fact: {e}")
        sys.exit(1) # Exit with an error code

if __name__ == '__main__':
    import sys
    main()
