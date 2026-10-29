# Changelog

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
