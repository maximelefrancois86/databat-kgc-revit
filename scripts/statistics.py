import sys
import os
from rdflib import Graph, RDF, Literal, BNode
from rdflib.term import Node
from app.namespaces import *
import shutil

for file in ["0_MINES_TCE_DOE_2021_LBD", "1_objects_pruned", "2_objects_transformed", "3_objects_renamed", "4_schedules", "5_properties"]:
    g = Graph()
    g.parse(f"temp/{file}.ttl")
    print(f"number of tiples in {file}: {len(g)}") 
    del g

n = 0
sum = 0
for root, dirs, files in os.walk("public"):
    for file in files:
        if not file.endswith(".ttl"):
            continue
        g = Graph()
        g.parse(f"{root}/{file}")
        n +=1
        sum += len(g)
print(f"number of graphs {n}") 
print(f"total number of triples {sum}") 
print(f"average number of triples {sum/n}") 