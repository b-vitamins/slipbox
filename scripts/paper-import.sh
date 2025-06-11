#!/bin/bash
set -euo pipefail

TITLE="${1:-}"
AUTHORS="${2:-}"
YEAR="${3:-}"
VENUE="${4:-}"

if [ -z "$TITLE" ]; then
    echo "Usage: $0 \"Paper Title\" \"Authors\" \"Year\" \"Conference/Journal\""
    exit 1
fi

CONTENT="* Citation
#+BEGIN_SRC bibtex
@article{key$(date +%s),
  title={${TITLE}},
  author={${AUTHORS}},
  year={${YEAR}},
  journal={${VENUE}}
}
#+END_SRC

* Summary

* Key Contributions

* Important Equations

* Personal Notes

* Related Work"

./scripts/create-node.sh "literature" "$TITLE" "$CONTENT"
