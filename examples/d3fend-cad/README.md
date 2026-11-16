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

## Checking them

```sh
make cad-report   # needs ROBOT and the pinned D3FEND (make tools imports); doesn't fail the build
```

`cad-report` runs the checks that `make data-report` runs on `data/*.ttl`, plus `class-used-as-value`, the other quality query that applies to instance data:

| Check | Run | Finds |
|---|---|---|
| `tests/seam/third-party-subject.rq` | own triples | statements about a D3FEND term |
| `tests/quality/class-used-as-predicate.rq` | with D3FEND | a class used as a predicate |
| `tests/quality/class-used-as-value.rq` | with D3FEND | `owl:hasValue` pointing at a class |
| `tests/quality/undeclared-mknd-term.rq` | with D3FEND | MKND terms nothing declares |
| `tests/seam/undeclared-third-party-term.rq` | with D3FEND | D3FEND terms missing from D3FEND 1.6.0 |

The rest of `tests/quality/` checks MKND's own classes, properties and release metadata, so it says nothing about instance data.

The graphs have no ontology header, and the two undeclared-term queries only look at modules in the MKND namespace. So `make` writes a copy of each graph to `build/cad/` that adds a header: module IRI `https://w3id.org/mknd/examples/d3fend-cad/<graph>`, importing D3FEND 1.6.0 through `src/catalog-v001.xml`. The graph's triples are unchanged. The import matters for `third-party-subject` too. Run on a bare file, the OWL API can't tell which D3FEND terms are classes and which are object properties, so it adds its own declarations of them. Those are triples about D3FEND terms, and the query then reports 459 of them across the nine files that parse. None of them is in a file.

Results are in `build/reports/cad-<graph>-<check>.tsv`, ROBOT's output in `build/reports/cad-<graph>.log`.

## Results

Run on 2026-11-16 against D3FEND 1.6.0, the pinned release (also the current one). Hits per check:

| Graph | third-party-subject | class-used-as-predicate | class-used-as-value | undeclared-mknd-term | undeclared-third-party-term |
|---|---|---|---|---|---|
| blackenergy | 0 | 0 | 0 | 0 | 0 |
| bushwalk | 0 | 0 | 0 | 0 | 0 |
| colonial-pipeline | 0 | 0 | 0 | 0 | 0 |
| industroyer-attack | 0 | 0 | 0 | 0 | 0 |
| industroyer-malware | 0 | 0 | 0 | 0 | 0 |
| notpetya | 0 | 0 | 0 | 0 | 0 |
| purdue ¹ | 0 | 0 | 0 | 0 | 0 |
| shadowcat | **1** | 0 | 0 | 0 | **1** |
| trisis | 0 | 0 | 0 | 0 | 0 |
| water-unitronics | 0 | 0 | 0 | 0 | 0 |

¹ `purdue.ttl` is not valid Turtle, and ROBOT exits with `INVALID ONTOLOGY FILE ERROR`. Its counts are for the escaped copy described under Triage.

## Triage

Both hits are true: they are errors in the example, not in the checks. So no check query changed.

| Graph | Check | Triple | Verdict |
|---|---|---|---|
| shadowcat | undeclared-third-party-term | `cad:0_7716786725845816 d3f:consider cad:0_8731411193589528` | **Example error: undeclared term.** D3FEND 1.6.0 declares no `d3f:consider`: the term appears nowhere in `d3fend.ttl`. The subject is a `cad:Note` ("We recommend these additional countermeasures…") and the object is a countermeasure. |
| shadowcat | third-party-subject | `d3f:consider rdf:type owl:AnnotationProperty` | **Example error, the same one.** The file doesn't contain this triple. The OWL API adds it on load because D3FEND doesn't declare `d3f:consider` and so gives no property type. The query is right to report it: as loaded, the module declares a D3FEND term. |
| purdue | (all; ROBOT exit 1) | `cad:-copy0_13621401125239707`, `cad:-copy0_28361114232255447`, `cad:-copy0_42383847084654125` (4 occurrences) | **Example error: invalid Turtle.** A prefixed name's local part can't start with `-` ([Turtle 1.1](https://www.w3.org/TR/turtle/#grammar-production-PN_LOCAL), production `PN_LOCAL`). CAD gives copied nodes the ID `-copy0_…` and its export doesn't escape it. `cad:\-copy0_…` names the same IRI and is valid, so `make` checks a copy escaped that way and prints a note. All checks are clean on that copy. |

## What SHACL shapes would catch

The SPARQL checks above test declarations, and only for D3FEND and MKND terms. They don't look at the `cad:` namespace, at how a node's properties fit its D3FEND class, or at literal values. Shapes over D3FEND would. None of the cases below is caught today:

- **Terms outside D3FEND.** A closed shape (`sh:closed true`) on D3FEND's classes, allowing D3FEND's properties, would reject predicates that CAD invented: `cad:dispatches` (industroyer-malware, 6 uses), `cad:if-conditional` (industroyer-attack), `cad:has-payload` (bushwalk), `cad:deceives` and `cad:downloads` (shadowcat), `cad:has-note` (bushwalk, shadowcat). Classes like `cad:Note`, `cad:Thing`, `cad:WebApplication`, `cad:WebServerApplicationProcess`, `cad:StopWindowsService` and `cad:InlinePowerShellScript` are undeclared too, and a `sh:class` on the type would report them. `undeclared-mknd-term` does this for MKND IRIs only.
- **Free text where D3FEND has a relation.** `cad:executes`, `cad:modifies` (blackenergy) and `cad:contains` (trisis) are declared as annotation properties and hold prose: `cad:executes "Launches the Dropbear SSH server…"`, `cad:contains "Py2EXE compiled python script"`. D3FEND has object properties `d3f:executes`, `d3f:modifies` and `d3f:contains` for these, so a reasoner never sees the links. A closed shape reports them. So would `sh:nodeKind sh:IRI` on a whitelist of D3FEND relation names.
- **Values that don't fit D3FEND's restrictions.** In D3FEND, `d3f:Process` is `d3f:process-image-path some d3f:ExecutableBinary`, `d3f:ChangeDefaultPassword` is `d3f:strengthens some d3f:Password`, and `d3f:T1486` (Data Encrypted for Impact) is `d3f:encrypts some d3f:File`. colonial-pipeline links its `d3f:Process` to a `d3f:ExecutableFile` (the superclass), its Change Default Password to a `d3f:Credential` (the superclass of Password), and its T1486 to a `d3f:ClientComputer`. notpetya also has T1486 encrypt a `d3f:ClientComputer`. Under OWL's open world, `some` doesn't limit other values, so the graphs are consistent and no query objects. A shape generated from the restrictions (`sh:class` on the property, at `sh:Warning`) reports these. It also reports cases that are fine as modelling (a `d3f:ClientComputer` that `d3f:contains` a `d3f:FileSystem`). A rough SPARQL count finds 61 such triples across the ten graphs, so these shapes would need review, not a hard failure.
- **Individuals used as classes.** Nine triples link two individuals with `rdfs:subClassOf`: one in bushwalk, four in industroyer-attack, four in purdue. In bushwalk, for example, `cad:0_23244452472671295` (Web Application) `rdfs:subClassOf cad:0_08600091218423167` (a `d3f:ServiceApplication` individual). The graph's own note says this proposes a new class, but OWL reads it as punning: two classes named like the individuals. A shape with `sh:targetSubjectsOf rdfs:subClassOf` and `sh:class owl:Class` catches it. `class-used-as-predicate` and `class-used-as-value` only test the reverse case, a class where an individual belongs.
- **Malformed literals.** In blackenergy, a startup path (`cad:location`) and a registry key (`cad:modifies`) have a line break in the middle (`…{C323A392-5BB0-⏎47D5-…}.lnk`, `…CurrentVersion\⏎Internet Settings…`). `sh:pattern "^[^\n]*$"` on path- and key-valued properties catches these.

Neither kind of check can see what the export dropped. CAD's comment block lists 60 edges it didn't write (28 with no label, and others such as `supports-command`, `note`, `agent-in` and `overwrites`) across nine of the ten graphs. Comparing the files with the CAD JSON is the only way to find them.
