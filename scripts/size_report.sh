#!/usr/bin/env bash
set -euo pipefail

BUILD_DIR="$1"
OUTPUT_DIR="$2"
mkdir -p "$OUTPUT_DIR"

SANDBOX_WASM=$(find "$BUILD_DIR" -maxdepth 3 -name "*.wasm" -print -quit)
SANDBOX_BIN=$(find "$BUILD_DIR" -maxdepth 3 -name "nt_sandbox" -o -name "nt_sandbox.exe" -print -quit)

REPORT="$OUTPUT_DIR/size-report.txt"
{
    echo "Size Report"
    echo "============"
    if [[ -n "$SANDBOX_WASM" ]]; then
        echo "wasm: $(stat -c%s "$SANDBOX_WASM") bytes - $SANDBOX_WASM"
    else
        echo "wasm: not generated"
    fi
    if [[ -n "$SANDBOX_BIN" ]]; then
        if command -v stat >/dev/null 2>&1; then
            echo "binary: $(stat -c%s "$SANDBOX_BIN") bytes - $SANDBOX_BIN"
        fi
    else
        echo "binary: not generated"
    fi
} > "$REPORT"

echo "size report written to $REPORT"
