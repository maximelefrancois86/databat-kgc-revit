from rdflib import URIRef, Graph, RDFS, SKOS, DCTERMS
from rdflib.namespace import Namespace, DefinedNamespace, NamespaceManager

class PROPS(DefinedNamespace):
    _fail = False
    _NS = Namespace("http://lbd.arch.rwth-aachen.de/props#")

class BOT(DefinedNamespace):
    _fail = False
    _NS = Namespace("https://w3id.org/bot#")

class COSWOT(DefinedNamespace):
    _fail = False
    Electricappliance: URIRef
    Window: URIRef
    IfcowlIfcfurniture: URIRef
    Door: URIRef
    Site: URIRef
    Space: URIRef
    Storey: URIRef
    Building: URIRef
    Wall: URIRef
    _NS = Namespace("https://w3id.org/coswot/")

class CDT(DefinedNamespace):
    _fail = True
    ucum: URIRef
    _NS = Namespace("https://w3id.org/cdt/")

namespaceManager = NamespaceManager(Graph())
namespaceManager.bind("props", PROPS._NS)
namespaceManager.bind("bot", BOT._NS)
namespaceManager.bind("coswot", COSWOT._NS)
namespaceManager.bind("cdt", CDT._NS)
namespaceManager.bind("skos", SKOS._NS)
namespaceManager.bind("schema", "https://schema.org/")
namespaceManager.bind("dct", DCTERMS._NS)
