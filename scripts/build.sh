#!/usr/bin/env bash
# Produces a static snapshot of the running forum into dist/.
# fsbbs is a dynamic app, so the "build" boots the server against a
# throwaway redis instance and crawls the public pages.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=./env.sh
source "$ROOT/scripts/env.sh"

cd "$ROOT"
ensure_venv

export REDIS_PORT="${BUILD_REDIS_PORT:-6399}"
export REDIS_EPHEMERAL=1
PORT="${BUILD_PORT:-8099}"
export PORT

ensure_redis
seed_redis

"$PY" -m fsbbs.http > "$ROOT/.venv/build-server.log" 2>&1 &
SERVER_PID=$!
cleanup() { kill "$SERVER_PID" 2>/dev/null || true; }
trap cleanup EXIT

base="http://127.0.0.1:$PORT"
for _ in $(seq 1 40); do
    curl -sf -o /dev/null "$base/index.html" && break
    sleep 0.5
done
if ! curl -sf -o /dev/null "$base/index.html"; then
    echo "fsbbs server did not come up" >&2
    cat "$ROOT/.venv/build-server.log" >&2
    exit 1
fi

rm -rf "$ROOT/dist"
mkdir -p "$ROOT/dist/t"

fetch() { # fetch <url path> <output path>
    curl -sf "$base$1" -o "$ROOT/dist/$2"
    echo "  $1 -> dist/$2"
}

echo "Crawling pages"
fetch /index.html index.html
fetch /index.json index.json
fetch /login.html login.html
fetch /register.html register.html

# every thing that has a page of its own
tids="$("$(redis_cli)" -p "$REDIS_PORT" --scan --pattern 'thing:*:type' | sed -E 's/thing:([0-9]+):type/\1/' | sort -n)"
for tid in $tids; do
    fetch "/t/$tid.html" "t/$tid.html"
done

echo "Copying assets"
mkdir -p "$ROOT/dist/s" "$ROOT/dist/j"
cp -R "$ROOT/themes/default/static/." "$ROOT/dist/s/"
cp -R "$ROOT/javascript/." "$ROOT/dist/j/"

echo "Static build written to dist/"
