#!/bin/bash
set -euo pipefail

NODE_ID="${1:-}"

if [ -z "$NODE_ID" ]; then
    echo "Usage: $0 <node-id>"
    exit 1
fi

# Get file path from node ID
FILE=$(emacs --batch -l scripts/init-org-roam.el --eval "
(let* ((node (org-roam-node-from-id \"${NODE_ID}\"))
       (file (when node (org-roam-node-file node))))
  (when file (princ file)))" 2>/dev/null)

if [ -n "$FILE" ] && [ -f "$FILE" ]; then
    echo "=== LaTeX Lint Report for: $(basename "$FILE") ==="
    
    # Extract LaTeX content and check with chktex
    grep -E "^\$\$|\\\\\[|#\+BEGIN_EXPORT latex" "$FILE" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "Checking for common LaTeX issues..."
        awk '/\$\$/{count++} END{if(count%2!=0) print "Warning: Unmatched $$ delimiters"}' "$FILE"
        grep -n '\.[A-Za-z]' "$FILE" | grep -E '\$.*\$' | sed 's/^/Line /' | sed 's/:/ - Warning: Missing space after period in math mode: /'
        if command -v chktex >/dev/null 2>&1; then
            echo ""
            echo "Running chktex..."
            chktex -q "$FILE" 2>/dev/null || true
        else
            echo "Note: Install chktex for more comprehensive LaTeX checking"
        fi
    else
        echo "No LaTeX content found in file"
    fi
else
    echo "Error: Could not find file for node ID: ${NODE_ID}"
fi
