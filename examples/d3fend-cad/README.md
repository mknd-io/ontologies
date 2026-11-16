# D3FEND CAD example graphs

Ten graphs that MITRE D3FEND publishes as CAD examples: models of real incidents and systems, built from D3FEND classes and properties. They are reference examples of normalized subgraph data. D3FEND is the authority for them; MKND keeps them here to test its data checks against.

The files are D3FEND CAD's Turtle export ("Save As Turtle") of the published CAD graphs, unchanged. Each node is an individual in `http://d3fend.mitre.org/ontologies/cad/instances#`, typed with D3FEND classes and linked with D3FEND properties. Terms CAD doesn't find in D3FEND get a `cad:` IRI, and the export lists dropped edges in a comment block at the end of each file. None of the files has an ontology header or imports.

They are not part of MKND and do not import it. `make test` does not read them.

## Sources

Each graph opens in D3FEND CAD at the first link. The second link is the CAD JSON that link loads.

| File | Graph | Open in CAD | CAD source |
|---|---|---|---|
| `blackenergy.ttl` | BlackEnergy attack on Ukrainian power grid | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/blackenergy.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/blackenergy.json> |
| `bushwalk.ttl` | BUSHWALK web shell | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/examples/bushwalk.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/examples/bushwalk.json> |
| `colonial-pipeline.ttl` | Colonial Pipeline incident | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/colonial-pipeline.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/colonial-pipeline.json> |
| `industroyer-attack.ttl` | Industroyer attack | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/industroyer-attack.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/industroyer-attack.json> |
| `industroyer-malware.ttl` | Industroyer malware | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/industroyer-malware.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/industroyer-malware.json> |
| `notpetya.ttl` | NotPetya ransomware attack | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/notpetya.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/notpetya.json> |
| `purdue.ttl` | Purdue model reference architecture | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/purdue.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/purdue.json> |
| `shadowcat.ttl` | SHADOWCAT intrusion | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/examples/shadowcat.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/examples/shadowcat.json> |
| `trisis.ttl` | TRISIS (TRITON) safety-system attack | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/trisis.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/trisis.json> |
| `water-unitronics.ttl` | Water system Unitronics PLC attacks | [CAD](https://d3fend.mitre.org/cad/?load=../resources/cad/domain/ot/water-unitronics.json&render_meta=true) | <https://d3fend.mitre.org/resources/cad/domain/ot/water-unitronics.json> |

The seven OT graphs are listed on [D3FEND for OT](https://d3fend.mitre.org/domain/ot/). BUSHWALK and SHADOWCAT are in the [CAD](https://d3fend.mitre.org/cad/) example list (`https://d3fend.mitre.org/cad/examples.json`). Industroyer malware is served from the same OT folder.

## Licence

These graphs are D3FEND website content, so D3FEND's [Terms of Use](https://d3fend.mitre.org/tou/) apply: MITRE grants a non-exclusive, royalty-free licence to use D3FEND for research, development and commercial purposes, provided every copy reproduces MITRE's copyright designation and that licence. [`LICENSE`](LICENSE) in this folder does so. The D3FEND ontology itself is MIT-licensed: `dcterms:license "MIT"` in the header of D3FEND 1.6.0 (`d3fend.ttl`), and [`LICENSE.md`](https://github.com/d3fend/d3fend-ontology/blob/develop/LICENSE.md) in d3fend/d3fend-ontology ("Copyright (c) 2022 The MITRE Corporation"). This repository's MIT licence does not cover this folder.
