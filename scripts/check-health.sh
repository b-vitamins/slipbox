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
emacs --batch -l scripts/init-org-roam.el --eval '
(let ((ids (org-roam-db-query [:select [id] :from nodes]))
      (seen (make-hash-table :test equal)))
  (dolist (id-row ids)
    (let ((id (car id-row)))
      (if (gethash id seen)
          (message "   ✗ Duplicate ID found: %s" id)
        (puthash id t seen))))
  (message "   ✓ ID check complete"))'
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
./scripts/find-orphans.sh | head -5
echo ""

echo "=== Health Check Complete ==="
