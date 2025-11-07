#!/usr/bin/env bash
set -euo pipefail

SRC=${1:-}
if [[ -z "$SRC" ]]; then
  echo "Usage: $(basename "$0") <source-file>" >&2
  exit 1
fi
if ! command -v clang-tidy >/dev/null 2>&1; then
  echo "clang-tidy is required but not found in PATH" >&2
  exit 1
fi

TMP_LOG=$(mktemp)
if clang-tidy "$SRC" --warnings-as-errors=* -- -std=c17 >"$TMP_LOG" 2>&1; then
  cat "$TMP_LOG"
  echo "Expected clang-tidy to report violations for $SRC" >&2
  rm -f "$TMP_LOG"
  exit 1
fi

cat "$TMP_LOG"
rm -f "$TMP_LOG"
exit 0
