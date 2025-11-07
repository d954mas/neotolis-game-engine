#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") --command-file <path> --required "flag1;flag2;..."

Scans a linker command log (e.g., Ninja link.txt) for the required guard flags and
fails when any flag is missing.
USAGE
}

COMMAND_FILE=""
REQUIRED_FLAGS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --command-file)
      COMMAND_FILE="$2"; shift 2 ;;
    --required)
      REQUIRED_FLAGS="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$COMMAND_FILE" || -z "$REQUIRED_FLAGS" ]]; then
  echo "Both --command-file and --required are mandatory" >&2
  usage
  exit 1
fi

if [[ ! -f "$COMMAND_FILE" ]]; then
  echo "Linker command file not found: $COMMAND_FILE" >&2
  exit 1
fi

content=$(<"$COMMAND_FILE")
missing=()
IFS=';' read -r -a flags <<< "$REQUIRED_FLAGS"
for flag in "${flags[@]}"; do
  [[ -z "$flag" ]] && continue
  if ! grep -F -- "$flag" <<< "$content" >/dev/null; then
    missing+=("$flag")
  fi
fi

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "Missing linker guard flags:" >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 1
fi

echo "All required linker guard flags found in ${COMMAND_FILE}" >&2
