#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/build-portal-preview.sh [options]

Options:
  --sandbox <path>         Path to sandbox artifact directory (default: testbeds/sandbox/out)
  --report <path>          Path to reports/size directory (default: reports/size)
  --preview-dir <path>     Preview destination (default: /tmp/portal-preview)
  --dist <path>            Packaged portal output (default: web/portal/dist)
  --commit <sha>           Commit hash for manifest metadata (default: current HEAD)
  --generated-at <iso>     ISO-8601 timestamp (default: current UTC time)
  --deployment-runtime <ms>  Deployment runtime in milliseconds for manifest metadata
  --ci                     Enable CI mode (enforces gzip budgets)
  -h, --help               Show this help message
EOF
}

stage_directory() {
    local source_dir="$1"
    local target_dir="$2"
    rm -rf "${target_dir}"
    mkdir -p "${target_dir}"
    cp -a "${source_dir}/." "${target_dir}/"
}

enforce_budgets() {
    local portal_dir="$1"
    local sandbox_dir="$2"
    local portal_size sandbox_size
    portal_size=$(gzip_size "${portal_dir}")
    sandbox_size=$(gzip_size "${sandbox_dir}")
    echo "Portal gzip size: ${portal_size} bytes (budget 153600)"
    echo "Sandbox gzip size: ${sandbox_size} bytes (budget 204800)"
    if (( portal_size > 153600 )); then
        echo "Portal bundle exceeds 150 KB gzip budget." >&2
        exit 1
    fi
    if (( sandbox_size > 204800 )); then
        echo "Sandbox bundle exceeds 200 KB gzip budget." >&2
        exit 1
    fi
}

gzip_size() {
    local target="$1"
    if [[ ! -e "${target}" ]]; then
        echo "0"
        return
    fi
    if [[ -d "${target}" ]]; then
        tar -C "${target}" -cf - . 2>/dev/null | gzip -c | wc -c
    else
        gzip -c "${target}" | wc -c
    fi
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
PORTAL_ROOT="${REPO_ROOT}/web/portal"
SANDBOX_PATH="${REPO_ROOT}/testbeds/sandbox/out"
REPORT_PATH="${REPO_ROOT}/reports/size"
PREVIEW_DIR="${PORTAL_PREVIEW_DIR:-/tmp/portal-preview}"
DIST_DIR="${PORTAL_DIST_DIR:-${PORTAL_ROOT}/dist}"
COMMIT_SHA="$(git -C "${REPO_ROOT}" rev-parse --short HEAD)"
GENERATED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
DEPLOYMENT_RUNTIME_MS=""
CI_MODE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --sandbox)
            SANDBOX_PATH="$(realpath "$2")"
            shift 2
            ;;
        --report)
            REPORT_PATH="$(realpath "$2")"
            shift 2
            ;;
        --preview-dir)
            PREVIEW_DIR="$(realpath -m "$2")"
            shift 2
            ;;
        --dist)
            DIST_DIR="$(realpath -m "$2")"
            shift 2
            ;;
        --commit)
            COMMIT_SHA="$2"
            shift 2
            ;;
        --generated-at)
            GENERATED_AT="$2"
            shift 2
            ;;
        --deployment-runtime)
            DEPLOYMENT_RUNTIME_MS="$2"
            shift 2
            ;;
        --ci)
            CI_MODE=1
            shift 1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

echo "Staging portal assets with sandbox=${SANDBOX_PATH} report=${REPORT_PATH}"

prepare_args=(
    --sandbox "${SANDBOX_PATH}"
    --report "${REPORT_PATH}"
    --output "${PORTAL_ROOT}"
    --commit "${COMMIT_SHA}"
    --generated-at "${GENERATED_AT}"
)

if [[ -n "${DEPLOYMENT_RUNTIME_MS}" ]]; then
    prepare_args+=(--deployment-runtime-ms "${DEPLOYMENT_RUNTIME_MS}")
fi

node "${REPO_ROOT}/scripts/portal/prepare-portal.js" "${prepare_args[@]}"

stage_directory "${PORTAL_ROOT}" "${PREVIEW_DIR}"
stage_directory "${PORTAL_ROOT}" "${DIST_DIR}"

if [[ "${CI_MODE}" -eq 1 ]]; then
    enforce_budgets "${DIST_DIR}" "${PORTAL_ROOT}/sandbox"
fi

echo "Portal preview ready at ${PREVIEW_DIR}/index.html"
echo "Packaged portal available at ${DIST_DIR}"
