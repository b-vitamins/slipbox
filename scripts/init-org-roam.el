;;; init-org-roam.el --- Initialize Org-Roam for batch operations -*- lexical-binding: t -*-

(require 'package)
(setq package-user-dir (expand-file-name "../elpa" (file-name-directory load-file-name)))
(package-initialize)

(require 'org)
(require 'org-roam)
(require 'org-id)

;; Configure directories
(setq org-roam-directory (expand-file-name "../notes" (file-name-directory load-file-name)))
(setq org-roam-db-location (expand-file-name "../notes/org-roam.db" (file-name-directory load-file-name)))
(setq org-id-locations-file (expand-file-name "../notes/.org-id-locations" (file-name-directory load-file-name)))

;; Ensure UUID generation
(setq org-id-method 'uuid)

;; Configure capture templates
(setq org-roam-capture-templates
      '(("f" "fleeting" plain "%?"
         :target (file+head "fleeting/%<%Y-%m-%d-%H-%M-%S>-${slug}.org"
                           ":PROPERTIES:\n:ID:       ${id}\n:END:\n#+TITLE: ${title}\n#+FILETAGS: :fleeting:\n#+SETUPFILE: ../../setupfile.org\n")
         :unnarrowed t)
        ("F" "fleeting-timed" plain "%?"
         :target (file+head "fleeting/%<%Y-%m-%d-%H-%M-%S>-${slug}.org"
                           ":PROPERTIES:\n:ID:       ${id}\n:END:\n#+TITLE: ${title}\n#+FILETAGS: :fleeting:\n#+SETUPFILE: ../../setupfile.org\n\n#+BEGIN: clocktable :maxlevel 2 :scope nil\n#+END:\n")
         :unnarrowed t)
        ("c" "concept" plain "%?"
         :target (file+head "concept/%<%Y-%m-%d-%H-%M-%S>-${slug}.org"
                           ":PROPERTIES:\n:ID:       ${id}\n:END:\n#+TITLE: ${title}\n#+FILETAGS: :concept:\n#+SETUPFILE: ../../setupfile.org\n")
         :unnarrowed t)
        ("l" "literature" plain "%?"
         :target (file+head "literature/%<%Y-%m-%d-%H-%M-%S>-${slug}.org"
                           ":PROPERTIES:\n:ID:       ${id}\n:END:\n#+TITLE: ${title}\n#+FILETAGS: :literature:\n#+AUTHOR: \n#+YEAR: \n#+SETUPFILE: ../../setupfile.org\n")
         :unnarrowed t)
        ("p" "problem" plain "%?"
         :target (file+head "problem/%<%Y-%m-%d-%H-%M-%S>-${slug}.org"
                           ":PROPERTIES:\n:ID:       ${id}\n:END:\n#+TITLE: ${title}\n#+FILETAGS: :problem:\n#+SETUPFILE: ../../setupfile.org\n\n* Problem Statement\n\n* Solution\n\n* Related Concepts")
         :unnarrowed t)))

;; Start org-roam
(org-roam-db-autosync-mode 1)

;; Utility functions
(defun create-org-roam-node (type title content)
  "Create a new org-roam node with TYPE, TITLE and CONTENT."
  (let* ((id (org-id-uuid))
         (slug (replace-regexp-in-string "[^a-z0-9]+" "-" 
                 (replace-regexp-in-string "^-\|-$" "" 
                   (downcase title))))
         (timestamp (format-time-string "%Y-%m-%d-%H-%M-%S"))
         (filename (format "%s-%s.org" timestamp slug))
         (dir (pcase type
                ("fleeting" "fleeting")
                ("fleeting-timed" "fleeting")
                ("concept" "concept")
                ("concept-timed" "concept")
                ("literature" "literature")
                ("literature-timed" "literature")
                ("problem" "problem")
                ("problem-timed" "problem")
                ("index" "index")
                ("daily" "daily")
                (_ "fleeting")))
         (filepath (expand-file-name (format "%s/%s" dir filename) org-roam-directory)))
    (make-directory (file-name-directory filepath) t)
    (with-temp-file filepath
      (insert ":PROPERTIES:\n")
      (insert (format ":ID:       %s\n" id))
      (insert ":END:\n")
      (insert (format "#+TITLE: %s\n" title))
      (insert (format "#+FILETAGS: :%s:\n" (replace-regexp-in-string "-timed$" "" type)))
      (insert "#+SETUPFILE: ../../setupfile.org\n")
      (when (string-match "-timed$" type)
        (insert "\n#+BEGIN: clocktable :maxlevel 2 :scope nil\n")
        (insert "#+END:\n"))
      (when content
        (insert (format "\n%s\n" content))))
    (org-roam-db-sync)
    filepath))

(provide 'init-org-roam)
