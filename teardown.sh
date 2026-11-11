#!/usr/bin/env bash
# Removes the lab's images, build cache and files. Run with: ./teardown.sh
set -u
cd "$(dirname "$0")"
docker images --format '{{.Repository}}:{{.Tag}}' | grep '^cache-lab:' | xargs -r docker image rm -f >/dev/null 2>&1 && echo "removed the images"
docker builder prune -af >/dev/null 2>&1 && echo "pruned the build cache"
rm -rf pollie data
echo "Now run ./verify-teardown.sh"
