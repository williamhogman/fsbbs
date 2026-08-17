#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=./env.sh
source "$ROOT/scripts/env.sh"

ensure_venv
redis_bin >/dev/null
echo "fsbbs environment ready"
