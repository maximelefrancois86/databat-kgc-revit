# IFCtoRDF

command to generate the ifcOWL graph:

```
java -jar IFCtoRDF-0.4-shaded.jar  --baseURI https://ci.mines-stetienne.fr/fayol/ ../IFC/MINES_TCE_DOE_V1_429\ Ouvert.ifc output.ttl
```


# IFCtoLBD

command to generate the turtle graph with LBD ontologies

```
java -jar IFCtoLBD_CLI.jar -b -be --hasGeolocation --hasGeometry --hasSeparateBuildingElementsModel --hasUnits -l=1 -p -t=output -u https://ci.mines-stetienne.fr/fayol/ ../IFC/MINES_TCE_DOE_V1_429\ Ouvert.ifc
``` 


\\X2\\00E9\\X0\\ --> é
\\X2\\00E8\\X0\\ --> è
\\X2\\00E0\\X0\\ --> à
\\X2\\00E7\\X0\\ --> ç
\\X2\\00E2\\X0\\ --> â
\\X2\\2019\\X0\\ --> '
\\X\\0D\\X\\0A --> \\n
\\X2\\00B0\\X0\\ --> °

properties are floored to the nearest integer 3.67 becomes 3.0^^decimal


Gonçal feedback by the end of the week
need a section for automatic compliance checking and permitting
need a section for ontologies that can be used in combination with the bco ontology (with Task 2.2)


conclusions about these standards:
Gonçal: which are suitable ? 
extract some value from the comparison ? -> which are suitable

Industry partners:
how they decide on using a certain standard or another? (in practice)
obligation based on a country?

bsdd / ids
standards: scope, limitations, compatibility with approaches / rule engines, 
when and where they can be applied. 

Piotr: standards are practice or implementation of interoperability practices
validation/prevalidation 
exchange data in different formats
data model -> encodings 

which level of information ... 

dimension of the implementation ... which standards are implemented ?

relation with work package 1, 4, 5, ...
for the demos: 
what standards the demo leaders are intending to use ...?


format: ifc/citygml, ...
piotr: add 3D tiles ? 



data model and data exchange format,
semantic part: Thamer can finalize that


the ogc standards -> 
Other categories, raise in the technical board meeting, and expect input from WP4 and WP5, 

leave out legal and regulation, it belongs to work package 1.

