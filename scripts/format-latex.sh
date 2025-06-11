#!/bin/bash
set -euo pipefail

NODE_ID="${1:-}"

if [ -z "$NODE_ID" ]; then
    echo "Usage: $0 <node-id>"
    exit 1
fi

emacs --batch -l scripts/init-org-roam.el --eval "
(let* ((node (org-roam-node-from-id \"${NODE_ID}\"))
       (file (when node (org-roam-node-file node))))
  (if file
      (progn
        (with-current-buffer (find-file-noselect file)
          ;; Format LaTeX equations
          (goto-char (point-min))
          (while (re-search-forward \"\\\\\\[\\\\|\\\\\\]\\|\$\$\" nil t)
            (let ((start (match-beginning 0))
                  (end (match-end 0)))
              (goto-char start)
              (unless (bolp) (insert \"\n\"))
              (goto-char (+ end 1))
              (unless (eolp) (insert \"\n\"))))
          (save-buffer))
        (message \"Formatted LaTeX in: %s\" (file-relative-name file org-roam-directory)))
    (message \"Node not found: ${NODE_ID}\")))"
