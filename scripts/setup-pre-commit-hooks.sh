#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
HOOKS_DIR="$ROOT_DIR/.git/hooks"

cat > "$HOOKS_DIR/pre-commit" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail

clang-format --dry-run --Werror $(git ls-files '*.c' '*.h')
HOOK

chmod +x "$HOOKS_DIR/pre-commit"

echo "Installed clang-format pre-commit hook"
