import pyoxigraph
from rdflib import URIRef

iri = "http://example.org/test"
nn = pyoxigraph.NamedNode(iri)
print(f"IRI: {iri}")
print(f"NamedNode str: {str(nn)}")
print(f"NamedNode value: {nn.value}")

from rdflib import Literal as RDFLiteral
lit = RDFLiteral("test", lang="en")
oxl = pyoxigraph.Literal(str(lit), language=lit.language)
print(f"Literal str: {str(oxl)}")
print(f"Literal value: {oxl.value}")
print(f"Literal language: {oxl.language}")
