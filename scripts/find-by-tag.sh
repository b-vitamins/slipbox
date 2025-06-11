#!/bin/bash
set -euo pipefail

TAG="${1:-}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let ((nodes (org-roam-db-query 
              [:select [nodes:id nodes:title nodes:file tags:tag]
               :from nodes
               :left-join tags
               :on (= nodes:id tags:node-id)
               :where (like tags:tag $r1)]
              (concat \"%\" \"${TAG}\" \"%\"))))
  (if nodes
      (dolist (node nodes)
        (message \"%s | %s | %s | %s\"
                 (nth 0 node)
                 (nth 1 node)
                 (file-relative-name (nth 2 node) org-roam-directory)
                 (nth 3 node)))
    (message \"No nodes found with tag: ${TAG}\")))"
