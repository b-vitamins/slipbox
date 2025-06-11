#!/bin/bash
set -euo pipefail
DATE="$(date +%Y-%m-%d)"
FILE="notes/daily/${DATE}.org"
if [ ! -f "$FILE" ]; then
  emacs --batch -l scripts/init-org-roam.el --eval "(create-org-roam-node \"daily\" \"Daily ${DATE}\" \"\")" >/dev/null
fi
echo "Opened $FILE"
