from rdflib import Graph, URIRef, Literal
from src.models.triple import Triple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.inference_engine import InferenceEngine

class KnowledgeGraph:
    def __init__(self, inference_engine: 'InferenceEngine' = None):
        self.explicit_graph = Graph()
        self.inferred_graph = Graph()
        self.inference_engine = inference_engine

    def _to_node(self, value: str):
        if value.startswith('http://') or value.startswith('https://') or value.startswith(':'):
            return URIRef(value)
        return Literal(value)

    def add_explicit(self, triple: Triple):
        s = URIRef(triple.subject)
        p = URIRef(triple.predicate)
        o = self._to_node(triple.object)
        self.explicit_graph.add((s, p, o))

        if self.inference_engine:
            inferred_triples = self.inference_engine.infer(self)
            for inferred_triple in inferred_triples:
                self.add_inferred(inferred_triple)

    def add_inferred(self, triple: Triple):
        s = URIRef(triple.subject)
        p = URIRef(triple.predicate)
        o = self._to_node(triple.object)
        self.inferred_graph.add((s, p, o))
