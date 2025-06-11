#!/bin/bash
set -euo pipefail
emacs --batch -l scripts/init-org-roam.el --eval '(org-roam-db-sync)'
