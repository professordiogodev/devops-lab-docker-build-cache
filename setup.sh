#!/usr/bin/env bash
# Clones Pollie and creates a 40 MB junk file (it stands for node_modules, datasets, build output ...). Run: ./setup.sh
set -u
cd "$(dirname "$0")"
for c in docker git; do command -v "$c" >/dev/null || { echo "MISSING: $c"; exit 1; }; done
docker info >/dev/null 2>&1 || { echo "Docker is not running."; exit 1; }
docker buildx version >/dev/null 2>&1 || { echo "The buildx plugin is missing (BuildKit needs it). Docker Desktop has it; on Linux install docker-buildx-plugin (or the docker-buildx package)."; exit 1; }
[ -d pollie ] || git clone -q -c advice.detachedHead=false --depth 1 --branch v0.1.1 https://github.com/professordiogodev/pollie.git pollie || { echo "could not clone pollie"; exit 1; }
mkdir -p data && [ -f data/sample.bin ] || head -c 40000000 /dev/urandom > data/sample.bin
echo "Ready. Measure the slow build:   ./measure.sh Dockerfile.slow"
