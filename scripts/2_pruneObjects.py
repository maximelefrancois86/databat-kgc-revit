import sys
from rdflib import Graph, RDF
from app.namespaces import *
from app.utils import camel_case
from typing import List

"""prune objects of undesired types, and explicit their class."""

def prune_objects(graph, to_prune:List, base):
    new_graph = Graph(namespace_manager=graph.namespace_manager)
    classes = set()
    one_per_class = dict()
    for s,p,o in graph:
        new_s, new_p, new_o = s, p, o
        if isinstance(s, URIRef) and str(s).startswith(base):
            stype = str(s)[len(base):str(s).rfind("_")]
            if stype in to_prune:
                continue
            clazz = URIRef(COSWOT._NS + camel_case(stype))
            classes.add(clazz)
            # if clazz in one_per_class and one_per_class[clazz] != s:
            #     continue
            # one_per_class[clazz] = s
            new_graph.add((new_s, RDF.type, clazz))
        if isinstance(o, URIRef) and str(o).startswith(base):
            otype = str(o)[len(base):str(o).rfind("_")]
            if otype in to_prune:
                continue
        new_graph.add((new_s, new_p, new_o))
    print(classes)
    return new_graph

if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    base = sys.argv[3]
    graph = Graph(namespace_manager=namespaceManager)
    print("parsing " + input)
    graph.parse(input, format="ttl")
    to_prune_classes = [
        "airterminal",
        "beam",
        "cablecarrierfitting",
        "cablecarriersegment",
        "column",
        "covering",
        "curtainwall",
        "ductfitting",
        "ductsegment",
        "flowterminal",
        "ifcowl_ifcopeningelement",
        "lightfixture",
        "member",
        "plate",
        "railing",
        "ramp",
        "roof",
        "slab",
        "stair",
        "stairflight"
    ]
    print("prune_objects")
    graph = prune_objects(graph, to_prune_classes, base)
    print("serialize " + output)
    graph.serialize(output, format="ttl", base=base)
