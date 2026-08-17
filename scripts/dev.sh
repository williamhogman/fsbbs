#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=./env.sh
source "$ROOT/scripts/env.sh"

cd "$ROOT"
ensure_venv
ensure_redis
seed_redis

export PORT="${PORT:-8080}"
exec "$PY" -m fsbbs.http
