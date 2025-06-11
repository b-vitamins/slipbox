#!/bin/bash
set -euo pipefail

TITLE="$1"
CONTENT="${2:-}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let ((file (create-org-roam-node \"index\" \"${TITLE}\" \"${CONTENT}\")))
  (message \"Index created: %s\" file))"
