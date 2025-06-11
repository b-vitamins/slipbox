#!/bin/bash
set -euo pipefail

echo "=== Starting Weekly Maintenance ==="
echo ""

# Archive old fleeting notes
echo "1. Archiving fleeting notes older than 30 days..."
OLD_COUNT=$(find notes/fleeting -name "*.org" -mtime +30 2>/dev/null | wc -l || echo 0)
if [ "$OLD_COUNT" -gt 0 ]; then
    find notes/fleeting -name "*.org" -mtime +30 -exec mv {} notes/archive/ \;
    echo "   Archived $OLD_COUNT old fleeting notes"
else
    echo "   No old fleeting notes to archive"
fi
echo ""

# Find orphaned nodes
echo "2. Checking for orphaned nodes..."
./scripts/find-orphans.sh
echo ""

# Database sync
echo "3. Syncing database..."
./scripts/sync-db.sh
echo ""

# Show statistics
echo "4. Repository statistics:"
./scripts/show-stats.sh
echo ""

echo "=== Weekly Maintenance Complete ==="
