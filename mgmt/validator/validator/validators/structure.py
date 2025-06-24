"""Structure validation for slips."""

import re
import uuid
from typing import List, Dict
from pathlib import Path

from .base import BaseValidator
from ..models import Slip, Violation, Severity


class RequiredPropertiesValidator(BaseValidator):
    """Validates that required properties exist and are properly formatted."""
    
    def __init__(self, org_roam_priority: bool = True, require_custom_id: bool = True):
        """Initialize with Org-roam priority and CUSTOM_ID requirement settings."""
        self.org_roam_priority = org_roam_priority
        self.require_custom_id = require_custom_id
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check for required properties: ID, CUSTOM_ID, TITLE, FILETAGS."""
        violations = []
        properties = slip.properties
        
        # Check ID exists and is valid UUID
        if not properties.id:
            violations.append(Violation(
                rule="MISSING_ID",
                message="Missing required :ID: property (required for Org-roam functionality)",
                severity=Severity.ERROR
            ))
        else:
            try:
                uuid.UUID(properties.id)
            except ValueError:
                violations.append(Violation(
                    rule="INVALID_ID",
                    message=f"Invalid UUID format in :ID: property: {properties.id}",
                    severity=Severity.ERROR
                ))
        
        # Check CUSTOM_ID exists (severity depends on configuration)
        if not properties.custom_id and self.require_custom_id:
            if self.org_roam_priority:
                # In Org-roam priority mode, missing CUSTOM_ID is a warning
                violations.append(Violation(
                    rule="MISSING_CUSTOM_ID",
                    message="Missing :CUSTOM_ID: property (human readable convenience for referencing)",
                    severity=Severity.WARNING
                ))
            else:
                # In non-Org-roam mode, missing CUSTOM_ID is an error
                violations.append(Violation(
                    rule="MISSING_CUSTOM_ID",
                    message="Missing required :CUSTOM_ID: property",
                    severity=Severity.ERROR
                ))
        
        # Check TITLE exists
        if not properties.title:
            violations.append(Violation(
                rule="MISSING_TITLE",
                message="Missing required #+TITLE: property",
                severity=Severity.ERROR
            ))
        
        # Check FILETAGS exists and has at least one tag
        if properties.filetags is None:
            violations.append(Violation(
                rule="MISSING_FILETAGS",
                message="Missing required #+FILETAGS: property",
                severity=Severity.ERROR
            ))
        elif len(properties.filetags) == 0:
            violations.append(Violation(
                rule="EMPTY_FILETAGS",
                message="#+FILETAGS: property exists but contains no tags",
                severity=Severity.WARNING
            ))
        
        return violations


class LuhmannNumberValidator(BaseValidator):
    """Validates CUSTOM_ID follows Luhmann numbering pattern."""
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check CUSTOM_ID follows pattern: \\d+(/\\d+)*[a-z]*\\d*"""
        violations = []
        
        if not slip.properties.custom_id:
            # RequiredPropertiesValidator will catch this
            return violations
        
        custom_id = slip.properties.custom_id
        
        # Pattern: digits, optional slashes with digits, optional letters, optional digits
        # Examples: 42, 42/3, 42/3a, 42/3a1, 57/12/5b2
        pattern = r'^\d+(/\d+)*[a-z]*\d*$'
        
        if not re.match(pattern, custom_id):
            violations.append(Violation(
                rule="INVALID_LUHMANN_NUMBER",
                message=f"CUSTOM_ID does not follow Luhmann numbering pattern: {custom_id}. "
                       f"Expected format: digits[/digits]*[letters]*[digits]* (e.g., 42/3a, 57/12)",
                severity=Severity.ERROR
            ))
        
        return violations


class WordCountValidator(BaseValidator):
    """Validates slip content doesn't exceed word limit."""
    
    def __init__(self, word_limit: int = 500):
        """Initialize with word limit (default 500)."""
        self.word_limit = word_limit
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check word count is within limit."""
        violations = []
        
        # Skip validation for slips tagged with :extended: or :sequence:
        exempt_tags = {"extended", "sequence"}
        if any(tag in exempt_tags for tag in slip.properties.filetags):
            return violations
        
        if slip.word_count > self.word_limit:
            violations.append(Violation(
                rule="WORD_LIMIT_EXCEEDED",
                message=f"Content exceeds {self.word_limit} word limit: {slip.word_count} words. "
                       f"Consider breaking into multiple slips or adding :extended: tag.",
                severity=Severity.ERROR
            ))
        
        return violations


class RoamPropertiesValidator(BaseValidator):
    """Validates ROAM_ALIASES and ROAM_REFS properties format."""
    
    def __init__(self, check_duplicate_aliases: bool = True):
        """Initialize with configuration."""
        self.check_duplicate_aliases = check_duplicate_aliases
        self.all_aliases = {}  # Will be populated by meta-validator
    
    def set_all_aliases(self, all_aliases: Dict[str, List[str]]):
        """Set all aliases for duplicate detection. Called by meta-validator."""
        self.all_aliases = all_aliases
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Validate ROAM_ALIASES and ROAM_REFS format."""
        violations = []
        
        # Validate ROAM_ALIASES format
        if slip.properties.roam_aliases:
            for alias in slip.properties.roam_aliases:
                if not self._is_valid_alias_format(alias):
                    violations.append(Violation(
                        rule="INVALID_ROAM_ALIAS",
                        message=f"Invalid ROAM_ALIASES format: '{alias}'. "
                               f"Should be readable text without special characters.",
                        severity=Severity.WARNING
                    ))
                
                # Check for duplicate aliases across slips
                if self.check_duplicate_aliases and self.all_aliases:
                    for file_path, aliases in self.all_aliases.items():
                        if file_path != str(slip.file_path) and alias in aliases:
                            violations.append(Violation(
                                rule="DUPLICATE_ROAM_ALIAS",
                                message=f"ROAM_ALIASES '{alias}' duplicated in {file_path}. "
                                       f"Aliases should be unique across slips.",
                                severity=Severity.WARNING
                            ))
        
        # Validate ROAM_REFS format  
        if slip.properties.roam_refs:
            for ref in slip.properties.roam_refs:
                if not self._is_valid_refs_format(ref):
                    violations.append(Violation(
                        rule="INVALID_ROAM_REFS",
                        message=f"Invalid ROAM_REFS format: '{ref}'. "
                               f"Should be URL (https://...) or citation key (@key or author2023word).",
                        severity=Severity.WARNING
                    ))
        
        return violations
    
    def _is_valid_alias_format(self, alias: str) -> bool:
        """Check if alias has valid format."""
        # Aliases should be readable text, not too long, reasonable characters
        if not alias or len(alias) > 100:  # Reasonable length limit
            return False
        
        # Should not contain control characters or excessive punctuation
        if any(ord(c) < 32 for c in alias):  # Control characters
            return False
        
        # Should have some alphanumeric content
        if not any(c.isalnum() for c in alias):
            return False
        
        return True
    
    def _is_valid_refs_format(self, ref: str) -> bool:
        """Check if ROAM_REFS entry has valid format."""
        # URLs (http/https)
        if ref.startswith(('http://', 'https://')):
            # Basic URL validation
            return len(ref) > 10 and '.' in ref
        
        # Citation keys (@key format)
        if ref.startswith('@'):
            key = ref[1:]
            return self._is_valid_citation_key(key)
        
        # Bare citation keys (author2023word format)
        if self._is_valid_citation_key(ref):
            return True
        
        # Other formats (DOIs, etc.) - be permissive for now
        return len(ref) > 3
    
    def _is_valid_citation_key(self, key: str) -> bool:
        """Check if string looks like a valid citation key."""
        # Citation keys typically: author2023word, smith_2024_theory, etc.
        if not key or len(key) < 3:
            return False
        
        # Should start with letter and contain mostly alphanumeric + common symbols
        if not key[0].isalpha():
            return False
        
        # Allow letters, numbers, underscores, hyphens, colons, dots
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-:.')
        return all(c in allowed_chars for c in key)


class SlipStructureValidator(BaseValidator):
    """Meta-validator that runs all structure validations."""
    
    def __init__(self, word_limit: int = 500, org_roam_priority: bool = True, require_custom_id: bool = True, 
                 check_duplicate_aliases: bool = True):
        """Initialize with configuration."""
        self.roam_validator = RoamPropertiesValidator(check_duplicate_aliases)
        self.validators = [
            RequiredPropertiesValidator(org_roam_priority, require_custom_id),
            LuhmannNumberValidator(),
            WordCountValidator(word_limit),
            self.roam_validator
        ]
        self.check_duplicate_aliases = check_duplicate_aliases
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all structure validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations
    
    def set_all_aliases_for_duplicate_check(self, all_aliases: Dict[str, List[str]]):
        """Set all aliases for duplicate detection. Called by ValidationEngine if needed."""
        if self.check_duplicate_aliases:
            self.roam_validator.set_all_aliases(all_aliases)