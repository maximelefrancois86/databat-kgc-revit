import sys
import os
from rdflib import Graph, RDF, Literal, BNode
from rdflib.term import Node
from app.namespaces import *
import shutil


def describe(graph:Graph, x:Node, g:Graph):
    if isinstance(x, Literal):
        return
    # the document
    if x.endswith("#"):
        doc = URIRef(str(x)[:-1])
        g.add((doc, RDF.type, SCHEMA.Dataset))
        g.add((doc, SCHEMA.about, x))
    # backward
    for s,p,o in graph.triples((None,None,x)):
        if p == RDF.type: # do not store all instances of a type
            continue
        if isinstance(s, BNode): # a bnode would be useless here
            continue
        g.add((s,p,o))
    # forward
    for s,p,o in graph.triples((x,None,None)):
        g.add((s,p,o))
        if isinstance(o, BNode):
            describe(graph, o, g)
        # if isinstance(o, URIRef):
        #     for triple in graph.triples((o,RDF.type,None)):
        #         g.add(triple)
                    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit(1)
    graph = Graph(namespace_manager=namespaceManager)
    input = sys.argv[1]
    base = sys.argv[2]

    graph.parse(input)
    
    hiddenLabels = Graph(namespace_manager=namespaceManager)
    for triple in graph.triples((None, SKOS.hiddenLabel, None)):
        hiddenLabels.add(triple)
    
    path = "public/emse/hidden.ttl"
    hiddenLabels.serialize(path, format="ttl", base=base)
    print("done")
