#!/bin/bash
set -euo pipefail

CONTENT="$1"
TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)
TITLE="Quick Capture ${TIMESTAMP}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let ((file (create-org-roam-node \"fleeting\" \"${TITLE}\" \"${CONTENT}\")))
  (message \"Captured to: %s\" file))"
