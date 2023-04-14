import sys
import os
from rdflib import Graph, RDF, Literal, BNode
from rdflib.term import Node
from app.namespaces import *
import shutil


def describe(graph:Graph, x:Node, g:Graph):
    if isinstance(x, Literal):
        return
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
        if isinstance(o, URIRef):
            for triple in graph.triples((o,RDF.type,None)):
                g.add(triple)
                    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit(1)
    graph = Graph(namespace_manager=namespaceManager)
    input = sys.argv[1]
    base = sys.argv[2]

    graph.parse(input)
        
    named_graphs={}
    for triple in graph:
        for t in triple:
            if isinstance(t, URIRef) and t.startswith(base):
                
                key = str(t).split('#')[0]
                try:
                    named_graphs[key].add(t)
                except:
                    named_graphs[key] = set()
                    named_graphs[key].add(t)
    
    for t in sorted(named_graphs.keys()):
        print(t)
        g = Graph(namespace_manager=graph.namespace_manager)
        for x in named_graphs[t]:
            describe(graph, x, g)
        path = "public/" + t[len(base):] + ".ttl"
        os.makedirs(path[:path.rfind("/")], exist_ok = True)
        g.serialize(path, format="ttl", base=base)
    print("done")

    for root, dirs, files in os.walk("public"):
        for dir in dirs:
            if f"{dir}.ttl" in files:
                shutil.copy(f"{root}/{dir}.ttl",f"{root}/{dir}/index.ttl")