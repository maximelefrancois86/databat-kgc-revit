from rdflib import Graph
from app.namespaces import *
g = Graph()
g.parse("temp/5_properties.ttl")

coswotOntology = set()
for triple in g:
    for term in triple:
        if str(term).startswith(COSWOT._NS):
            coswotOntology.add(term)

import pprint 
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(sorted(list(coswotOntology)))

    