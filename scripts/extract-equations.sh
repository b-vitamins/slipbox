#!/bin/bash
set -euo pipefail

TOPIC="${1:-}"

emacs --batch -l scripts/init-org-roam.el --eval "
(let ((files (if (string-empty-p \"${TOPIC}\")
                 (org-roam-list-files)
               (mapcar #'car
                       (org-roam-db-query
                        [:select [nodes:file]
                         :from nodes
                         :left-join tags
                         :on (= nodes:id tags:node-id)
                         :where (or (like nodes:title $r1)
                                   (like tags:tag $r1))]
                        (concat \"%\" \"${TOPIC}\" \"%\"))))
      (equations '()))
  (dolist (file files)
    (when (file-exists-p file)
      (with-temp-buffer
        (insert-file-contents file)
        (goto-char (point-min))
        (while (re-search-forward \"\\\\\\[\\(.*?\\)\\\\\\]\" nil t)
          (push (list (match-string 1) file) equations))
        (goto-char (point-min))
        (while (re-search-forward \"\\$\\$\\(.*?\\)\\$\\$\" nil t)
          (push (list (match-string 1) file) equations)))))
  (if equations
      (progn
        (message \"=== Equations found%s ===\"
                 (if (string-empty-p \"${TOPIC}\") \"\" (concat \" for: \" \"${TOPIC}\")))
        (dolist (eq (reverse equations))
          (message \"\nFile: %s\" (file-relative-name (cadr eq) org-roam-directory))
          (message \"Equation: %s\" (car eq))))
    (message \"No equations found%s\"
             (if (string-empty-p \"${TOPIC}\") \"\" (concat \" for: \" \"${TOPIC}\")))))"
