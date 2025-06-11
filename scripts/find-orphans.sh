#!/bin/bash
set -euo pipefail

emacs --batch -l scripts/init-org-roam.el --eval '
(let ((orphans (org-roam-db-query 
                [:select [nodes:file nodes:title]
                 :from nodes
                 :left-join links
                 :on (= nodes:id links:dest)
                 :where (is links:dest nil)])))
  (if orphans
      (progn
        (message "=== Orphaned Nodes (no backlinks) ===")
        (dolist (orphan orphans)
          (message "%s | %s" 
                   (file-relative-name (car orphan) org-roam-directory)
                   (cadr orphan))))
    (message "No orphaned nodes found.")))'
