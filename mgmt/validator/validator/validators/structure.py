"""Structure validation for slips."""

import re
import uuid
from typing import List

from .base import BaseValidator
from ..models import Slip, Violation, Severity


class RequiredPropertiesValidator(BaseValidator):
    """Validates that required properties exist and are properly formatted."""
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check for required properties: ID, CUSTOM_ID, TITLE, FILETAGS."""
        violations = []
        properties = slip.properties
        
        # Check ID exists and is valid UUID
        if not properties.id:
            violations.append(Violation(
                rule="MISSING_ID",
                message="Missing required :ID: property",
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
        
        # Check CUSTOM_ID exists  
        if not properties.custom_id:
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


class SlipStructureValidator(BaseValidator):
    """Meta-validator that runs all structure validations."""
    
    def __init__(self, word_limit: int = 500):
        """Initialize with configuration."""
        self.validators = [
            RequiredPropertiesValidator(),
            LuhmannNumberValidator(),
            WordCountValidator(word_limit)
        ]
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all structure validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations