#!/bin/bash
set -euo pipefail

NODE_ID="${1:-}"
SECTION="${2:-}"

if [ -z "$NODE_ID" ]; then
    echo "Usage: $0 <node-id> [section-marker]"
    exit 1
fi

emacs --batch -l scripts/init-org-roam.el --eval "
(let* ((node (org-roam-node-from-id \"${NODE_ID}\"))
       (file (when node (org-roam-node-file node))))
  (if file
      (message \"Splitting node: %s\" (org-roam-node-title node))
    (message \"Error: Node not found: ${NODE_ID}\")))"

echo "Note: Manual splitting recommended for complex nodes."
echo "This script identifies split points. Use create-node.sh to create new nodes."
