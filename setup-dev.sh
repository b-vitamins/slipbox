#!/bin/bash
set -euo pipefail

# Install system packages
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo -E apt-get install -y --no-install-recommends emacs-nox sqlite3 ripgrep fd-find jq git \
    texlive-extra-utils chktex lacheck uuid-runtime

# Create scripts directory and note directories
mkdir -p scripts
mkdir -p notes/{daily,fleeting,literature,concept,problem,index,attachments,archive}

# Write .gitignore for notes
cat > notes/.gitignore <<'EOG'
org-roam.db
org-roam.db-wal
org-roam.db-shm
EOG

# Download Emacs packages
emacs --batch -Q <<'ELISP'
(require 'package)
(setq package-user-dir (expand-file-name "elpa"))
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/") t)
(package-initialize)
(package-refresh-contents)
(dolist (pkg '(org org-roam))
  (unless (package-installed-p pkg)
    (package-install pkg)))
ELISP

# Make all scripts executable
chmod +x scripts/*.sh 2>/dev/null || true

# Create starter note
mkdir -p notes/index
emacs --batch -l scripts/init-org-roam.el --eval "(with-temp-file \"notes/index/start-here.org\" (insert \"#+TITLE: Start Here\n#+SETUPFILE: ../../setupfile.org\n\nWelcome to the slipbox.\n\"))"

# Build initial database
emacs --batch -l scripts/init-org-roam.el --eval '(org-roam-db-sync)'

# Copy AGENTS.md template if provided
if [ -f AGENTS.md.comprehensive ]; then
  cp AGENTS.md.comprehensive AGENTS.md
fi

echo "=== Setup Complete ==="
echo "Created $(ls scripts/*.sh | wc -l) scripts"
echo "Run ./scripts/check-health.sh to verify installation"
