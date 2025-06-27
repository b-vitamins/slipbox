"""Tag inheritance and analysis for Org-roam slips."""

import re
from typing import List, Dict, Set, Optional
from collections import defaultdict

from .base import BaseValidator
from ..models import Slip, Violation, Severity


class TagInheritanceValidator(BaseValidator):
    """Validates tag inheritance and structure in slips."""
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check tag inheritance and usage patterns."""
        violations = []
        
        # Extract all tags from the slip
        file_tags = set(slip.properties.filetags or [])
        headline_tags = self._extract_headline_tags(slip.content)
        
        # Check for tag conflicts
        for line_num, tags in headline_tags.items():
            # Check for redundant tags (already in filetags)
            redundant = tags & file_tags
            if redundant:
                violations.append(Violation(
                    rule="REDUNDANT_HEADLINE_TAGS",
                    message=f"Headline tags {redundant} already in #+FILETAGS. "
                           f"Headlines inherit file tags automatically.",
                    line_number=line_num,
                    severity=Severity.INFO
                ))
        
        # Check for too many unique tags
        all_tags = file_tags.copy()
        for tags in headline_tags.values():
            all_tags.update(tags)
        
        if len(all_tags) > 10:
            violations.append(Violation(
                rule="TOO_MANY_TAGS",
                message=f"Slip has {len(all_tags)} unique tags. "
                       f"Consider consolidating or using more general tags.",
                severity=Severity.WARNING
            ))
        
        return violations
    
    def _extract_headline_tags(self, content: str) -> Dict[int, Set[str]]:
        """Extract tags from headlines."""
        headline_tags = {}
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Match headlines with tags
            match = re.match(r'^(\*+)\s+(.+?)\s+:([\w:]+):$', line)
            if match:
                tags_str = match.group(3)
                tags = set(tag for tag in tags_str.split(':') if tag)
                headline_tags[i] = tags
        
        return headline_tags


class TagConsistencyValidator(BaseValidator):
    """Validates tag naming and consistency."""
    
    def __init__(self, known_tags: Optional[Set[str]] = None):
        """Initialize with optional set of known valid tags."""
        self.known_tags = known_tags or set()
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check tag naming conventions and consistency."""
        violations = []
        
        all_tags = list(slip.properties.filetags or [])
        
        for tag in all_tags:
            # Check tag format (lowercase letters and numbers only)
            if not re.match(r'^[a-z][a-z0-9]*$', tag):
                violations.append(Violation(
                    rule="INVALID_TAG_FORMAT",
                    message=f"Tag '{tag}' must contain only lowercase letters and numbers (a-z0-9)",
                    severity=Severity.ERROR
                ))
            
            # Check tag length (max 20 characters)
            if len(tag) > 20:
                violations.append(Violation(
                    rule="TAG_TOO_LONG",
                    message=f"Tag '{tag}' exceeds 20 character limit ({len(tag)} chars)",
                    severity=Severity.ERROR
                ))
            
            # Check for similar tags (typos)
            # Skip similarity check for known intentional pairs
            intentional_similar_pairs = [
                ('s4', 's5'),  # S4/S5 are different model versions
                ('s5', 's4'),
            ]
            
            similar = self._find_similar_tags(tag, all_tags)
            if similar:
                # Check if this is an intentional pair
                is_intentional = any(
                    (tag == pair[0] and sim_tag in similar and sim_tag == pair[1])
                    for pair in intentional_similar_pairs
                    for sim_tag in similar
                )
                
                if not is_intentional:
                    violations.append(Violation(
                        rule="SIMILAR_TAGS",
                        message=f"Tag '{tag}' is similar to {similar}. Check for typos.",
                        severity=Severity.INFO
                    ))
            
            # Check against known tags if provided
            if self.known_tags and tag not in self.known_tags:
                suggestions = self._suggest_known_tags(tag)
                if suggestions:
                    violations.append(Violation(
                        rule="UNKNOWN_TAG",
                        message=f"Unknown tag '{tag}'. Did you mean: {suggestions}?",
                        severity=Severity.INFO
                    ))
        
        return violations
    
    def _find_similar_tags(self, tag: str, all_tags: List[str]) -> List[str]:
        """Find tags that are similar (potential typos)."""
        similar = []
        for other in all_tags:
            if other != tag and self._are_similar(tag, other):
                similar.append(other)
        return similar
    
    def _are_similar(self, s1: str, s2: str) -> bool:
        """Check if two strings are similar (edit distance <= 2)."""
        # Simple check: length difference
        if abs(len(s1) - len(s2)) > 2:
            return False
        
        # Check for substring
        if s1 in s2 or s2 in s1:
            return True
        
        # Simple edit distance (not optimal but good enough)
        if len(s1) == len(s2):
            diff_count = sum(1 for a, b in zip(s1, s2) if a != b)
            return diff_count <= 2
        
        return False
    
    def _suggest_known_tags(self, tag: str) -> List[str]:
        """Suggest known tags similar to the given tag."""
        suggestions = []
        for known in self.known_tags:
            if self._are_similar(tag, known):
                suggestions.append(known)
        return suggestions[:3]  # Limit to 3 suggestions


class TagHierarchyValidator(BaseValidator):
    """Validates tag hierarchy and relationships."""
    
    def __init__(self, tag_hierarchy: Optional[Dict[str, List[str]]] = None):
        """Initialize with optional tag hierarchy.
        
        Args:
            tag_hierarchy: Dict mapping parent tags to child tags.
                          E.g., {"ml": ["neural_networks", "reinforcement_learning"]}
        """
        self.tag_hierarchy = tag_hierarchy or {}
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check tag hierarchy rules."""
        violations = []
        
        if not self.tag_hierarchy or not slip.properties.filetags:
            return violations
        
        tags = set(slip.properties.filetags)
        
        # Check for missing parent tags
        for tag in tags:
            for parent, children in self.tag_hierarchy.items():
                if tag in children and parent not in tags:
                    violations.append(Violation(
                        rule="MISSING_PARENT_TAG",
                        message=f"Tag '{tag}' requires parent tag '{parent}'",
                        severity=Severity.INFO
                    ))
        
        # Check for redundant child tags
        for parent in tags:
            if parent in self.tag_hierarchy:
                children = self.tag_hierarchy[parent]
                child_tags = [c for c in children if c in tags]
                
                # If parent tag is present, having all children might be redundant
                if len(child_tags) == len(children):
                    violations.append(Violation(
                        rule="REDUNDANT_CHILD_TAGS",
                        message=f"All child tags of '{parent}' are present. "
                               f"Consider using only the parent tag.",
                        severity=Severity.INFO
                    ))
        
        return violations


class TagAnalysisValidator(BaseValidator):
    """Meta-validator for all tag-related validations."""
    
    def __init__(self, known_tags: Optional[Set[str]] = None,
                 tag_hierarchy: Optional[Dict[str, List[str]]] = None):
        """Initialize with configuration."""
        self.validators = [
            TagInheritanceValidator(),
            TagConsistencyValidator(known_tags),
            TagHierarchyValidator(tag_hierarchy)
        ]
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all tag validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations