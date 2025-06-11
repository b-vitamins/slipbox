#!/bin/bash
set -euo pipefail
TITLE="$1"
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g;s/--*/-/g;s/^-//;s/-$//')
FILE="notes/index/${SLUG}.org"
UUID=$(uuidgen)
mkdir -p notes/index
emacs --batch -l scripts/init-org-roam.el --eval "(with-temp-file \"${FILE}\" (insert \":PROPERTIES:\n:ID:       ${UUID}\n:END:\n#+TITLE: ${TITLE}\n#+FILETAGS: :index:\n#+SETUPFILE: ../../setupfile.org\n\n\"))"
echo "Index created: $FILE"
