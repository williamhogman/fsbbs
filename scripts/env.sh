#!/usr/bin/env bash
# shared helpers: python venv + redis server resolution
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

py_deps=(twisted redis jinja2 markdown msgpack six pyopenssl service_identity)
py_nodeps=(cyclone txredisapi)

ensure_venv() {
    if [ ! -x "$PY" ]; then
        python3 -m venv "$VENV"
    fi
    if [ ! -f "$VENV/.deps-ok" ]; then
        "$PIP" install --quiet "${py_deps[@]}"
        # cyclone/txredisapi pin ancient twisted versions that no longer build,
        # their runtime works fine against modern twisted.
        "$PIP" install --quiet --no-deps "${py_nodeps[@]}"
        touch "$VENV/.deps-ok"
    fi
}

redis_bin() {
    if command -v redis-server >/dev/null 2>&1; then
        command -v redis-server
        return
    fi
    local cache="$ROOT/.venv/.redis-path"
    if [ ! -s "$cache" ]; then
        nix build --no-link --print-out-paths nixpkgs#redis > "$cache"
    fi
    echo "$(cat "$cache")/bin/redis-server"
}

redis_cli() {
    local server
    server="$(redis_bin)"
    echo "${server%redis-server}redis-cli"
}

ensure_redis() {
    local port="${REDIS_PORT:-6379}"
    if "$(redis_cli)" -p "$port" ping >/dev/null 2>&1; then
        return
    fi
    # one data dir per port so throwaway instances (build/smoke) never touch
    # the durable dev dataset
    local dir="$ROOT/.venv/redis-$port"
    # REDIS_EPHEMERAL=1 disables persistence entirely (build/smoke runs)
    local persist=(--appendonly yes --appendfsync everysec --save '900 1')
    if [ "${REDIS_EPHEMERAL:-0}" = "1" ]; then
        rm -rf "$dir"
        persist=(--appendonly no --save '')
    fi
    mkdir -p "$dir"
    "$(redis_bin)" --port "$port" --daemonize yes \
        --dir "$dir" "${persist[@]}" \
        --logfile "$dir/redis.log"
    for _ in $(seq 1 30); do
        "$(redis_cli)" -p "$port" ping >/dev/null 2>&1 && return
        sleep 0.5
    done
    echo "redis failed to start" >&2
    exit 1
}


seed_redis() {
    local port="${REDIS_PORT:-6379}"
    "$PY" "$ROOT/scripts/seed.py" "$port"
}
