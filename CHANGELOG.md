# Changelog

## 0.5.0 — 2026-10-29

Built on **MITRE D3FEND 1.6.0** (was 0.14.0). Some IRIs change; see Changed.

### Changed
- **D3FEND pin** `http://d3fend.mitre.org/ontologies/d3fend/0.14.0/d3fend.owl` → `…/1.6.0/d3fend.owl`. References to D3FEND terms that 1.6.0 renamed or removed now point to:

  | 0.14.0 term | Now |
  |---|---|
  | `d3f:NetworkPackets` | `d3f:NetworkPacket` |
  | `d3f:NetworkService` | `d3f:NetworkServiceApplicationProcess` |
  | `d3f:Document` | `d3f:DigitalDocument` |
  | `d3f:DigitalObject` | `d3f:DigitalArtifact` |
  | `d3f:d3fend-catalog-object-property` (parent of `mknd:connected-by`, `isolated-by`, `provided-by`) | `d3f:associated-with` |
  | `d3f:publisher` (examples) | `d3f:provider`; `d3f:publishes` dropped |
  | `d3f:provides` | new `mknd:provides`, inverse of `mknd:provided-by` |
  | `d3f:SoftwareProduct`, `d3f:SoftwareService` | new `mknd:SoftwareProduct` (under `d3f:Software`), `mknd:SoftwareService` (under `d3f:ServiceApplication`) |
  | `d3f:Proposition`, `d3f:Assessment` | new `mknd:Proposition` (under `d3f:DigitalInformation`), `mknd:Assessment` (under `d3f:Action`) |

- **`mknd:Malware`** is now Software that `d3f:implements some d3f:OffensiveTechnique`. In D3FEND 1.x techniques are plans, not goals, so the old `d3f:has-goal` definition left the class empty.
- **`mknd:ManualTaskRun`** is now under `d3f:Action` (it was under `d3f:UserAction`, which 1.x turned into a record) and is disjoint with `mknd:MachineAction`.
- **Datasets are generated** by `scripts/data/generate.py` (`make data`) from pinned upstream revisions, recorded in each file's `dcterms:source`: GTFOBins `d1d30414` and LOLBAS `ded90467`, the revisions the 0.4.0 files came from.
  - String facts are datatype properties now instead of D3FEND classes misused as predicates: new `mknd:operating-system`, `mknd:required-privileges` and `mknd:use-case`; existing `mknd:extCategory` and `mknd:extType`.
  - ATT&CK techniques are individuals typed by their D3FEND class (e.g. `mknd:technique_T1218 a d3f:T1218`), so classes are no longer used as values. Deprecated techniques get their successor (`T1562.001` → `T1685`).
  - Case-variant Windows directories are merged into one individual (variants become `skos:altLabel`) instead of `owl:sameAs` links. Placeholder files ("N/A", "No fixed path") are removed.
  - LOLBAS gains the 2 entries the old export missed (rdrleakdiag.exe, UtilityFunctions.ps1).
  - Generated descriptions on `d3f:Detect` individuals are dropped; they were derived from the URL path, not from upstream.
- `owl:priorVersion` now points at `https://w3id.org/mknd/0.4.0/`.

## 0.4.0 — 2026-10-29

Breaking: every IRI changes. Re-point imports and data at the new namespace.

### Changed
- **Namespace** `https://mekanoid.io/ontology/` → `https://w3id.org/mknd/`. The old domain never resolved; the new IRIs redirect to the documentation and serializations.
- **Modules.** The single `mknd.ttl` is split into core (`https://w3id.org/mknd/`), the D3FEND alignment (`https://w3id.org/mknd/alignment/d3fend`), examples (`https://w3id.org/mknd/examples`) and datasets (`https://w3id.org/mknd/data/gtfobins`, `…/data/lolbas`). Importing core no longer pulls in example individuals.
- **D3FEND import** is pinned to version IRI `http://d3fend.mitre.org/ontologies/d3fend/0.14.0/d3fend.owl` instead of the unversioned IRI, which silently followed D3FEND releases.
- **Terms formerly minted in the D3FEND namespace** move to MKND:
  - `d3f:connected-by` → `mknd:connected-by`
  - `d3f:isolated-by` → `mknd:isolated-by`
  - `d3f:providedBy` and `d3f:provided-by` → `mknd:provided-by`
- `mknd:hasURL`, `mknd:importBucketUrl` and `mknd:reference` are datatype properties only (they were also typed as object properties). `mknd:hasURL` now has range `xsd:anyURI` and is no longer a sub-property of `d3f:identifier`.
- `mknd:timeCreatedEpoch`, `mknd:firstSeenEpoch` and `mknd:lastSeenEpoch` are labelled "… (epoch)" to tell them apart from their non-epoch counterparts.

### Fixed
- The ontology with its examples was inconsistent: a `d3f:has-link` value lacked `xsd:anyURI`, and `mknd:hasURL` values (`xsd:anyURI`) violated the `xsd:string` range inherited from `d3f:identifier`.
- `d3f:Subroutine` restriction `d3f:uses hasValue d3f:IPAddress` turned the class into an individual; it is now `someValuesFrom`.
- `owl:qualifiedCardinality` was declared as an annotation property.
- 19 classes and properties had no label.

### Removed
- Vendored copies of D3FEND (0.13.0-BETA-1, 0.14.0) and schema.org; the Protégé inferred-axioms export `mknd-axioms.ttl`; committed Widoco output. Documentation and serializations are now built by CI.

## 0.3.0 — 2024-01-30

Last release under `https://mekanoid.io/ontology/`.
