from src.models.knowledge_graph import KnowledgeGraph
import logging

class PersistenceService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        logging.info(f"PersistenceService initialized with file path: {file_path}")

    def save(self, knowledge_graph: KnowledgeGraph):
        try:
            logging.info(f"Saving knowledge graph to {self.file_path}")
            knowledge_graph.explicit_graph.serialize(destination=self.file_path, format='turtle')
            logging.info("Knowledge graph saved successfully.")
        except Exception as e:
            logging.error(f"Error saving knowledge graph: {e}")
            raise

    def load(self) -> KnowledgeGraph:
        logging.info(f"Loading knowledge graph from {self.file_path}")
        knowledge_graph = KnowledgeGraph()
        try:
            knowledge_graph.explicit_graph.parse(self.file_path, format='turtle')
            logging.info("Knowledge graph loaded successfully.")
        except FileNotFoundError:
            logging.warning(f"Knowledge graph file not found at {self.file_path}. Returning an empty graph.")
        except Exception as e:
            logging.error(f"Error loading knowledge graph: {e}")
            raise
        return knowledge_graph
