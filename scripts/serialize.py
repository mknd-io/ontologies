"""Write RDF/XML, JSON-LD and N-Triples siblings next to a Turtle file.

usage: serialize.py OUT_DIR/NAME.ttl [...]   (each .ttl must already exist)
"""
import sys
from pathlib import Path

import rdflib

FORMATS = {".owl": "xml", ".jsonld": "json-ld", ".nt": "nt"}

for arg in sys.argv[1:]:
    ttl = Path(arg)
    g = rdflib.Graph().parse(ttl, format="turtle")
    for suffix, fmt in FORMATS.items():
        g.serialize(ttl.with_suffix(suffix), format=fmt, encoding="utf-8")
    print(f"{ttl}: {len(g)} triples -> {', '.join(FORMATS)}")
