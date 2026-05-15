from smart_memory.nlp import TripleExtractor
te = TripleExtractor()
triples = te.extract("Alice works at TechCorp and knows Bob")
for t in triples:
    print(f"{t.subject} {t.predicate} {t.object}")
