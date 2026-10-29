[![Build](https://github.com/mknd-io/ontologies/actions/workflows/build.yml/badge.svg)](https://github.com/mknd-io/ontologies/actions/workflows/build.yml)

# Mekanoid Ontology (MKND)

MKND is an OWL ontology for cybersecurity knowledge graphs. It covers observables, alerts, incidents, vulnerabilities (with CVSS) and response actions. It extends [MITRE D3FEND](https://d3fend.mitre.org) and is meant to be used together with it.

- **Namespace:** `https://w3id.org/mknd/` (prefix `mknd:`)
- **Documentation:** <https://mknd-io.github.io/ontologies/>
- **Current release:** 0.4.0, built on D3FEND 0.14.0. See [CHANGELOG.md](CHANGELOG.md).

## Using it

Import the core ontology. It brings in the D3FEND alignment and the pinned D3FEND release:

```turtle
<https://example.org/my-ontology> owl:imports <https://w3id.org/mknd/> .
```

Every IRI resolves through [w3id.org](https://w3id.org/mknd/). Browsers get the documentation; RDF clients get the format they ask for (`text/turtle`, `application/rdf+xml`, `application/ld+json`, `application/n-triples`). To pin a release, use its version IRI, e.g. `https://w3id.org/mknd/0.4.0/`.

| Module | IRI | Source | Contents |
|---|---|---|---|
| Core | `https://w3id.org/mknd/` | [`src/mknd.ttl`](src/mknd.ttl) | MKND classes and properties, plus reference values such as CVSS metric levels and incident statuses |
| D3FEND alignment | `https://w3id.org/mknd/alignment/d3fend` | [`src/mknd-d3fend.ttl`](src/mknd-d3fend.ttl) | Every statement MKND makes about a D3FEND term; imports D3FEND by version IRI |
| Examples | `https://w3id.org/mknd/examples` | [`examples/mknd-examples.ttl`](examples/mknd-examples.ttl) | Illustrative individuals (hosts, sockets, sessions, CVEs, vendors). Not imported by core |
| Datasets | `https://w3id.org/mknd/data/{gtfobins,lolbas}` | [`data/`](data) | [GTFOBins](https://gtfobins.github.io) and [LOLBAS](https://lolbas-project.github.io) binaries and commands as individuals |

## How MKND extends D3FEND

MKND treats D3FEND as a read-only dependency:

1. **No copies of D3FEND in this repo.** The alignment imports a specific release by version IRI (`http://d3fend.mitre.org/ontologies/d3fend/0.14.0/d3fend.owl`). The build downloads it; it is never committed or edited.
2. **New terms go in the MKND namespace.** MKND never mints a `d3f:` IRI. If D3FEND lacks a property, MKND defines it (`mknd:provided-by`, `mknd:connected-by`, …) and links it to D3FEND with `rdfs:subPropertyOf` or `owl:inverseOf`.
3. **Everything MKND says about a D3FEND term lives in one module.** That means subclass links, restrictions, inverses, labels and icons attached to `d3f:` terms. The core only describes MKND terms. Upgrading D3FEND therefore only touches `src/mknd-d3fend.ttl`.

`make test` enforces all three rules (see [`tests/seam/`](tests/seam)).

## Repository layout

```
src/          ontology sources: core, D3FEND alignment, Protégé catalog, Widoco config
examples/     example individuals (imports core)
data/         GTFOBins / LOLBAS datasets (import core)
assets/icons  SVG icons referenced by mknd:icon
tests/        SPARQL checks run by ROBOT, and the w3id redirect test
w3id/         redirect rules served at https://w3id.org/mknd/ (mirror of perma-id/w3id.org ids/mknd)
scripts/      small helpers used by the Makefile
```

Generated files (docs, other serializations, reasoner output) are not committed. They are built into `build/`.

## Working on the ontology

Requirements: Java 17+, Python 3, `curl`, `make`. ROBOT, Widoco, rdflib and the pinned D3FEND release are downloaded on first use.

```sh
make test       # seam rules, quality checks, ELK + HermiT reasoning, w3id redirects
make site       # documentation + all serializations into build/site
```

Edit in Protégé by opening `src/mknd.ttl`. `src/catalog-v001.xml` resolves the alignment and D3FEND to local files; run `make imports` once to download D3FEND for offline use. Protégé's Turtle output is the canonical format, so saving from Protégé keeps diffs small.

### Checks

| Check | What it catches |
|---|---|
| `tests/seam/third-party-subject.rq` | core or examples saying something about a D3FEND term |
| `tests/seam/third-party-declaration.rq` | the alignment declaring (minting) a term D3FEND doesn't have |
| `tests/seam/alignment-scope.rq` | the alignment saying things about MKND terms |
| `tests/seam/undeclared-third-party-term.rq` | references to D3FEND terms missing from the pinned release |
| `tests/quality/*.rq` | undeclared MKND terms, property type clashes, classes used as values or predicates, missing/duplicate labels, missing release metadata. Several are adapted from [D3FEND's own checks](https://github.com/d3fend/d3fend-ontology/tree/master/src/queries) |
| ELK / HermiT | unsatisfiable classes; inconsistency of core + alignment + examples + D3FEND |
| `tests/w3id/run.sh` | `w3id/.htaccess` redirects, on a throwaway local Apache |

The datasets have known modelling problems (D3FEND classes used as predicates, plain strings on object properties). They are tracked by `make data-report`, which does not fail the build.

### Upgrading D3FEND

```sh
make drift D3FEND_NEXT=1.6.0   # D3FEND terms MKND uses that the new release lacks
```

Fix what it reports, then change the version in the `owl:imports` of `src/mknd-d3fend.ttl` and in `src/catalog-v001.xml`. `make test` fails if the two disagree.

### Releasing

1. Set the new version in `owl:versionInfo` and `owl:versionIRI` of every module (core, alignment, examples, data), and update `dcterms:modified`. `make test` fails if a module is left behind.
2. Add a CHANGELOG entry and merge to `main`.
3. Tag the merge commit `v<version>` and push the tag. CI attaches the `/<version>/` snapshot to a GitHub Release.

Every deploy republishes the snapshots of all GitHub Releases, so old version IRIs keep resolving.

## Maintainer

Anton Goncharov ([@ag0x00](https://github.com/ag0x00), <anton.goncharov@gmail.com>, ORCID [0000-0001-7399-6740](https://orcid.org/0000-0001-7399-6740)). Issues and pull requests are welcome.

## License

[MIT](LICENSE). D3FEND is © The MITRE Corporation and is subject to its [terms of use](https://d3fend.mitre.org/about/).
