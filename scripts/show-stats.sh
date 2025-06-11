#!/bin/bash
set -euo pipefail

emacs --batch -l scripts/init-org-roam.el --eval '
(let* ((total-nodes (caar (org-roam-db-query [:select (funcall count nodes:id) :from nodes])))
       (total-links (caar (org-roam-db-query [:select (funcall count source) :from links])))
       (fleeting (caar (org-roam-db-query [:select (funcall count nodes:id)
                                           :from nodes
                                           :left-join tags
                                           :on (= nodes:id tags:node-id)
                                           :where (= tags:tag "fleeting")])))
       (concept (caar (org-roam-db-query [:select (funcall count nodes:id)
                                          :from nodes
                                          :left-join tags
                                          :on (= nodes:id tags:node-id)
                                          :where (= tags:tag "concept")])))
       (literature (caar (org-roam-db-query [:select (funcall count nodes:id)
                                             :from nodes
                                             :left-join tags
                                             :on (= nodes:id tags:node-id)
                                             :where (= tags:tag "literature")])))
       (orphans (length (org-roam-db-query [:select nodes:id
                                            :from nodes
                                            :left-join links
                                            :on (= nodes:id links:dest)
                                            :where (is links:dest nil)]))))
  (message "=== Org-Roam Statistics ===")
  (message "Total nodes: %d" (or total-nodes 0))
  (message "Total links: %d" (or total-links 0))
  (message "")
  (message "By type:")
  (message "  Fleeting: %d" (or fleeting 0))
  (message "  Concept: %d" (or concept 0))
  (message "  Literature: %d" (or literature 0))
  (message "")
  (message "Orphaned nodes: %d" orphans)
  (when (> total-nodes 0)
    (message "Average links per node: %.2f" (/ (float total-links) total-nodes))))'
