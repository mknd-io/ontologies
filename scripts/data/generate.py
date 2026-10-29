#!/usr/bin/env python3
"""Generate data/gtfobins.ttl and data/lolbas.ttl from pinned upstream revisions.

    generate.py --d3fend build/imports/d3fend-X.ttl [--cache build/upstream] [--out data] [gtfobins] [lolbas]

Upstream repositories and revisions are pinned in scripts/data/sources.json. Tarballs are
downloaded once from codeload.github.com into --cache (network needed on first run only).
Output is deterministic: the same pins, D3FEND release and src/mknd.ttl give byte-identical
files.

Modelling (see README, "Data"):
  * individuals keep the IRI scheme of the original 2024 export: mknd:command_<cmd>,
    mknd:executable_<name>, mknd:function_<name>, mknd:file_<dir>_<name>,
    mknd:directory_<dir>, mknd:detect_<type>-<url>; <...> is percent-encoded.
  * string facts use datatype properties (mknd:operating-system, mknd:required-privileges,
    mknd:use-case, mknd:extCategory, mknd:extType), never D3FEND classes as predicates.
  * GTFOBins functions are d3f:Subroutine individuals linked with mknd:provides.
  * an ATT&CK technique is an individual mknd:technique_<ID> typed with the D3FEND
    technique class, so the class itself is never used as an individual (no punning).
    Techniques that the pinned D3FEND release deprecates are replaced by the technique
    named in its rdfs:seeAlso.
  * Windows paths are case-insensitive: directories that differ only in case are one
    individual (most frequent spelling; the others become skos:altLabel).
"""
import argparse
import io
import json
import re
import sys
import tarfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import quote

import yaml
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS

ROOT = Path(__file__).resolve().parents[2]
MKND = Namespace("https://w3id.org/mknd/")
D3F = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")

CREATOR = URIRef("https://orcid.org/0000-0001-7399-6740")
LICENSE = URIRef("https://opensource.org/license/mit")

DATASETS = {
    "gtfobins": {
        "title": "GTFOBins dataset for MKND",
        "description": "Unix binaries and the commands from GTFOBins (https://gtfobins.github.io) "
                       "that can be abused with them, as MKND/D3FEND individuals.",
        "log_label": "gtfobins collector script",
    },
    "lolbas": {
        "title": "LOLBAS dataset for MKND",
        "description": "Windows living-off-the-land binaries, scripts and libraries from the LOLBAS "
                       "project (https://lolbas-project.github.io), as MKND/D3FEND individuals.",
        "log_label": "lolbas collector script",
    },
}

# LOLBAS keeps entries in one directory per type; the website shows these type names.
LOLBAS_TYPES = {"OSBinaries": "Binaries", "OSLibraries": "Libraries", "OSScripts": "Scripts",
                "OtherMSBinaries": "OtherMSBinaries"}


def iri(kind, *parts):
    """mknd:<kind>_<part>[_<part>...] with every part percent-encoded (the 2024 scheme)."""
    return MKND[kind + "_" + "_".join(quote(p, safe="!'*") for p in parts)]


# ---------------------------------------------------------------------------- upstream
def fetch(source, cache):
    repo, rev = source["repo"], source["rev"]
    path = cache / f"{repo.replace('/', '_')}-{rev}.tar.gz"
    if not path.exists():
        cache.mkdir(parents=True, exist_ok=True)
        url = f"https://codeload.github.com/{repo}/tar.gz/{rev}"
        print(f"fetching {url}", file=sys.stderr)
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        path.with_suffix(".part").write_bytes(data)
        path.with_suffix(".part").rename(path)
    files = {}
    with tarfile.open(path) as tar:
        for m in tar.getmembers():
            if m.isfile() and m.name.endswith((".md", ".yml")):
                rel = str(PurePosixPath(*PurePosixPath(m.name).parts[1:]))  # drop <repo>-<rev>/
                files[rel] = tar.extractfile(m).read().decode("utf-8")
    return files


# ---------------------------------------------------------------------------- D3FEND
class Techniques:
    """Map ATT&CK IDs to the D3FEND technique class of the pinned release."""

    def __init__(self, d3fend_ttl):
        self.g = Graph().parse(d3fend_ttl)
        self.by_id = {}
        for cls, tid in self.g.subject_objects(D3F["attack-id"]):
            if (cls, RDF.type, OWL.Class) in self.g and str(cls) == str(D3F[str(tid)]):
                self.by_id[str(tid)] = cls

    def deprecated(self, cls):
        return any(o.toPython() is True for o in self.g.objects(cls, OWL.deprecated))

    def resolve(self, tid):
        """(attack id, class) for tid, following deprecations; class is None if unknown."""
        cls = self.by_id.get(tid)
        seen = set()
        while cls is not None and self.deprecated(cls) and cls not in seen:
            seen.add(cls)
            nxt = [o for o in self.g.objects(cls, RDFS.seeAlso)
                   if (o, D3F["attack-id"], None) in self.g and not self.deprecated(o)]
            if len(nxt) != 1:
                break
            cls = nxt[0]
        if cls is None:
            return tid, None
        return str(self.g.value(cls, D3F["attack-id"])), cls

    def label(self, cls):
        return self.g.value(cls, RDFS.label)


# ---------------------------------------------------------------------------- output
class Dataset:
    def __init__(self, name, source, core):
        self.name = name
        self.g = Graph()
        for p, ns in (("d3f", D3F), ("dcterms", DCTERMS), ("mknd", MKND), ("owl", OWL),
                      ("rdfs", RDFS), ("skos", SKOS), ("xsd", XSD)):
            self.g.bind(p, ns, replace=True)
        self.log = MKND["ingestion_log_" + name]
        meta = DATASETS[name]
        version, modified = core
        ont = URIRef(f"https://w3id.org/mknd/data/{name}")
        tree = URIRef(f"https://github.com/{source['repo']}/tree/{source['rev']}")
        g = self.g
        g.add((ont, RDF.type, OWL.Ontology))
        g.add((ont, OWL.versionIRI, URIRef(f"{ont}/{version}")))
        g.add((ont, OWL.versionInfo, Literal(version)))
        g.add((ont, OWL.imports, URIRef(str(MKND))))
        g.add((ont, DCTERMS.title, Literal(meta["title"], lang="en")))
        g.add((ont, DCTERMS.description, Literal(meta["description"], lang="en")))
        g.add((ont, DCTERMS.creator, CREATOR))
        g.add((ont, DCTERMS.license, LICENSE))
        g.add((ont, DCTERMS.modified, Literal(modified, datatype=XSD.date)))
        g.add((ont, DCTERMS.source, tree))
        g.add((ont, DCTERMS.date, Literal(source["date"], datatype=XSD.date)))
        g.add((ont, RDFS.comment, Literal(
            f"Generated by scripts/data/generate.py (`make data`) from {source['repo']} at commit "
            f"{source['rev']} ({source['date']}); dcterms:date is that commit's date. "
            "Do not edit by hand.", lang="en")))
        self.individual(self.log, D3F.EventLog, meta["log_label"], value=False)

    def individual(self, s, cls, label, value=True):
        g = self.g
        g.add((s, RDF.type, cls))
        g.add((s, RDF.type, OWL.NamedIndividual))
        g.add((s, RDFS.label, Literal(label)))
        if value:
            g.add((s, MKND.value, Literal(label)))
        if s != self.log:
            g.add((s, D3F["created-by"], self.log))
            g.add((self.log, D3F.creates, s))
        return s

    def text(self, s, p, value):
        if value is not None and str(value).strip():
            self.g.add((s, p, Literal(str(value))))

    def link(self, s, p, o, inverse=None):
        self.g.add((s, p, o))
        if inverse is not None:
            self.g.add((o, inverse, s))

    def technique(self, techniques, tid):
        tid, cls = techniques.resolve(tid.strip())
        t = MKND["technique_" + quote(tid, safe="")]
        if cls is None:
            print(f"warning: {self.name}: ATT&CK {tid} is not in the pinned D3FEND release; "
                  "typed d3f:OffensiveTechnique", file=sys.stderr)
            self.individual(t, D3F.OffensiveTechnique, tid, value=False)
        else:
            self.individual(t, cls, f"{tid} {techniques.label(cls)}", value=False)
        self.g.add((t, D3F["attack-id"], Literal(tid)))
        return t

    def write(self, path):
        data = self.g.serialize(format="turtle")
        Path(path).write_text(data, encoding="utf-8")
        print(f"{path}: {len(self.g)} triples", file=sys.stderr)


# ---------------------------------------------------------------------------- GTFOBins
FRONT_MATTER = re.compile(r"\A---\n(.*?\n)---", re.S)


def gtfobins(files, ds, techniques):
    pages = sorted(p for p in files if p.startswith("_gtfobins/") and p.endswith(".md"))
    if not pages:
        sys.exit("gtfobins: no _gtfobins/*.md pages; the generator reads the pre-2025 page format")
    for page in pages:
        binary = PurePosixPath(page).stem
        meta = yaml.safe_load(FRONT_MATTER.match(files[page]).group(1)) or {}
        exe = ds.individual(iri("executable", binary), D3F.ExecutableFile, binary)
        ds.text(exe, MKND["operating-system"], "Unix")
        ds.text(exe, D3F.description, meta.get("description"))
        for function, examples in (meta.get("functions") or {}).items():
            fn = ds.individual(iri("function", function), D3F.Subroutine, function)
            cmd = ds.individual(iri("command", f"{binary}-{function}"), D3F.Command,
                                f"{binary}-{function}", value=False)
            ds.text(cmd, MKND["operating-system"], "Unix")
            ds.link(exe, MKND.provides, fn, inverse=MKND["provided-by"])
            ds.link(cmd, MKND.provides, fn, inverse=MKND["provided-by"])
            ds.link(cmd, MKND["provided-by"], exe)
            ds.link(cmd, D3F.uses, exe, inverse=D3F["used-by"])
            for ex in examples or []:
                ds.text(cmd, MKND.value, ex.get("code"))
                ds.text(cmd, D3F.description, ex.get("description"))
                for tid in ex.get("mitre") or []:
                    ds.link(cmd, D3F.enables, ds.technique(techniques, tid))


# ---------------------------------------------------------------------------- LOLBAS
def lolbas(files, ds, techniques):
    entries = []
    for path in sorted(files):
        parts = PurePosixPath(path).parts
        if len(parts) == 3 and parts[0] == "yml" and parts[1] in LOLBAS_TYPES and path.endswith(".yml"):
            entries.append((LOLBAS_TYPES[parts[1]], yaml.safe_load(files[path])))
    if not entries:
        sys.exit("lolbas: no yml/<type>/*.yml entries")

    # Windows paths are case-insensitive: one directory per case-folded path.
    spellings = defaultdict(Counter)
    for _, e in entries:
        for fp in e.get("Full_Path") or []:
            p = full_path(fp)
            if p:
                parent = str(p.parent)
                spellings[parent.casefold()][parent] += 1
    canonical = {k: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for k, c in spellings.items()}

    for kind, e in entries:
        name = str(e["Name"])
        exe = ds.individual(iri("executable", name), D3F.ExecutableFile, name)
        ds.text(exe, MKND["operating-system"], "Windows")
        ds.text(exe, MKND.extType, kind)
        ds.text(exe, D3F.description, e.get("Description"))

        for fp in e.get("Full_Path") or []:
            p = full_path(fp)
            if not p:
                continue
            parent = str(p.parent)
            canon = canonical[parent.casefold()]
            d = ds.individual(iri("directory", canon), D3F.Directory, canon)
            if parent != canon:
                ds.g.add((d, SKOS.altLabel, Literal(parent)))
            f = ds.individual(iri("file", parent, p.name), D3F.File, p.name)
            ds.link(d, D3F.contains, f, inverse=D3F["contained-by"])
            ds.link(f, D3F.contains, exe, inverse=D3F["contained-by"])

        commands = []
        for c in e.get("Commands") or []:
            text = str(c["Command"])
            cmd = ds.individual(iri("command", text), D3F.Command, text)
            commands.append(cmd)
            ds.text(cmd, MKND.id, text)
            ds.text(cmd, D3F.description, c.get("Description"))
            ds.text(cmd, MKND["use-case"], c.get("Usecase"))
            ds.text(cmd, MKND.extCategory, c.get("Category"))
            ds.text(cmd, MKND["required-privileges"], c.get("Privileges"))
            ds.text(cmd, MKND["operating-system"], c.get("OperatingSystem") or "Windows")
            ds.link(cmd, D3F.uses, exe, inverse=D3F["used-by"])
            for tid in str(c.get("MitreID") or "").split(","):
                if tid.strip():
                    ds.link(cmd, D3F.enables, ds.technique(techniques, tid))

        # Detections are given per binary; they may detect any of its commands.
        for det in e.get("Detection") or []:
            for kind_, url in (det or {}).items():
                url = str(url).strip()
                if not url.startswith(("http://", "https://")):
                    continue  # free-text IOCs are not modelled
                d = ds.individual(MKND["detect_" + quote(f"{kind_}-{url}", safe="!'*")], D3F.Detect, url)
                ds.text(d, MKND.extType, kind_)
                for cmd in commands:
                    ds.link(d, D3F["may-detect"], cmd, inverse=D3F["may-be-detected-by"])


def full_path(fp):
    """PureWindowsPath for a Full_Path entry, None for placeholders like 'no default'."""
    p = str((fp or {}).get("Path") or "").strip()
    return PureWindowsPath(p) if "\\" in p else None


# ---------------------------------------------------------------------------- main
def core_metadata(core_ttl):
    text = Path(core_ttl).read_text(encoding="utf-8")
    version = re.search(r'owl:versionInfo "([^"]+)"', text).group(1)
    modified = re.search(r'dcterms:modified "([^"]+)"', text).group(1)
    return version, modified


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datasets", nargs="*", default=sorted(DATASETS), choices=sorted(DATASETS))
    ap.add_argument("--d3fend", required=True, help="pinned D3FEND release (Turtle)")
    ap.add_argument("--core", default=ROOT / "src/mknd.ttl")
    ap.add_argument("--sources", default=ROOT / "scripts/data/sources.json")
    ap.add_argument("--cache", default=ROOT / "build/upstream", type=Path)
    ap.add_argument("--out", default=ROOT / "data", type=Path)
    args = ap.parse_args()

    sources = json.loads(Path(args.sources).read_text())
    core = core_metadata(args.core)
    techniques = Techniques(args.d3fend)
    for name in args.datasets:
        ds = Dataset(name, sources[name], core)
        {"gtfobins": gtfobins, "lolbas": lolbas}[name](fetch(sources[name], args.cache), ds, techniques)
        ds.write(args.out / f"{name}.ttl")


if __name__ == "__main__":
    main()
