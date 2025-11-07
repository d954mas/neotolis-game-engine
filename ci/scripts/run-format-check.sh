#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--all | file1 [file2 ...]]

Runs clang-format (C/C++) and cmake-format (CMake lists/modules) in --check
mode. Exits non-zero when formatting drift is detected.
USAGE
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 1
fi

root=$(git rev-parse --show-toplevel)
cd "$root"

collect_files() {
  local pattern=$1
  if [[ $# -gt 1 ]]; then
    shift
    printf '%s\n' "$@"
    return
  fi
  git ls-files -z | tr '\0' '\n' | grep -E "$pattern" || true
}

# Determine target files
if [[ $# -gt 0 && $1 != "--all" ]]; then
  mapfile -t TARGETS < <(printf '%s\n' "$@" | sed 's#^./##')
else
  mapfile -t TARGETS < <(git ls-files)
fi

if [[ ${1:-} == "--all" ]]; then
  TARGETS=( $(git ls-files) )
fi

clang_files=()
cmake_files=()
for f in "${TARGETS[@]}"; do
  [[ -n $f ]] || continue
  case "$f" in
    *.c|*.h|*.cpp|*.hpp)
      clang_files+=("$f") ;;
    *.cmake|CMakeLists.txt)
      cmake_files+=("$f") ;;
  esac
done

if [[ ${#clang_files[@]} -eq 0 && ${#cmake_files[@]} -eq 0 ]]; then
  echo "run-format-check: nothing to check" >&2
  exit 0
fi

if [[ ${#clang_files[@]} -gt 0 ]]; then
  if ! command -v clang-format >/dev/null 2>&1; then
    echo "clang-format not found" >&2
    exit 1
  fi
  echo "[format] Checking ${#clang_files[@]} C/C++ files"
  clang-format --dry-run -Werror "${clang_files[@]}"
fi

if [[ ${#cmake_files[@]} -gt 0 ]]; then
  if ! command -v cmake-format >/dev/null 2>&1; then
    echo "cmake-format not found" >&2
    exit 1
  fi
  echo "[format] Checking ${#cmake_files[@]} CMake files"
  cmake-format --check "${cmake_files[@]}"
fi

echo "[format] All files look good"
