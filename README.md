# databat-kgc-revit

Knowledge Graph construction from the Revit 3D model of a building

The scripts in this repository are used to generate a knowledge graph with entry point https://ci.mines-stetienne.fr/emse 

This knowledge publicly documents the model of Espace Fauriel Building at Mines Saint-Étienne, using the Building Topology Ontology. 

# How to reproduce

1. Export the IFC model from the Revit 2021 model `rvt/MINES_TCE_DOE_2021.rvt`, using the IFC for Revit add-in exporter and export setup `rvt/IFCExportConfiguration_IFC4 Design Transfer View.json`.
2. Run the IFC-to-LBD converter, with options as shown in `rvt/IFCtoLBD-Desktop_Java_15_options_used.png`
2. Execute the Dynamo script `rvt/RoomAdjacenciesByLevel.dyn` to generate file `schedules/adjacency_guid.csv` that encodes the adjacencies between rooms.
3. Export the schedules whose name begin with "Ifc" into the `schedules` folder. With only option _Export column header_ checked, and option _Field delimiter_ set to `,`.
4. Run the scripts in sequence:
    1. `scripts/1_repareCharacters.py` restores unicode characters obfuscated by the IFC-to-LBD converter
    2. `scripts/2_pruneObjects.py` only keeps objects that have the following string in their IRI: _site_, _building_, _storey_, _space_, _wall_, _window_, _ifcowl_ifcfurniture_, _electricappliance_.
    3. `scripts/3_transformObjects.py` explicitly types the objects, keeps only a few relevant triples from the ones generated by IFC-to-LBD, selects appropriate properties, and converts the objects.
    4. `scripts/4_renameObjects.py` changes the IRIs of objects to IRIs that better reflects the topology of the building.
    5. `scripts/5_readSchedules.py` used to extract important information that have been lost somewhere in the Revit-to-IFC-to-LBD pipeline, including the location of furnitures and devices, and which spaces are adjacent to windows and doors.
    6. `scripts/6_addProperties.py` used to define some SOSA/SSN properties for objects: temperature, CO2, humidity of spaces, and open/close status of doors and windows.
    7. `scripts/7_storeTurtleFiles.py` used to generate the set of turtle files that can then be pushed to the server


Step 4. can be run with the following sequence of commands.

```
python3 -m pip install rdflib
mkdir temp
python3 scripts/1_repareCharacters.py lbd/MINES_TCE_DOE_2021_LBD.ttl temp/0_MINES_TCE_DOE_2021_LBD.ttl
python3 scripts/2_pruneObjects.py temp/0_MINES_TCE_DOE_2021_LBD.ttl temp/1_objects_pruned.ttl https://ci.mines-stetienne.fr/
python3 scripts/3_transformObjects.py temp/1_objects_pruned.ttl temp/2_objects_transformed.ttl https://ci.mines-stetienne.fr/
python3 scripts/4_renameObjects.py temp/2_objects_transformed.ttl temp/3_objects_renamed.ttl https://ci.mines-stetienne.fr/
python3 scripts/5_readSchedules.py temp/3_objects_renamed.ttl temp/4_schedules.ttl https://ci.mines-stetienne.fr/
python3 scripts/6_addProperties.py temp/4_schedules.ttl temp/5_properties.ttl https://ci.mines-stetienne.fr/
python3 scripts/7_storeTurtleFiles.py temp/5_properties.ttl https://ci.mines-stetienne.fr/
```