#!/usr/bin/env bash
# usage: assert-empty.sh RESULT.tsv "what is being checked"
# Fails when a ROBOT query result (TSV with a header row) has any rows.
set -euo pipefail
rows=$(( $(wc -l < "$1") - 1 ))
if (( rows > 0 )); then
  echo "FAIL $2: $rows violation(s) — $1"
  head -20 "$1"
  exit 1
fi
echo "ok   $2"
