#!/usr/bin/env bash
# End-to-end PASS/FAIL gate for fsbbs.
# Boots a throwaway redis + server, walks the whole user flow and asserts on it.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=./env.sh
source "$ROOT/scripts/env.sh"

cd "$ROOT"
ensure_venv

export REDIS_PORT="${SMOKE_REDIS_PORT:-6398}"
export REDIS_EPHEMERAL=1
PORT="${SMOKE_PORT:-8098}"
export PORT
base="http://127.0.0.1:$PORT"

ensure_redis
seed_redis >/dev/null

LOG="$ROOT/.venv/smoke-server.log"
"$PY" -m fsbbs.http > "$LOG" 2>&1 &
SERVER_PID=$!
cleanup() {
    kill "$SERVER_PID" 2>/dev/null || true
    "$(redis_cli)" -p "$REDIS_PORT" shutdown nosave >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in $(seq 1 40); do
    curl -sf -o /dev/null "$base/index.html" && break
    sleep 0.5
done

pass=0; fail=0
ok()   { pass=$((pass+1)); printf 'PASS  %s\n' "$1"; }
bad()  { fail=$((fail+1)); printf 'FAIL  %s\n' "$1"; }
check() { # check <name> <expected> <actual>
    if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (expected '$2' got '$3')"; fi
}
contains() { # contains <name> <needle> <haystack>
    case "$3" in *"$2"*) ok "$1";; *) bad "$1 (missing '$2')";; esac
}
status() { curl -s -o /dev/null -w '%{http_code}' "$@"; }

# --- server is up -----------------------------------------------------------
check "server serves front page" 200 "$(status "$base/index.html")"
check "root serves front page"   200 "$(status "$base/")"
contains "front page renders seeded forum" "fsbbs" "$(curl -s "$base/index.html")"
check "seeded topic page renders" 200 "$(status "$base/t/3.html")"
check "unknown thing 404s" 404 "$(status "$base/t/999.html")"

# --- register ---------------------------------------------------------------
user="smoke$RANDOM$RANDOM"
jar="$(mktemp)"; jar2="$(mktemp)"
reg="$(curl -s -c "$jar" -d "username=$user" -d "password=hunter2" "$base/api/register.json")"
contains "register succeeds" '"status": "success"' "$reg"
grep -q $'\ts\t' "$jar" && ok "register sets session cookie" || bad "register sets session cookie"
secret="$(awk '$6=="s"{print $7}' "$jar")"

# --- session is bound and durable ------------------------------------------
ttl="$("$(redis_cli)" -p "$REDIS_PORT" ttl "session:$secret")"
if [ "$ttl" -gt 500000 ]; then ok "session has 7 day ttl ($ttl s)"; else bad "session ttl ($ttl)"; fi
boundip="$("$(redis_cli)" -p "$REDIS_PORT" get "session-ip:$secret")"
check "session bound to client ip" "127.0.0.1" "$boundip"

# --- create a topic and post ------------------------------------------------
check "new topic accepted" 302 "$(status -b "$jar" -d "tid=2" -d "title=smoke topic" -d "text=hello *world*" "$base/new_topic")"
newtid="$("$(redis_cli)" -p "$REDIS_PORT" get thing:next_tid)"
topic=$((newtid-1))
check "created topic renders" 200 "$(status "$base/t/$topic.html")"
contains "topic shows its title" "smoke topic" "$(curl -s "$base/t/$topic.html")"
contains "category lists new topic" "smoke topic" "$(curl -s "$base/t/2.html")"

check "new post accepted" 302 "$(status -b "$jar" -d "tid=$topic" -d "text=a reply from smoke" "$base/new_post")"
contains "post is rendered in topic" "a reply from smoke" "$(curl -s "$base/t/$topic.html")"

# --- anonymous writes are rejected -----------------------------------------
check "anonymous post rejected" 401 "$(status -d "tid=$topic" -d "text=nope" "$base/new_post")"
check "anonymous topic rejected" 401 "$(status -d "tid=2" -d "title=nope" -d "text=nope" "$base/new_topic")"

# --- session hijacking ------------------------------------------------------
"$(redis_cli)" -p "$REDIS_PORT" set "session-ip:$secret" "10.9.9.9" >/dev/null
check "hijacked session rejected" 401 "$(status -b "$jar" -d "tid=$topic" -d "text=hijack" "$base/new_post")"
"$(redis_cli)" -p "$REDIS_PORT" set "session-ip:$secret" "127.0.0.1" >/dev/null
check "owner still accepted after hijack attempt" 302 "$(status -b "$jar" -d "tid=$topic" -d "text=still me" "$base/new_post")"

# --- login / logout ---------------------------------------------------------
check "wrong password refused" '"status": "failure"' "$(curl -s -d "username=$user" -d "password=wrong" "$base/api/login.json" | tr -d '\n' | grep -o '"status": "[a-z]*"')"
curl -s -b "$jar" -X POST -o /dev/null "$base/api/logout.json"
check "logged out session is gone" "" "$("$(redis_cli)" -p "$REDIS_PORT" get "session:$secret")"
check "old cookie no longer posts" 401 "$(status -b "$jar" -d "tid=$topic" -d "text=after logout" "$base/new_post")"
login="$(curl -s -c "$jar2" -d "username=$user" -d "password=hunter2" "$base/api/login.json")"
contains "re-login succeeds" '"status": "success"' "$login"
check "re-login can post" 302 "$(status -b "$jar2" -d "tid=$topic" -d "text=back again" "$base/new_post")"

# --- durability -------------------------------------------------------------
"$(redis_cli)" -p "$REDIS_PORT" config set appendonly yes >/dev/null
"$(redis_cli)" -p "$REDIS_PORT" bgrewriteaof >/dev/null
for _ in $(seq 1 20); do
    [ "$("$(redis_cli)" -p "$REDIS_PORT" info persistence | tr -d '\r' | grep -c 'aof_rewrite_in_progress:0')" = "1" ] && break
    sleep 0.5
done
check "aof persistence enabled" "appendonly yes" "$("$(redis_cli)" -p "$REDIS_PORT" config get appendonly | tr '\n' ' ' | tr -d '\r' | sed 's/ $//')"

# --- api --------------------------------------------------------------------
contains "index json exposes forum" '"name"' "$(curl -s "$base/index.json")"
contains "thing json works" '"title"' "$(curl -s "$base/api/get_thing.json?id=$topic")"

rm -f "$jar" "$jar2"

echo
if grep -qiE 'traceback|unhandled error' "$LOG"; then
    fail=$((fail+1))
    echo "FAIL  server log is clean"
    tail -n 40 "$LOG"
else
    pass=$((pass+1)); echo "PASS  server log is clean"
fi

echo
echo "$pass passed, $fail failed"
if [ "$fail" -gt 0 ]; then
    echo "SMOKE: FAIL"
    exit 1
fi
echo "SMOKE: PASS"
