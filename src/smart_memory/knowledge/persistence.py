from abc import ABC, abstractmethod
from pathlib import Path
from smart_memory.knowledge.graph import ProvenanceGraph
from rdflib_sqlalchemy.store import SQLAlchemy
from sqlalchemy import create_engine
from rdflib import Graph
from smart_memory.config import config
import rdflib_sqlalchemy # noqa: F401

class Persistence(ABC):
    @abstractmethod
    def save(self, graph: ProvenanceGraph):
        pass

    @abstractmethod
    def load(self, graph: ProvenanceGraph):
        pass

class TurtlePersistence(Persistence):
    def __init__(self, path: Path):
        self.path = path

    def save(self, graph: ProvenanceGraph):
        graph.save_to_file(self.path)

    def load(self, graph: ProvenanceGraph):
        graph.load_from_file(self.path)

class SQLitePersistence(Persistence):
    def __init__(self, path: Path):
        self.path = path
        self.engine = create_engine(f"sqlite:///{str(self.path.absolute())}")
        self.store = SQLAlchemy(engine=self.engine)

    def save(self, graph: ProvenanceGraph):
        # With SQLAlchemy, the graph is saved automatically
        pass

    def load(self, graph: ProvenanceGraph):
        graph.graph = Graph(store=self.store, identifier=graph.graph.identifier)
        graph.graph.open(str(self.path), create=True)

def get_persistence_backend() -> Persistence:
    if config.persistence_backend == "turtle":
        return TurtlePersistence(config.persistence_path)
    elif config.persistence_backend == "sqlite":
        return SQLitePersistence(config.persistence_path)
    else:
        raise ValueError(f"Unknown persistence backend: {config.persistence_backend}")
