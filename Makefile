# MKND build. Same commands locally and in CI.
#
#   make test     seam, quality and reasoning checks (default)
#   make site     publishable site in build/site (docs + every serialization + versioned copy)
#   make drift D3FEND_NEXT=1.6.0   which D3FEND terms MKND uses that a newer release lacks
#   make data                      regenerate data/*.ttl from the upstream revisions in scripts/data/sources.json
#   make data-report               non-blocking quality report for data/*.ttl
#   make test-w3id                 check w3id/.htaccess redirects on a local Apache
#
# Needs: java 17+, python3, curl. Tools are downloaded into bin/ and .venv/.

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.DEFAULT_GOAL := test

# Single sources of truth: the MKND version lives in src/mknd.ttl, the D3FEND pin in the
# alignment's owl:imports.
VERSION        := $(shell sed -n 's/.*owl:versionInfo "\([^"]*\)".*/\1/p' src/mknd.ttl | head -1)
MODIFIED       := $(shell sed -n 's/.*dcterms:modified "\([^"]*\)".*/\1/p' src/mknd.ttl | head -1)
D3FEND_VERSION := $(shell grep -o 'd3fend/[0-9][^/]*/d3fend.owl' src/mknd-d3fend.ttl | cut -d/ -f2)
D3FEND_URL      = https://d3fend.mitre.org/ontologies/d3fend/$(1)/d3fend.ttl

ROBOT_VERSION  := 1.9.11
WIDOCO_VERSION := 1.4.26
JAVA_OPTS      ?= -Xmx6G
ROBOT_JAR      := bin/robot-$(ROBOT_VERSION).jar
WIDOCO_JAR     := bin/widoco-$(WIDOCO_VERSION).jar
ROBOT          := java $(JAVA_OPTS) -jar $(ROBOT_JAR)
CATALOG        := --catalog src/catalog-v001.xml
PY             := .venv/bin/python

D3FEND_TTL := build/imports/d3fend-$(D3FEND_VERSION).ttl
MODULES    := src/mknd.ttl src/mknd-d3fend.ttl
EXAMPLES   := examples/mknd-examples.ttl
DATA       := $(wildcard data/*.ttl)
SITE       := build/site
REPORTS    := build/reports

ASSERT_EMPTY := tests/assert-empty.sh

# ---------------------------------------------------------------------------- tools
$(ROBOT_JAR):
	mkdir -p bin
	curl -fsSL -o $@ https://github.com/ontodev/robot/releases/download/v$(ROBOT_VERSION)/robot.jar

$(WIDOCO_JAR):
	mkdir -p bin
	curl -fsSL -o $@ https://github.com/dgarijo/Widoco/releases/download/v$(WIDOCO_VERSION)/widoco-$(WIDOCO_VERSION)-jar-with-dependencies_JDK-17.jar

$(PY):
	python3 -m venv .venv
	.venv/bin/pip install -q rdflib==7.* pyyaml==6.*

build/imports/d3fend-%.ttl:
	mkdir -p $(@D)
	curl -fsSL -o $@ $(call D3FEND_URL,$*)

# pyyaml joined the venv for `make data`; add it to venvs made before that
.venv/.pyyaml: $(PY)
	.venv/bin/pip install -q pyyaml==6.*
	touch $@

.PHONY: tools imports
tools: $(ROBOT_JAR) $(WIDOCO_JAR) $(PY)
imports: $(D3FEND_TTL)

# ---------------------------------------------------------------------------- tests
.PHONY: test test-pins test-seam test-quality test-reason test-w3id
test: test-pins test-seam test-quality test-reason test-w3id

# the D3FEND pin and MKND version must agree everywhere they are written down
test-pins:
	@grep -q 'd3fend/$(D3FEND_VERSION)/d3fend.owl" uri="../build/imports/d3fend-$(D3FEND_VERSION).ttl"' src/catalog-v001.xml \
	  || { echo "FAIL src/catalog-v001.xml does not map D3FEND $(D3FEND_VERSION)"; exit 1; }
	@for f in $(MODULES) $(EXAMPLES) $(DATA); do \
	  grep -q 'owl:versionInfo "$(VERSION)"' $$f || { echo "FAIL $$f is not at version $(VERSION)"; exit 1; }; \
	done
	@echo "ok   pins: MKND $(VERSION), D3FEND $(D3FEND_VERSION)"

# Own-axiom queries run without --use-graphs, so only the module's own triples are seen.
test-seam: $(ROBOT_JAR) $(D3FEND_TTL)
	@mkdir -p $(REPORTS)
	@for f in src/mknd.ttl $(EXAMPLES); do \
	  out=$(REPORTS)/seam-subject-$$(basename $$f .ttl).tsv; \
	  $(ROBOT) query $(CATALOG) -i $$f --query tests/seam/third-party-subject.rq $$out; \
	  $(ASSERT_EMPTY) $$out "$$f says nothing about D3FEND terms"; \
	done
	@$(ROBOT) query $(CATALOG) --use-graphs true -i src/mknd-d3fend.ttl \
	  --query tests/seam/third-party-declaration.rq $(REPORTS)/seam-declaration.tsv
	@$(ROBOT) query $(CATALOG) -i src/mknd-d3fend.ttl \
	  --query tests/seam/alignment-scope.rq $(REPORTS)/seam-scope.tsv
	@$(ASSERT_EMPTY) $(REPORTS)/seam-declaration.tsv "alignment mints no D3FEND terms"
	@$(ASSERT_EMPTY) $(REPORTS)/seam-scope.tsv "alignment only talks about D3FEND terms"
	@$(ROBOT) query $(CATALOG) --use-graphs true -i $(EXAMPLES) \
	  --query tests/seam/undeclared-third-party-term.rq $(REPORTS)/seam-undeclared-d3f.tsv
	@$(ASSERT_EMPTY) $(REPORTS)/seam-undeclared-d3f.tsv "every D3FEND term used exists in D3FEND $(D3FEND_VERSION)"

QUALITY := undeclared-mknd-term property-type-clash class-used-as-value class-used-as-predicate \
           ontology-metadata duplicate-labels missing-label

# examples import core, which imports the alignment: one closure covers all three modules
test-quality: $(ROBOT_JAR) $(D3FEND_TTL)
	@mkdir -p $(REPORTS)
	@$(ROBOT) query $(CATALOG) --use-graphs true -i $(EXAMPLES) \
	  $(foreach q,$(QUALITY),--query tests/quality/$(q).rq $(REPORTS)/quality-$(q).tsv)
	@for q in $(QUALITY); do $(ASSERT_EMPTY) $(REPORTS)/quality-$$q.tsv $$q || fail=1; done; exit $${fail:-0}

# ELK: no unsatisfiable classes. HermiT: core + alignment + examples + D3FEND is consistent.
test-reason: $(ROBOT_JAR) $(D3FEND_TTL)
	@mkdir -p $(REPORTS)
	@$(ROBOT) merge $(CATALOG) -i $(EXAMPLES) \
	  reason --reasoner ELK --output build/reasoned.owl
	@echo "ok   ELK: no unsatisfiable classes"
	@$(ROBOT) explain $(CATALOG) -i $(EXAMPLES) --reasoner HermiT -M inconsistency \
	  --explanation $(REPORTS)/inconsistency.md
	@grep -q 'No explanations found' $(REPORTS)/inconsistency.md \
	  || { echo "FAIL HermiT: inconsistent"; cat $(REPORTS)/inconsistency.md; exit 1; }
	@echo "ok   HermiT: consistent"

# w3id.org redirect rules against a local Apache (skipped when httpd is not installed)
test-w3id:
	@tests/w3id/run.sh 2>&1 | grep -v AH00558

# ---------------------------------------------------------------------------- reports
.PHONY: drift data-report
D3FEND_NEXT ?= $(D3FEND_VERSION)
drift: $(ROBOT_JAR) build/imports/d3fend-$(D3FEND_NEXT).ttl
	@mkdir -p $(REPORTS)
	sed 's#../build/imports/d3fend-$(D3FEND_VERSION).ttl#../build/imports/d3fend-$(D3FEND_NEXT).ttl#' \
	  src/catalog-v001.xml > src/.catalog-drift.xml
	$(ROBOT) query --catalog src/.catalog-drift.xml --use-graphs true -i $(EXAMPLES) \
	  --query tests/seam/undeclared-third-party-term.rq $(REPORTS)/drift-$(D3FEND_NEXT).tsv
	rm src/.catalog-drift.xml
	@echo "D3FEND terms MKND uses that $(D3FEND_NEXT) lacks:"; cat $(REPORTS)/drift-$(D3FEND_NEXT).tsv

# ---------------------------------------------------------------------------- data
# data/*.ttl are generated: the upstream GTFOBins/LOLBAS revisions are pinned in
# scripts/data/sources.json and ATT&CK techniques resolve against the pinned D3FEND release.
# Downloads the upstream tarballs into build/upstream on first run (network needed).
.PHONY: data
data: .venv/.pyyaml $(D3FEND_TTL)
	$(PY) scripts/data/generate.py --d3fend $(D3FEND_TTL) --cache build/upstream --out data

# Non-blocking quality report for the generated data.
DATA_GRAPH_QUERIES := tests/quality/class-used-as-predicate.rq tests/quality/undeclared-mknd-term.rq \
                      tests/seam/undeclared-third-party-term.rq
data-report: $(ROBOT_JAR) $(D3FEND_TTL)
	@mkdir -p $(REPORTS)
	@for f in $(DATA); do n=$$(basename $$f .ttl); \
	  $(ROBOT) query $(CATALOG) -i $$f --query tests/seam/third-party-subject.rq \
	    $(REPORTS)/data-$$n-third-party-subject.tsv > /dev/null 2>&1; \
	  for q in $(DATA_GRAPH_QUERIES); do \
	    $(ROBOT) query $(CATALOG) --use-graphs true -i $$f --query $$q \
	      $(REPORTS)/data-$$n-$$(basename $$q .rq).tsv > /dev/null 2>&1; \
	  done; \
	  for r in $(REPORTS)/data-$$n-*.tsv; do $(ASSERT_EMPTY) $$r "$$(basename $$r .tsv)" --report; done; \
	done

# ---------------------------------------------------------------------------- site
.PHONY: site docs serializations
site: docs serializations
	rm -rf $(SITE)/icons $(SITE)/$(VERSION)
	cp -R assets/icons $(SITE)/icons
	mkdir -p $(SITE)/$(VERSION)
	cd $(SITE) && cp -R mknd.* alignment examples.* data $(VERSION)/
	touch $(SITE)/.nojekyll
	@echo "site: $(SITE) (MKND $(VERSION))"

serializations: $(PY)
	mkdir -p $(SITE)/alignment $(SITE)/data
	cp src/mknd.ttl $(SITE)/mknd.ttl
	cp src/mknd-d3fend.ttl $(SITE)/alignment/d3fend.ttl
	cp $(EXAMPLES) $(SITE)/examples.ttl
	cp $(DATA) $(SITE)/data/
	$(PY) scripts/serialize.py $(SITE)/mknd.ttl $(SITE)/alignment/d3fend.ttl $(SITE)/examples.ttl $(addprefix $(SITE)/data/,$(notdir $(DATA)))

docs: $(WIDOCO_JAR) $(PY)
	rm -rf build/doc
	mkdir -p build/doc $(SITE)
	$(PY) scripts/doc_input.py build/doc/mknd.ttl
	sed 's/@VERSION@/$(VERSION)/g; s/@D3FEND_VERSION@/$(D3FEND_VERSION)/g; s/@MODIFIED@/$(MODIFIED)/g' src/widoco.conf > build/doc/widoco.conf
	java $(JAVA_OPTS) -jar $(WIDOCO_JAR) -ontFile build/doc/mknd.ttl -outFolder build/doc/out \
	  -confFile build/doc/widoco.conf -rewriteAll -webVowl -uniteSections -lang en \
	  -includeAnnotationProperties -noPlaceHolderText
	$(PY) scripts/light_theme.py build/doc/out/doc
	cp -R build/doc/out/doc/. $(SITE)/
	cp $(SITE)/index-en.html $(SITE)/index.html
	rm -f $(SITE)/readme.md   # Widoco's own serializations are replaced by `serializations`

# ---------------------------------------------------------------------------- misc
.PHONY: clean print-version
print-version:
	@echo $(VERSION)

clean:
	rm -rf build
