import sys
from rdflib import Graph, RDF
from app.namespaces import *

def expand(propertyList):
    for property in propertyList:
        title = property[:1].title() + property[1:]
        p = URIRef(f"{COSWOT._NS}has{title}Property")
        c = URIRef(f"{COSWOT._NS}{title}Property")
        yield (property, p, c)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    base = sys.argv[3]
    graph = Graph(namespace_manager=namespaceManager)
    print("parse")
    graph.parse(input, format="ttl")
    

    print("space")
    spaceProperties = ["temperature", "relativeHumidity", "carbonDioxydeConcentration"]
    for space, in graph.query("""SELECT ?space WHERE { { ?space a bot:Building } UNION { ?space a bot:Storey } UNION { ?space a bot:Zone } UNION { ?space a bot:Space } }"""):
        for name,p,c in expand(spaceProperties):
            o = URIRef(f"{space}{name}")
            graph.add((space, p, o))
            graph.add((o, RDF.type, c))

    print("openable")
    openableProperties = [ "openClose" ]
    for element, in graph.query("""SELECT ?openable WHERE { { ?openable a coswot:Door } UNION { ?openable a coswot:Window } }"""):
        for name,p,c in expand(openableProperties):
            o = URIRef(f"{element}{name}")
            graph.add((element, p, o))
            graph.add((o, RDF.type, c))

    print("serialize")
    graph.serialize(output, format="ttl", base=base)