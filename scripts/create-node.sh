#!/bin/bash
set -euo pipefail

TYPE="${1:-fleeting}"
TITLE="${2:-Untitled}"
CONTENT="${3:-}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let ((file (create-org-roam-node \"${TYPE}\" \"${TITLE}\" \"${CONTENT}\")))
  (message \"Created: %s\" file))"
