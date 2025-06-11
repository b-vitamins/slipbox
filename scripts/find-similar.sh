#!/bin/bash
set -euo pipefail

NODE_ID="${1:-}"

if [ -z "$NODE_ID" ]; then
    echo "Usage: $0 <node-id>"
    exit 1
fi

emacs --batch -l scripts/init-org-roam.el --eval "
(let* ((node (org-roam-node-from-id \"${NODE_ID}\"))
       (node-links (when node
                    (org-roam-db-query
                     [:select [dest]
                      :from links
                      :where (= source $s1)]
                     \"${NODE_ID}\")))
       (similar-nodes '()))
  (when node-links
    (dolist (link node-links)
      (let ((shared (org-roam-db-query
                     [:select [source]
                      :from links
                      :where (and (= dest $s1)
                                 (!= source $s2))]
                     (car link) \"${NODE_ID}\")))
        (dolist (s shared)
          (push (car s) similar-nodes))))
    (let ((freq (make-hash-table :test 'equal)))
      (dolist (n similar-nodes)
        (puthash n (1+ (gethash n freq 0)) freq))
      (message "=== Nodes similar to: %s ===" (org-roam-node-title node))
      (let ((sorted (sort (hash-table-keys freq)
                          (lambda (a b)
                            (> (gethash a freq) (gethash b freq))))))
        (dolist (similar-id (seq-take sorted 10))
          (let ((similar-node (org-roam-node-from-id similar-id)))
            (when similar-node
              (message "%d shared links | %s | %s"
                       (gethash similar-id freq)
                       similar-id
                       (org-roam-node-title similar-node))))))))
