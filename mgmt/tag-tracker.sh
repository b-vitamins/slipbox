#!/bin/bash

# tag-tracker.sh - Track new tags introduced in commits
# Usage: Called from prepare-commit-msg hook

TAGS_FILE=".git/tags-index"
STAGED_FILES=$(git diff --cached --name-only | grep "^slips/.*\.org$")

# Initialize tags file if it doesn't exist
if [ ! -f "$TAGS_FILE" ]; then
    echo "# Tag index for slipbox - auto-generated" > "$TAGS_FILE"
    grep -h "^#+FILETAGS:" slips/*.org 2>/dev/null | \
        sed 's/#+FILETAGS: *//' | \
        tr ':' '\n' | \
        grep -v '^$' | \
        sort -u >> "$TAGS_FILE"
fi

# Get existing tags
existing_tags=$(cat "$TAGS_FILE" | grep -v '^#' | sort -u)

# Get tags from staged files
if [ -n "$STAGED_FILES" ]; then
    # Extract filetags and split by colons to get individual tags
    new_tags=$(echo "$STAGED_FILES" | while read file; do
        git show ":$file" 2>/dev/null | grep "^#+FILETAGS:" | sed 's/#+FILETAGS: *//' | tr ':' '\n'
    done | grep -v '^$' | sort -u)
    
    # Find truly new tags
    truly_new_tags=$(comm -13 <(echo "$existing_tags") <(echo "$new_tags"))
    
    if [ -n "$truly_new_tags" ]; then
        echo "$truly_new_tags"
        # Update tags file
        echo "$truly_new_tags" >> "$TAGS_FILE"
        sort -u "$TAGS_FILE" -o "$TAGS_FILE"
    fi
fi