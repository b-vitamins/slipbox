"""Headline node validation for Org-roam slips."""

import re
from typing import List, Dict, Set
from pathlib import Path

from .base import BaseValidator
from ..models import Slip, Violation, Severity, HeadlineNode


class HeadlineNodeValidator(BaseValidator):
    """Validates headline nodes within slips."""
    
    def __init__(self, check_duplicate_ids: bool = True):
        """Initialize validator.
        
        Args:
            check_duplicate_ids: Whether to check for duplicate IDs across headlines.
        """
        self.check_duplicate_ids = check_duplicate_ids
        self.all_node_ids: Dict[str, str] = {}  # ID -> file:line reference
    
    def set_all_node_ids(self, all_ids: Dict[str, str]):
        """Set all node IDs for duplicate detection."""
        self.all_node_ids = all_ids
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Validate headline nodes in slip."""
        violations = []
        
        if not slip.headline_nodes:
            return violations
        
        # Check each headline node
        for node in slip.headline_nodes:
            # Validate node has required ID
            if not node.properties.id:
                violations.append(Violation(
                    rule="HEADLINE_MISSING_ID",
                    message=f"Headline '{node.title}' has properties block but no :ID:",
                    line_number=node.line_number,
                    severity=Severity.ERROR
                ))
            
            # Validate ID format (should be UUID)
            elif node.properties.id:
                try:
                    import uuid
                    uuid.UUID(node.properties.id)
                except ValueError:
                    violations.append(Violation(
                        rule="HEADLINE_INVALID_ID",
                        message=f"Headline '{node.title}' has invalid ID format: {node.properties.id}",
                        line_number=node.line_number,
                        severity=Severity.ERROR
                    ))
            
            # Check for duplicate IDs
            if self.check_duplicate_ids and node.properties.id in self.all_node_ids:
                other_ref = self.all_node_ids[node.properties.id]
                violations.append(Violation(
                    rule="DUPLICATE_HEADLINE_ID",
                    message=f"Headline ID '{node.properties.id}' already used in {other_ref}",
                    line_number=node.line_number,
                    severity=Severity.ERROR
                ))
            
            # Warn if headline has CUSTOM_ID (unusual for headline nodes)
            if node.properties.custom_id:
                violations.append(Violation(
                    rule="HEADLINE_HAS_CUSTOM_ID",
                    message=f"Headline '{node.title}' has CUSTOM_ID '{node.properties.custom_id}'. "
                           f"This is unusual for headline nodes.",
                    line_number=node.line_number,
                    severity=Severity.INFO
                ))
        
        return violations


class HeadlineTitleValidator(BaseValidator):
    """Validates headline titles and structure."""
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check headline titles are properly formatted."""
        violations = []
        
        if not slip.headline_nodes:
            return violations
        
        for node in slip.headline_nodes:
            # Check for empty titles
            if not node.title or not node.title.strip():
                violations.append(Violation(
                    rule="EMPTY_HEADLINE_TITLE",
                    message=f"Headline at line {node.line_number} has empty title",
                    line_number=node.line_number,
                    severity=Severity.ERROR
                ))
            
            # Check for TODO keywords in node titles (should be properties)
            todo_pattern = r'^(TODO|DONE|NEXT|WAITING|CANCELLED)\s+'
            if re.match(todo_pattern, node.title):
                violations.append(Violation(
                    rule="TODO_IN_NODE_TITLE",
                    message=f"Headline node '{node.title}' has TODO keyword. "
                           f"Node headlines should not have TODO states.",
                    line_number=node.line_number,
                    severity=Severity.WARNING
                ))
            
            # Check for tags in headline (should use filetags)
            if re.search(r'\s+:[^:]+:$', node.title):
                violations.append(Violation(
                    rule="TAGS_IN_HEADLINE_NODE",
                    message=f"Headline node '{node.title}' has inline tags. "
                           f"Use #+FILETAGS: or inherit from parent.",
                    line_number=node.line_number,
                    severity=Severity.INFO
                ))
        
        return violations


class HeadlineStructureValidator(BaseValidator):
    """Validates overall headline structure and nesting."""
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check headline structure is reasonable."""
        violations = []
        
        if not slip.headline_nodes:
            return violations
        
        # Build level histogram
        level_counts = {}
        for node in slip.headline_nodes:
            level_counts[node.level] = level_counts.get(node.level, 0) + 1
        
        # Check for deep nesting
        max_level = max(level_counts.keys()) if level_counts else 0
        if max_level > 3:
            violations.append(Violation(
                rule="DEEP_HEADLINE_NESTING",
                message=f"Headlines nested {max_level} levels deep. "
                       f"Consider flattening structure or creating separate slips.",
                severity=Severity.WARNING
            ))
        
        # Check for too many headline nodes
        total_nodes = len(slip.headline_nodes)
        if total_nodes > 10:
            violations.append(Violation(
                rule="TOO_MANY_HEADLINE_NODES",
                message=f"File has {total_nodes} headline nodes. "
                       f"Consider splitting into multiple slips.",
                severity=Severity.WARNING
            ))
        
        # Check for orphaned deep headlines (e.g., *** without **)
        if len(level_counts) > 1:
            levels = sorted(level_counts.keys())
            for i in range(1, len(levels)):
                if levels[i] - levels[i-1] > 1:
                    violations.append(Violation(
                        rule="ORPHANED_HEADLINE_LEVEL",
                        message=f"Headline level {levels[i]} without level {levels[i]-1}. "
                               f"Headline hierarchy should be continuous.",
                        severity=Severity.WARNING
                    ))
        
        return violations


class HeadlineNodesValidator(BaseValidator):
    """Meta-validator for all headline node validations."""
    
    def __init__(self, check_duplicate_ids: bool = True):
        """Initialize with configuration."""
        self.node_validator = HeadlineNodeValidator(check_duplicate_ids)
        self.validators = [
            self.node_validator,
            HeadlineTitleValidator(),
            HeadlineStructureValidator()
        ]
        self.check_duplicate_ids = check_duplicate_ids
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all headline validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations
    
    def set_all_node_ids_for_duplicate_check(self, all_ids: Dict[str, str]):
        """Set all node IDs for duplicate detection."""
        if self.check_duplicate_ids:
            self.node_validator.set_all_node_ids(all_ids)