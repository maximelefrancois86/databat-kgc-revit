import sys
from rdflib import Graph
from rdflib.query import Result
from app.namespaces import *
from typing import List

"""basic transformation of objects in the building model"""

def transformSite(graph:Graph):
    """Issue somewhere in the toolchain: lat/lon is lon/lat. Wrong value?"""
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Site }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a geo:Feature, bot:Site ;
    skos:hiddenLabel ?hiddenLabel ;
    rdfs:label ?siteName ;
    schema:address ?address ;
    dct:title ?projectName ;
    props:refElevationIfcSite_attribute_simple ?elevation_ucum ;
    geo:hasGeometry [ geo:asWKT ?wkt ] ;
    bot:hasBuilding ?building .
} WHERE {
    ?s a geo:Feature, bot:Site ;
    props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
    props:nameIfcRoot_attribute_simple ?siteName ;
    props:projectAddress_simple ?address ;
    props:projectName_simple ?projectName ;
    props:refElevationIfcSite_attribute_simple ?elevation ;
    geo:hasGeometry [ geo:asWKT ?wkt ] ;
    bot:hasBuilding ?building .
    BIND( STRDT( CONCAT( STR(?elevation), " m") , cdt:ucum ) AS ?elevation_ucum ) 
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Site }""").bindings[0]["count"]
    print(f"bot:Site {count}->{count2}")
    return graph

def transformBuilding(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Building }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Building ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        bot:hasStorey ?storey .
} WHERE {
    ?s a bot:Building ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:nameIfcRoot_attribute_simple ?name ;
        bot:hasStorey ?storey .
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Building }""").bindings[0]["count"]
    print(f"bot:Building {count}->{count2}")
    return graph


def transformStorey(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Storey }""").bindings[0]["count"]
    g = graph.query("""CONSTRUCT {
    ?s a bot:Storey ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        coswot:hasElevationStableValue ?elevation_ucum .
} WHERE {
    ?s a bot:Storey ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:nameIfcRoot_attribute_simple ?name ;
        props:elevationIfcBuildingStorey_attribute_simple ?elevation .
    BIND( STRDT( CONCAT( STR(?elevation), " m") , cdt:ucum ) AS ?elevation_ucum ) 
}""").graph
    g += graph.query("""CONSTRUCT {
    ?s a bot:Storey ;
        bot:containsElement ?element .
} WHERE {
    ?s a bot:Storey ;
        bot:containsElement ?element .
}""").graph
    g += graph.query("""CONSTRUCT {
    ?s a bot:Storey ;
        bot:hasSpace ?space .
} WHERE {
    ?s a bot:Storey ;
        bot:hasSpace ?space .
}""").graph
    g.namespace_manager = namespaceManager
    count2 = g.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Storey }""").bindings[0]["count"]
    print(f"bot:Storey {count}->{count2}")
    return g


def transformSpace(graph:Graph):
    """issues: volume and other quantity values are rounded to the nearest integer"""
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Space }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Space ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        rdfs:comment ?comment ;
        bot:adjacentElement ?adjacentElement .
} WHERE {
    ?s a bot:Space ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:nameIfcRoot_attribute_simple ?name ;
        props:longNameIfcSpatialElement_attribute_simple ?comment ;
        bot:adjacentElement ?adjacentElement .
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a bot:Space }""").bindings[0]["count"]
    print(f"bot:Space {count}->{count2}")
    return graph


def transformDoor(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Door }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Element, coswot:Door ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        rdfs:comment ?comment ;
        bot:adjacentElement ?adjacentElement ;
        coswot:hasOverallWidthStableValue ?width_ucum ;
        coswot:hasOverallHeightStableValue ?height_ucum ;
        coswot:category ?category .
} WHERE {
    ?s a bot:Element, coswot:Door ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:objectTypeIfcObject_attribute_simple ?name ;
        props:overallWidthIfcDoor_attribute_simple ?width ;
        props:overallHeightIfcDoor_attribute_simple ?height ;
        props:category_simple ?category .
    BIND( STRDT( CONCAT( STR(?width), " m") , cdt:ucum ) AS ?width_ucum ) 
    BIND( STRDT( CONCAT( STR(?height), " m") , cdt:ucum ) AS ?height_ucum ) 
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Door }""").bindings[0]["count"]
    print(f"bot:Door {count}->{count2}")
    return graph

def transformKNXDevice(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Electricappliance }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Element, coswot:Device ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        coswot:KNXAddress ?knxAddress ;
        coswot:category ?category .
} WHERE {
    ?s a bot:Element, coswot:Electricappliance ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:objectTypeIfcObject_attribute_simple ?name ;
        props:family_simple "KNX Device: Thing" ;
        props:kNXAddress_simple ?knxAddress ;
        props:category_simple ?category .
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Device }""").bindings[0]["count"]
    print(f"coswot:Device {count}->{count2}")
    return graph

def transformFurniture(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:IfcowlIfcfurniture }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Element, coswot:Furniture ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        coswot:category ?category .
} WHERE {
    ?s a bot:Element, coswot:IfcowlIfcfurniture ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:objectTypeIfcObject_attribute_simple ?name ;
        props:category_simple ?category .
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Furniture }""").bindings[0]["count"]
    print(f"coswot:Furniture {count}->{count2}")
    return graph


def transformWall(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Wall }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Element, coswot:Wall ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        rdfs:comment ?comment ;
        coswot:category ?category ;
        bot:hasSubElement ?element .
} WHERE {
    ?s a bot:Element, coswot:Wall ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:objectTypeIfcObject_attribute_simple ?name ;
        props:category_simple ?category .
    OPTIONAL { ?s props:description_simple ?comment }
    OPTIONAL { ?s bot:hasSubElement ?element }
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Wall }""").bindings[0]["count"]
    print(f"coswot:Wall {count}->{count2}")
    return graph



def transformWindow(graph:Graph):
    count = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Window }""").bindings[0]["count"]
    result = graph.query("""CONSTRUCT {
    ?s a bot:Element, coswot:Window ;
        skos:hiddenLabel ?hiddenLabel ;
        rdfs:label ?name ;
        coswot:hasOverallWidthStableValue ?width_ucum ;
        coswot:hasOverallHeightStableValue ?height_ucum ;
        coswot:category ?category .
} WHERE {
    ?s a bot:Element, coswot:Window ;
        props:globalIdIfcRoot_attribute_simple ?hiddenLabel ;
        props:objectTypeIfcObject_attribute_simple ?name ;
        props:overallHeightIfcWindow_attribute_simple ?height ;
        props:overallWidthIfcWindow_attribute_simple ?width ;
        props:category_simple ?category .
    BIND( STRDT( CONCAT( STR(?width), " m") , cdt:ucum ) AS ?width_ucum ) 
    BIND( STRDT( CONCAT( STR(?height), " m") , cdt:ucum ) AS ?height_ucum ) 
}""") # type: Result
    graph = result.graph
    graph.namespace_manager = namespaceManager
    count2 = graph.query("""SELECT (count(?s) AS ?count) WHERE { ?s a coswot:Window }""").bindings[0]["count"]
    print(f"coswot:Window {count}->{count2}")
    return graph



if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    base = sys.argv[3]
    graph = Graph(namespace_manager=namespaceManager)
    graph.parse(input, format="ttl")
    
    outputGraph = Graph(namespace_manager=namespaceManager)
    outputGraph += transformSite(graph)
    outputGraph += transformBuilding(graph)
    outputGraph += transformStorey(graph)
    outputGraph += transformSpace(graph)
    outputGraph += transformDoor(graph)
    outputGraph += transformKNXDevice(graph)
    outputGraph += transformFurniture(graph)
    outputGraph += transformWall(graph)
    outputGraph += transformWindow(graph)
    
    outputGraph.serialize(output, format="ttl", base=base)
    
    
    
# bot:Site 1->1
# bot:Building 1->1
# bot:Storey 9->9
# bot:Space 215->215
# bot:Door 323->322
# coswot:Device 137->137
# coswot:Furniture 1386->1386
# coswot:Wall 1729->1729
# coswot:Window 313->313