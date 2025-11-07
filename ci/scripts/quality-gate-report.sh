#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") --preset <preset> --workflow <workflow> --output <path> --build-dir <dir>

Collects compiler/linker/memory instrumentation metadata and emits a quality-gate report
conforming to ci/schemas/quality-gate-report.schema.json. Metrics are currently
placeholders; later phases will replace them with real data sources.
USAGE
}

PRESET=""
WORKFLOW=""
OUTPUT=""
BUILD_DIR=""
ARTIFACT_VERSION="0.2.0"
WARNINGS_AS_ERRORS="true"
LINKER_STATUS="pass"
THIRD_PARTY_RAW=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --preset)
      PRESET="$2"; shift 2 ;;
    --workflow)
      WORKFLOW="$2"; shift 2 ;;
    --output)
      OUTPUT="$2"; shift 2 ;;
    --build-dir)
      BUILD_DIR="$2"; shift 2 ;;
    --warnings-as-errors)
      WARNINGS_AS_ERRORS="$2"; shift 2 ;;
    --linker-status)
      LINKER_STATUS="$2"; shift 2 ;;
    --third-party)
      THIRD_PARTY_RAW+=("$2"); shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$PRESET" || -z "$WORKFLOW" || -z "$OUTPUT" || -z "$BUILD_DIR" ]]; then
  echo "preset, workflow, output, and build-dir are required" >&2
  usage
  exit 1
fi

CACHE_FILE="$BUILD_DIR/CMakeCache.txt"
if [[ ! -f "$CACHE_FILE" ]]; then
  echo "CMakeCache not found at $CACHE_FILE" >&2
  exit 1
fi

read_cache_list() {
  local key="$1"
  local line
  line=$(grep -E "^${key}:.*=" "$CACHE_FILE" || true)
  [[ -z "$line" ]] && echo "" && return
  echo "${line#*=}"
}

IFS=';' read -r -a COMPILER_FLAGS_ARR <<< "$(read_cache_list NT_FAILFAST_WARNING_FLAGS)"
IFS=';' read -r -a LINKER_FLAGS_ARR <<< "$(read_cache_list NT_FAILFAST_LINK_FLAGS)"

THIRD_PARTY_JSON_ENTRIES=()
for entry in "${THIRD_PARTY_RAW[@]}"; do
  IFS=':' read -r path reason <<< "$entry"
  [[ -z "$path" ]] && continue
  [[ -z "$reason" ]] && reason="Third-party dependency"
  THIRD_PARTY_JSON_ENTRIES+=("{\"path\":\"$path\",\"reason\":\"$reason\"}")
fi

json_array_from_strings() {
  local first=1
  printf '['
  for item in "$@"; do
    [[ -z "$item" ]] && continue
    if [[ $first -eq 0 ]]; then
      printf ','
    fi
    printf '"%s"' "$item"
    first=0
  done
  printf ']'
}

compiler_flags_json=$(json_array_from_strings "${COMPILER_FLAGS_ARR[@]}")
linker_flags_json=$(json_array_from_strings "${LINKER_FLAGS_ARR[@]}")
third_party_json="["
for idx in "${!THIRD_PARTY_JSON_ENTRIES[@]}"; do
  [[ $idx -ne 0 ]] && third_party_json+="," 
  third_party_json+="${THIRD_PARTY_JSON_ENTRIES[$idx]}"
done
third_party_json+="]"

overall_status="pass"
if [[ "$LINKER_STATUS" != "pass" ]]; then
  overall_status="fail"
fi

mkdir -p "$(dirname "$OUTPUT")"

now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
commit_sha=$(git rev-parse HEAD 2>/dev/null || echo "0000000")
build_url=${CI_JOB_URL:-"https://ci.example.local/job/unknown"}

cat <<JSON > "$OUTPUT"
{
  "preset": "$PRESET",
  "workflow": "$WORKFLOW",
  "artifact_version": "$ARTIFACT_VERSION",
  "metadata": {
    "commit": "${commit_sha}",
    "timestamp": "${now_iso}",
    "build_url": "${build_url}"
  },
  "status": "${overall_status}",
  "compiler_flags": {
    "warnings_as_errors": ${WARNINGS_AS_ERRORS},
    "flags": ${compiler_flags_json},
    "violations": []
  },
  "linker_guards": {
    "flags": ${linker_flags_json},
    "stack_protector": true,
    "status": "${LINKER_STATUS}",
    "notes": ""
  },
  "third_party_whitelist": {
    "entries": ${third_party_json}
  },
  "sanitizer_matrix": {
    "enabled": false,
    "components": [],
    "coverage_pct": 0
  },
  "static_analysis": {
    "violations": 0,
    "new_violations": 0,
    "status": "fail"
  },
  "formatting": {
    "drift_files": 0,
    "status": "fail"
  },
  "binary_budget": {
    "wasm_delta_kb": 0,
    "native_delta_kb": 0,
    "status": "fail"
  },
  "memory_policy": {
    "ram_peak_bytes": 0,
    "shadow_bytes": 0,
    "status": "fail"
  },
  "microbench": {
    "median_ms": 0,
    "regression_pct": 0,
    "status": "fail"
  },
  "security_review_hours": {
    "current": 0,
    "baseline": 10,
    "status": "fail",
    "history": []
  }
}
JSON

echo "[quality-gate-report] Created placeholder report at $OUTPUT" >&2
