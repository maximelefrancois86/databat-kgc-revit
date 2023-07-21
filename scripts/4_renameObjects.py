import sys
from rdflib import Graph
from rdflib.query import Result
from app.namespaces import *

"""implement new naming convention for IRIs"""

def rename(graph:Graph, base:str):
    replacements = {}
    for site, site_name in graph.query("""SELECT ?site ?iri_name WHERE { 
                                            ?site a bot:Site ; 
                                                rdfs:label ?name 
                                            BIND(encode_for_uri(?name) as ?iri_name)
                                        }"""):
        replacements[site] = URIRef(f"{site_name}#", base=base)
        for building, building_name in graph.query("""SELECT ?building ?iri_name WHERE { 
                                                        ?site bot:hasBuilding ?building . 
                                                        ?building a bot:Building ; 
                                                            rdfs:label ?name . 
                                                        BIND(encode_for_uri(?name) as ?iri_name)
                                                    }""", initBindings={'site': site }):
            replacements[building] = URIRef(f"{site_name}/{building_name}#", base=base)
            for storey, storey_name in graph.query("""SELECT ?storey ?iri_name WHERE {
                                                        ?building bot:hasStorey ?storey . 
                                                        ?storey a bot:Storey ; 
                                                            rdfs:label ?name .
                                                        BIND(encode_for_uri(?name) as ?iri_name)
                                                    }""", initBindings={'building': building }):
                replacements[storey] = URIRef(f"{site_name}/{building_name}/{storey_name}#", base=base)
                for space, space_name in graph.query("""SELECT ?space ?iri_name WHERE { 
                                                        ?storey bot:hasSpace ?space . 
                                                        ?space a bot:Space ; 
                                                            rdfs:label ?name .
                                                        BIND(encode_for_uri(?name) as ?iri_name)
                                                    }""", initBindings={'storey': storey }):
                    replacements[space] = URIRef(f"{site_name}/{building_name}/{storey_name}/{space_name}#", base=base)
    new_graph = Graph(namespace_manager=graph.namespace_manager)
    for s,p,o in graph:
        triple = (replacements.get(s, s), replacements.get(p, p), replacements.get(o, o)) 
        new_graph.add(triple)
    # map(new_graph.add, [ (replacements.get(term, term) for term in triple ) for triple in graph ])
    print(f"renaming {len(graph)}->{len(new_graph)}")
    if len(graph) != len(new_graph):
        print("WARNING: duplicate room names!")
        from collections import Counter
        counts = Counter(replacements.values())
        result = {k: v for k, v in replacements.items() if counts[v] > 1}
        import pprint 
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)
    return new_graph


if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    base = sys.argv[3]
    graph = Graph(namespace_manager=namespaceManager)
    print("parse")
    graph.parse(input, format="ttl")
    print("rename")
    outputGraph = rename(graph, base)
    print("serialize")
    outputGraph.serialize(output, format="ttl", base=base)
