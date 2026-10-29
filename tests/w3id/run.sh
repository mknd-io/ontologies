#!/usr/bin/env bash
# Exercise w3id/.htaccess on a throwaway local Apache, the way w3id.org serves it.
# usage: tests/w3id/run.sh          (needs Apache httpd with mod_rewrite)
set -euo pipefail
cd "$(dirname "$0")/../.."

HTTPD=$(command -v httpd || command -v apache2 || true)
[[ -n "$HTTPD" ]] || { echo "skip: no httpd"; exit 0; }
for d in /usr/libexec/apache2 /usr/lib/apache2/modules /usr/lib64/httpd/modules /opt/homebrew/lib/httpd/modules; do
  [[ -f "$d/mod_rewrite.so" ]] && MODS=$d && break
done
[[ -n "${MODS:-}" ]] || { echo "skip: mod_rewrite not found"; exit 0; }

ROOT=$(mktemp -d)
trap 'kill $(cat "$ROOT/httpd.pid" 2>/dev/null) 2>/dev/null || true; rm -rf "$ROOT"' EXIT
mkdir -p "$ROOT/docs/mknd"
cp w3id/.htaccess "$ROOT/docs/mknd/.htaccess"
PORT=${PORT:-18080}
# Load what this build doesn't have compiled in (Ubuntu builds in unixd, authz_core, ...).
BUILTIN=$("$HTTPD" -l)
load_modules() {
  for m in mpm_prefork authz_core unixd dir rewrite env; do
    grep -q "mod_$m.c" <<<"$BUILTIN" || echo "LoadModule ${m}_module $MODS/mod_$m.so"
  done
}
cat > "$ROOT/httpd.conf" <<EOF
ServerRoot "$ROOT"
ServerName localhost
Listen 127.0.0.1:$PORT
PidFile "$ROOT/httpd.pid"
ErrorLog "$ROOT/error.log"
$(load_modules)
DocumentRoot "$ROOT/docs"
<Directory "$ROOT/docs">
  AllowOverride All
  Require all granted
</Directory>
EOF
"$HTTPD" -f "$ROOT/httpd.conf" -k start
sleep 1

S=https://mknd-io.github.io/ontologies
fail=0
check() {  # path accept expected-location
  got=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -H "Accept: $2" "http://127.0.0.1:$PORT/mknd/$1")
  if [[ "$got" == "303 $3" ]]; then echo "ok   /mknd/$1 [$2]"; else echo "FAIL /mknd/$1 [$2] -> $got (want 303 $3)"; fail=1; fi
}
HTML='text/html,application/xhtml+xml,*/*;q=0.8'
RDFLIB='text/turtle, application/rdf+xml;q=0.9, application/ld+json;q=0.8'

check ""                     "$HTML"               "$S/"
check ""                     "text/turtle"         "$S/mknd.ttl"
check ""                     "application/rdf+xml" "$S/mknd.owl"
check ""                     "$RDFLIB"             "$S/mknd.ttl"
check "0.4.0/"               "application/ld+json" "$S/0.4.0/mknd.jsonld"
check "0.4.0/"               "$HTML"               "$S/"
check "Malware"              "$HTML"               "$S/#Malware"
check "Malware"              "application/n-triples" "$S/mknd.nt"
check "alignment/d3fend"     "$HTML"               "$S/alignment/d3fend.ttl"
check "alignment/d3fend/0.4.0" "application/rdf+xml" "$S/0.4.0/alignment/d3fend.owl"
check "examples"             "text/turtle"         "$S/examples.ttl"
check "data/lolbas"          "application/ld+json" "$S/data/lolbas.jsonld"
check "data/gtfobins/0.4.0"  "$HTML"               "$S/0.4.0/data/gtfobins.ttl"
exit $fail
