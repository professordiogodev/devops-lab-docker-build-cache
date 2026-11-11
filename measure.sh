#!/usr/bin/env bash
# Measures a Dockerfile: a cold build, an unchanged rebuild, a rebuild after a ONE-LINE source change,
# and a rebuild after a change to requirements.txt.   Usage: ./measure.sh Dockerfile.slow
set -u
cd "$(dirname "$0")"
DF=${1:-Dockerfile.fast}; TAG=cache-lab:$(echo "$DF" | tr 'A-Z.' 'a-z-' | tr -cd 'a-z0-9-')
[ -d pollie ] || { echo "Run ./setup.sh first."; exit 1; }
b() { # label
  local s=$(date +%s); DOCKER_BUILDKIT=1 docker build --progress=plain -f "$DF" -t "$TAG" . > /tmp/cache-lab-build.log 2>&1; local rc=$?; local e=$(date +%s)
  printf '%-34s %4ss   cached steps: %s   context: %s\n' "$1" $((e-s)) "$(grep -c ' CACHED' /tmp/cache-lab-build.log)" "$(grep 'transferring context' /tmp/cache-lab-build.log | sort -t: -k2 | grep -oE '[0-9.]+ ?[kKMG]?B' | sort -h | tail -1)"
  return $rc
}
docker builder prune -af >/dev/null 2>&1
echo "== $DF"
b "1. cold build" || { tail -20 /tmp/cache-lab-build.log; exit 1; }
b "2. rebuild, nothing changed"
echo "# touched $(date +%s)" >> pollie/pollie/api/main.py
b "3. one line of Python changed"
echo "# touched $(date +%s)" >> pollie/requirements.txt
b "4. requirements.txt changed"
git -C pollie checkout -q -- pollie/api/main.py requirements.txt 2>/dev/null
