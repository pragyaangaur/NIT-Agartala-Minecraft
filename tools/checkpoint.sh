#!/bin/bash
# Usage: tools/checkpoint.sh "note file"
set -e
cd "$(dirname "$0")/.."
CP="checkpoints/$(date -u +%Y-%m-%dT%H%MZ)"
mkdir -p "$CP"
cp out/NITAgartala_world.zip "$CP/"
cp out/renders/aerial_overview.png "$CP/"
cp BUILDINGS.csv "$CP/"
[ -n "$1" ] && cp "$1" "$CP/PROGRESS_NOTE.md"
echo "checkpoint -> $CP"
