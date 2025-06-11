#!/bin/bash
set -euo pipefail

START="${1:-}"
END="${2:-}"

if [ -z "$START" ] || [ -z "$END" ]; then
    echo "Usage: $0 <start-topic> <end-topic>"
    exit 1
fi

echo "=== Creating Learning Path ==="
echo "From: $START"
echo "To: $END"
echo ""
echo "Searching for connections..."

./scripts/find-node.sh "$START"
echo "---"
./scripts/find-node.sh "$END"

echo ""
echo "Suggested approach:"
echo "1. Identify prerequisite concepts"
echo "2. Create index node for the learning path"
echo "3. Order concepts from basic to advanced"
echo "4. Link each step to the next"
