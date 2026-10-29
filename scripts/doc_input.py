"""Build the Widoco input: MKND core + D3FEND alignment as one document, imports removed.

Widoco cannot use the Protégé catalog, so it would try to fetch the imports over the
network. The rendered page documents MKND terms and MKND's additions to D3FEND terms;
D3FEND itself is linked, not rendered.

usage: doc_input.py OUT.ttl
"""
import sys

import rdflib
from rdflib.namespace import OWL

CORE, ALIGNMENT = "src/mknd.ttl", "src/mknd-d3fend.ttl"
ONTOLOGY = rdflib.URIRef("https://w3id.org/mknd/")

core = rdflib.Graph().parse(CORE)
alignment = rdflib.Graph().parse(ALIGNMENT)
g = rdflib.Graph()
for prefix, ns in core.namespaces():
    g.bind(prefix, ns, override=True)
g += core
alignment_header = set(alignment.subjects(rdflib.RDF.type, OWL.Ontology))
for s, p, o in alignment:
    if s not in alignment_header:
        g.add((s, p, o))
g.remove((ONTOLOGY, OWL.imports, None))
g.serialize(sys.argv[1], format="turtle")
print(f"{sys.argv[1]}: {len(g)} triples")
