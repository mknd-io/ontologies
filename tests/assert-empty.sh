#!/usr/bin/env bash
# usage: assert-empty.sh RESULT.tsv "what is being checked" [--report]
# ROBOT writes a header plus one line per row, or an empty file when nothing matched.
# Fails when the result has rows, unless --report is given (then it only prints the count).
set -euo pipefail
[[ -f "$1" ]] || { echo "FAIL $2: missing result $1"; exit 1; }
rows=0
[[ -s "$1" ]] && rows=$(( $(wc -l < "$1") - 1 ))
if [[ "${3:-}" == --report ]]; then
  printf '%6d  %s\n' "$rows" "$2"
elif (( rows > 0 )); then
  echo "FAIL $2: $rows violation(s) — $1"
  head -20 "$1"
  exit 1
else
  echo "ok   $2"
fi
