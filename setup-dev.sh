#!/bin/bash
set -euo pipefail

# slipbox development environment setup
# Installs Emacs with org-roam and supporting utilities in offline-ready mode.
# Run this script once while online. It will download packages and
# Emacs extensions so that you can work offline afterwards.


# Update package lists
sudo apt-get update -y

# Install essential packages without recommendations to avoid mail utilities
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    emacs-nox git ripgrep curl

# Prepare minimal Emacs configuration for package installation
EMACS_DIR="$HOME/.emacs.d"
mkdir -p "$EMACS_DIR"
INIT_FILE="$EMACS_DIR/init.el"

cat > "$INIT_FILE" <<'EOL'
(require 'package)
(setq package-archives '(("melpa" . "https://melpa.org/packages/")
                         ("gnu" . "https://elpa.gnu.org/packages/")))
(package-initialize)
(unless package-archive-contents
  (package-refresh-contents))
(dolist (pkg '(org org-roam))
  (unless (package-installed-p pkg)
    (package-install pkg)))
EOL

# Install packages now so they are cached for offline use
emacs --batch -l "$INIT_FILE"

# Verify installation
if emacs --batch --eval="(progn (require 'package) (package-initialize) (require 'org) (require 'org-roam) (message \"Org-roam installed\"))" >/tmp/emacs-check.log 2>&1; then
    echo "Emacs and org-roam installed successfully."
else
    echo "Failed to install org-roam. See /tmp/emacs-check.log" >&2
    exit 1
fi

cat <<'EOT'

Development environment setup complete.
You can now use Emacs with org-roam offline.
EOT
