#!/bin/bash
set -euo pipefail

echo "=== Org-Roam Health Check ==="
echo ""

# Check for required directories
echo "1. Checking directory structure..."
for dir in daily fleeting literature concept problem index attachments archive; do
    if [ -d "notes/$dir" ]; then
        echo "   ✓ notes/$dir exists"
    else
        echo "   ✗ notes/$dir missing - creating..."
        mkdir -p "notes/$dir"
    fi
done
echo ""

# Check for duplicate IDs
echo "2. Checking for duplicate IDs..."
ID_LIST=$(grep -r "^:ID:" notes | awk '{print $2}')
DUPES=$(echo "$ID_LIST" | sort | uniq -d)
if [ -n "$DUPES" ]; then
    for id in $DUPES; do
        echo "   ✗ Duplicate ID found: $id"
    done
else
    echo "   ✓ ID check complete"
fi
echo ""

# Check database
echo "3. Database status..."
if [ -f "notes/org-roam.db" ]; then
    SIZE=$(du -h "notes/org-roam.db" | cut -f1)
    echo "   ✓ Database exists (size: $SIZE)"
else
    echo "   ! Database missing - run sync-db.sh"
fi
echo ""

# Check for orphaned files
echo "4. Checking for orphaned files..."
if command -v emacs >/dev/null 2>&1 && emacs --batch --eval "(if (require 'org-roam nil t) (kill-emacs 0) (kill-emacs 1))" >/dev/null 2>&1; then
    ./scripts/find-orphans.sh | head -5
else
    echo "   ! org-roam not available; skipping orphan check"
fi
echo ""

echo "=== Health Check Complete ==="
