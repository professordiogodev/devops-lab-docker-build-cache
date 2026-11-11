#!/usr/bin/env bash
# Builds your Dockerfile several times and measures the cache. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
[ -d pollie ] || { echo "Run ./setup.sh first." >&2; exit 1; }
exec python3 .lab/cachecheck.py
