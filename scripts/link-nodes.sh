#!/bin/bash
set -euo pipefail

SOURCE_ID="$1"
TARGET_ID="$2"
LINK_TEXT="${3:-Link}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let* ((source-node (org-roam-node-from-id \"${SOURCE_ID}\"))
       (target-node (org-roam-node-from-id \"${TARGET_ID}\")))
  (if (and source-node target-node)
      (let ((source-file (org-roam-node-file source-node)))
        (with-current-buffer (find-file-noselect source-file)
          (goto-char (point-max))
          (insert (format \"\n\n[[id:%s][%s]]\n\" \"${TARGET_ID}\" \"${LINK_TEXT}\"))
          (save-buffer))
        (org-roam-db-sync)
        (message \"Linked: %s -> %s\" 
                 (org-roam-node-title source-node)
                 (org-roam-node-title target-node)))
    (message \"Error: Could not find one or both nodes\")))"
