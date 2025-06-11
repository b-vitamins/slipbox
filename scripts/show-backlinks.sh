#!/bin/bash
set -euo pipefail

NODE_ID="${1:-}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let* ((node (org-roam-node-from-id \"${NODE_ID}\"))
       (backlinks (when node 
                   (org-roam-db-query 
                    [:select [source dest]
                     :from links
                     :where (= dest $s1)]
                    \"${NODE_ID}\"))))
  (if backlinks
      (progn
        (message \"=== Backlinks to: %s ===\" (org-roam-node-title node))
        (dolist (link backlinks)
          (let ((source-node (org-roam-node-from-id (car link))))
            (when source-node
              (message \"%s | %s\"
                       (org-roam-node-id source-node)
                       (org-roam-node-title source-node))))))
    (message \"No backlinks found for node: ${NODE_ID}\")))"
