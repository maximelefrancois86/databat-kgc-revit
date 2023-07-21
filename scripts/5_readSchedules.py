import sys
import csv
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL
from collections import namedtuple
from app.namespaces import *
from app.utils import camel_case, strip_accents
from itertools import combinations

def addAssemblyCode(graph:Graph, iri:URIRef, assemblyCode:str, assemblyDescription:str):
    if not assemblyCode or not assemblyDescription:
        return
    uniformatAssemblyCode = URIRef(f"kg/uniformat/{assemblyCode}#", base=base)
    graph.add((iri, COSWOT.hasUniformatAssemblyCode, uniformatAssemblyCode))
    graph.add((uniformatAssemblyCode, RDF.type, COSWOT.UniformatAssemblyCode))
    graph.add((uniformatAssemblyCode, RDFS.label, Literal(assemblyCode)))
    graph.add((uniformatAssemblyCode, RDFS.comment, Literal(assemblyDescription)))

def readScheduleSpace(graph:Graph, base:str):
    g, r = Graph(namespace_manager=namespaceManager), {}
    with open("schedules/IfcRoom.csv") as file:
        reader = csv.reader(file)
        next(reader)
        Data = namedtuple("IfcSpace", ["IfcGUID","Level","ZoneName","Number","Name","IfcExportAs","Department","Occupancy","Area","Volume","Perimeter","UnboundedHeight"])
        for data in map(Data._make, reader):
            iri = URIRef(f"emse/fayol/{data.Level}/{data.Number}#", base=base)
            storey = URIRef(f"emse/fayol/{data.Level}#", base=base)
            zone = URIRef(f"emse/fayol/{data.Level}/{data.ZoneName}#", base=base)
            g.add((zone, RDF.type, BOT.Zone))
            g.add((storey, BOT.containsZone, zone))
            g.add((zone, BOT.hasSpace, iri))
            g.remove((storey, BOT.hasSpace, iri))
            # ignore name
            # ignore IfcExportAs
            # ignore Department
            # ignore Occupancy
            if data.Area[0].isdigit():
                g.add((iri, COSWOT.hasAreaStableValue, Literal(f"{data.Area[:-3]} m2", datatype=CDT.ucum)))
            if data.Volume[0].isdigit():
                g.add((iri, COSWOT.hasVolumeStableValue, Literal(f"{data.Volume[:-3]} m3", datatype=CDT.ucum)))
            if data.Perimeter[0].isdigit():
                g.add((iri, COSWOT.hasPerimeterStableValue, Literal(f"{data.Perimeter[:-3]} m", datatype=CDT.ucum)))
            if data.UnboundedHeight[0].isdigit():
                g.add((iri, COSWOT.hasUnboundedHeightStableValue, Literal(f"{data.UnboundedHeight} m", datatype=CDT.ucum)))
    return g, r

def readScheduleDoor(graph:Graph, base:str):
    g, r = Graph(namespace_manager=namespaceManager), {}
    with open("schedules/IfcDoor.csv") as file:
        reader = csv.reader(file)
        next(reader)
        Data = namedtuple("IfcDoor", ["IfcGUID","Family","Type","Assembly_code","Assembly_description",
                                    "Level","Largeur","Hauteur","From","To","HeatTransferCoefficient","ThermalResistance","Thickness"])
        for data in map(Data._make, reader):
            result = graph.query("""SELECT ?door WHERE { ?door skos:hiddenLabel ?label }""", initBindings={"label": Literal(data.IfcGUID)})
            if not len(result):
                print(f"Warning unkown IfcGUID {data.IfcGUID}")
                continue
            iri = result.bindings[0]["door"]
            r[iri] = URIRef(f"emse/fayol/{data.Level}/door/{data.IfcGUID}#", base=base)
            # ignore family
            # ignore type
            addAssemblyCode(g, iri, data.Assembly_code, data.Assembly_description)
            level = URIRef(f"emse/fayol/{data.Level}#", base=base)
            g.add((level, BOT.containsElement, iri))
            g.add((iri, COSWOT.hasWidthStableValue, Literal(f"{data.Largeur} m", datatype=CDT.ucum)))
            g.add((iri, COSWOT.hasHeightStableValue, Literal(f"{data.Hauteur} m", datatype=CDT.ucum)))
            if data.From:
                room = URIRef(f"emse/fayol/{data.Level}/{data.From}#", base=base)
                g.add((room, BOT.adjacentElement, iri))
            if data.To:
                room = URIRef(f"emse/fayol/{data.Level}/{data.To}#", base=base)
                g.add((room, BOT.adjacentElement, iri))
            if data.HeatTransferCoefficient:
                g.add((iri, COSWOT.hasHeatTransferCoefficientStableValue, Literal(f"{data.HeatTransferCoefficient[:-9]} W/(m2.K)", datatype=CDT.ucum)))
            if data.ThermalResistance:            
                g.add((iri, COSWOT.hasThermalResistanceStableValue, Literal(f"{data.ThermalResistance[:-9]} (m2.K)/W", datatype=CDT.ucum)))
            g.add((iri, COSWOT.hasThicknessStableValue, Literal(f"{data.Thickness} m", datatype=CDT.ucum)))
    return g, r

def readCanWalkTo(graph:Graph):
    # for room1, room2 in graph.query("""SELECT DISTINCT ?room1 ?room2 WHERE {
    #     ?room1 rdf:type bot:Space ; bot:adjacentElement ?door .
    #     ?room2 rdf:type bot:Space ; bot:adjacentElement ?door .
    #     ?door a coswot:Door .
    #     FILTER( ?room1 != ?room2 )
    # }"""): # too slow
    for door,_,_ in graph.triples((None, RDF.type, COSWOT.Door)):
        rooms = { room for room,_,_ in graph.triples((None, BOT.adjacentElement, door)) if (room, RDF.type, BOT.Space) in graph }
        for room1, room2 in combinations(rooms, 2):
            graph.add((room1, COSWOT.canWalkTo, room2))
            graph.add((room2, COSWOT.canWalkTo, room1))

def readElectricAppliance(graph:Graph, base:str):
    g, r = Graph(namespace_manager=namespaceManager), {}
    with open("schedules/IfcElectricAppliance.csv") as file:
        reader = csv.reader(file)
        next(reader)
        Data = namedtuple("IfcDoor", ["IfcGUID","Family","Type","Level","RoomNumber","KNXAddress","Assembly_code","Assembly_description"])
        for data in map(Data._make, reader):
            result = graph.query("""SELECT ?device WHERE { ?device skos:hiddenLabel ?label }""", initBindings={"label": Literal(data.IfcGUID)})
            if not len(result):
                print(f"Warning unkown IfcGUID {data.IfcGUID}")
                continue
            room = URIRef(f"emse/fayol/{data.Level}/{data.RoomNumber}#", base=base)
            iri = result.bindings[0]["device"]
            r[iri] = URIRef(f"emse/fayol/{data.Level}/{data.RoomNumber}/device/{data.IfcGUID}#", base=base)
            g.add((room, BOT.containsElement, iri))
            g.add((iri, OWL.sameAs, URIRef(f"knx/emse/fayol/{data.KNXAddress}")))
            addAssemblyCode(g, iri, data.Assembly_code, data.Assembly_description)
    return g, r


def readFurniture(graph:Graph, base:str):
    g, r = Graph(namespace_manager=namespaceManager), {}
    with open("schedules/IfcFurniture.csv") as file:
        reader = csv.reader(file)
        next(reader)
        Data = namedtuple("IfcFurniture", ["IfcGUID","Level","RoomNumber","Assembly_code","Assembly_description","Family","Type"])
        for data in map(Data._make, reader):
            result = graph.query("""SELECT ?furniture WHERE { ?furniture skos:hiddenLabel ?label }""", initBindings={"label": Literal(data.IfcGUID)})
            if not len(result):
                print(f"Warning unkown IfcGUID {data.IfcGUID}")
                continue
            if data.RoomNumber:
                host = URIRef(f"emse/fayol/{data.Level}/{data.RoomNumber}#", base=base)
            else:
                host = URIRef(f"emse/fayol/{data.Level}#", base=base)
            iri = result.bindings[0]["furniture"]
            typ = camel_case(strip_accents(data.Family))
            r[iri] = URIRef(f"{str(host)[:-1]}/{typ}/{data.IfcGUID}#", base=base)
            g.add((host, BOT.containsElement, iri))
            addAssemblyCode(g, iri, data.Assembly_code, data.Assembly_description)
    return g, r

            
def readWall(graph:Graph, base:str):
    g, r = Graph(namespace_manager=namespaceManager), {}
    guids = []
    with open("schedules/IfcWall.csv") as file:
        reader = csv.reader(file)
        next(reader)
        Data = namedtuple("IfcWall", ["IfcGUID","Family","Type","Assembly_code","Assembly_description","HeatTransferCoefficient","ThermalResistance","Width","Length","Area","Volume","ThermalMass"])
        for data in map(Data._make, reader):
            guids.append(data.IfcGUID)
            result = graph.query("""SELECT ?wall ?host WHERE { 
                                 ?wall skos:hiddenLabel ?label . 
                                 OPTIONAL { ?host bot:containsElement ?wall } 
                                 } ORDER BY DESC(?host)""", initBindings={"label": Literal(data.IfcGUID)})
            if not len(result):
                continue
            iri = result.bindings[0]["wall"]
            host = result.bindings[0]["host"]
            if host:
                r[iri] = URIRef(f"{host[:-1]}/wall/{data.IfcGUID}#", base=base)
            else:
                r[iri] = URIRef(f"emse/fayol/wall/{data.IfcGUID}#", base=base)
            addAssemblyCode(g, iri, data.Assembly_code, data.Assembly_description)
            if data.HeatTransferCoefficient:
                g.add((iri, COSWOT.hasHeatTransferCoefficientStableValue, Literal(f"{data.HeatTransferCoefficient[:-9]} W/(m2.K)", datatype=CDT.ucum)))
            if data.ThermalResistance:            
                g.add((iri, COSWOT.hasThermalResistanceStableValue, Literal(f"{data.ThermalResistance[:-9]} (m2.K)/W", datatype=CDT.ucum)))
            if data.Width:            
                g.add((iri, COSWOT.hasWidthStableValue, Literal(f"{data.Width} m", datatype=CDT.ucum)))
            if data.Length:            
                g.add((iri, COSWOT.hasLengthStableValue, Literal(f"{data.Length} m", datatype=CDT.ucum)))
            if data.Area:
                g.add((iri, COSWOT.hasAreaStableValue, Literal(f"{data.Area[:-3]} m2", datatype=CDT.ucum)))
            if data.Volume:
                g.add((iri, COSWOT.hasVolumeStableValue, Literal(f"{data.Volume[:-3]} m", datatype=CDT.ucum)))
            if data.Volume:
                g.add((iri, COSWOT.hasThermalMassStableValue, Literal(f"{data.ThermalMass} m", datatype=CDT.ucum)))
    # deal with unscheduled walls
    for wall, label, host in graph.query("""SELECT ?wall ?label ?host WHERE { 
                                                ?wall a coswot:Wall .
                                                ?wall skos:hiddenLabel ?label . 
                                                OPTIONAL { ?host bot:containsElement ?wall } }"""):
        if str(label) in guids:
            continue
        if not host:
            host = URIRef(f"emse/fayol#")
        r[wall] = URIRef(f"{host[:-1]}/wall/{label}#", base=base)                
    return g, r

    


def readWindow(graph:Graph, base:str):
    g, r = Graph(namespace_manager=namespaceManager), {}
    with open("schedules/IfcWindow.csv") as file:
        reader = csv.reader(file)
        next(reader)
        Data = namedtuple("IfcWindow", ["IfcGUID","Description","Dimensions","Level",
                                        "ConductiviteThermique","ResistanceThermique","Largeur","Hauteur","From","To"])
        for data in map(Data._make, reader):
            result = graph.query("""SELECT ?window WHERE { ?window skos:hiddenLabel ?label }""", initBindings={"label": Literal(data.IfcGUID)})
            if not len(result):
                print(f"Warning unkown IfcGUID {data.IfcGUID}")
                continue
            iri = result.bindings[0]["window"]
            r[iri] = URIRef(f"emse/fayol/{data.Level}/window/{data.IfcGUID}#", base=base)
            # ignore description
            g.add((iri, COSWOT.hasDimensionsStableValue, Literal(data.Dimensions)))
            if data.ConductiviteThermique:
                g.add((iri, COSWOT.hasHeatTransferCoefficientStableValue, Literal(f"{data.ConductiviteThermique[:-9]} W/(m2.K)", datatype=CDT.ucum)))
            if data.ResistanceThermique:            
                g.add((iri, COSWOT.hasThermalResistanceStableValue, Literal(f"{data.ResistanceThermique[:-9]} (m2.K)/W", datatype=CDT.ucum)))
            if data.Largeur:            
                g.add((iri, COSWOT.hasWidthStableValue, Literal(f"{data.Largeur} m", datatype=CDT.ucum)))
            if data.Hauteur:            
                g.add((iri, COSWOT.hasHeightStableValue, Literal(f"{data.Hauteur} m", datatype=CDT.ucum)))
            if data.From:
                room = URIRef(f"emse/fayol/{data.Level}/{data.From}#", base=base)
                g.add((room, BOT.adjacentElement, iri))
            if data.To:
                room = URIRef(f"emse/fayol/{data.Level}/{data.To}#", base=base)
                g.add((room, BOT.adjacentElement, iri))
    return g, r

def readAdjacency(graph):
    g = Graph(namespace_manager=namespaceManager)
    with open("schedules/adjacency_guid.csv") as file:
        reader = csv.reader(file)
        for data in reader:
            guid = data[0]
            iri1 = graph.query("""SELECT ?room WHERE { ?room skos:hiddenLabel ?label }""", initBindings={"label": Literal(guid)}).bindings[0]["room"]
            for guid in data[1:]:
                iri2 = graph.query("""SELECT ?room WHERE { ?room skos:hiddenLabel ?label }""", initBindings={"label": Literal(guid)}).bindings[0]["room"]
                g.add((iri1, BOT.adjacentTo, iri2))
    return g

if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    base = sys.argv[3]
    graph = Graph(namespace_manager=namespaceManager)
    graph.parse(input, format="ttl")
    replacements = {}
    
    print("readScheduleSpace")
    g, r = readScheduleSpace(graph, base)
    graph += g
    replacements.update(r)
    
    print("readScheduleDoor")
    g, r = readScheduleDoor(graph, base)
    graph += g
    replacements.update(r)

    print("readCanWalkTo")
    readCanWalkTo(graph)
    
    print("readElectricAppliance")
    g, r = readElectricAppliance(graph, base)
    graph += g
    replacements.update(r)
    
    print("readFurniture")
    g, r = readFurniture(graph, base)
    graph += g
    replacements.update(r)

    print("readWall")
    g, r = readWall(graph, base)
    graph += g
    replacements.update(r)

    print("readWindow")
    g, r = readWindow(graph, base)
    graph += g
    replacements.update(r)

    print("readAdjacency")
    graph += readAdjacency(graph)

    new_graph = Graph(namespace_manager=graph.namespace_manager)
    for s,p,o in graph:
        triple = (replacements.get(s, s), replacements.get(p, p), replacements.get(o, o)) 
        new_graph.add(triple)
    print(f"renaming {len(graph)}->{len(new_graph)}")
    if len(graph) != len(new_graph):
        print("WARNING: duplicate room names!")
        from collections import Counter
        counts = Counter(replacements.values())
        result = {k: v for k, v in replacements.items() if counts[v] > 1}
        import pprint 
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)

    new_graph.serialize(output, format="ttl", base=base)
