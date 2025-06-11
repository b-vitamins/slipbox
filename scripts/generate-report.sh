#!/bin/bash
set -euo pipefail

PERIOD="${1:-week}"
TYPE="${2:-progress}"

echo "=== Generating $TYPE report for past $PERIOD ==="
echo ""

case "$TYPE" in
    progress)
        echo "Recent activity:"
        find notes -name "*.org" -mtime -7 -type f | while read -r file; do
            echo "- Modified: $(basename "$file")"
        done
        echo ""
        ./scripts/show-stats.sh
        ;;
    links)
        echo "Link analysis:"
        ./scripts/find-orphans.sh
        ;;
    *)
        echo "Unknown report type: $TYPE"
        echo "Available types: progress, links"
        ;;
esac
