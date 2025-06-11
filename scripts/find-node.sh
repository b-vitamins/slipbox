#!/bin/bash
set -euo pipefail

QUERY="${1:-}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let ((nodes (org-roam-db-query 
              [:select [nodes:id nodes:title nodes:file]
               :from nodes
               :where (or (like nodes:title $r1)
                         (like nodes:file $r1))]
              (concat \"%\" \"${QUERY}\" \"%\"))))
  (if nodes
      (dolist (node nodes)
        (message \"%s | %s | %s\" 
                 (nth 0 node) 
                 (nth 1 node) 
                 (file-relative-name (nth 2 node) org-roam-directory)))
    (message \"No nodes found matching: ${QUERY}\")))"
