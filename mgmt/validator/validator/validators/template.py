"""Template compliance validation for slips."""

import re
from typing import List, Optional, Dict, Pattern
from pathlib import Path
from datetime import datetime

from .base import BaseValidator
from ..models import Slip, Violation, Severity


class FilenameFormatValidator(BaseValidator):
    """Validates slip filenames follow consistent timestamp format."""
    
    def __init__(self, expected_formats: Optional[List[Pattern[str]]] = None):
        """Initialize with expected filename formats.
        
        Args:
            expected_formats: List of regex patterns for valid filenames.
                             If None, will auto-detect from existing slips.
        """
        self.expected_formats = expected_formats or []
        self.detected_formats: Dict[str, int] = {}  # format -> count
        self.format_examples: Dict[str, str] = {}  # format -> example filename
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check filename follows consistent format."""
        violations = []
        filename = slip.file_path.name
        
        # Extract just the base filename without extension
        base_name = slip.file_path.stem
        
        # If no expected formats provided, we're in detection mode
        if not self.expected_formats:
            format_type = self._detect_format_type(base_name)
            self.detected_formats[format_type] = self.detected_formats.get(format_type, 0) + 1
            if format_type not in self.format_examples:
                self.format_examples[format_type] = filename
            return violations
        
        # Check against expected formats
        matched = False
        for pattern in self.expected_formats:
            if pattern.match(base_name):
                matched = True
                break
        
        if not matched:
            format_type = self._detect_format_type(base_name)
            violations.append(Violation(
                rule="INCONSISTENT_FILENAME_FORMAT",
                message=f"Filename '{filename}' does not match expected format. "
                       f"Detected format: {format_type}",
                severity=Severity.WARNING
            ))
        
        return violations
    
    def _detect_format_type(self, base_name: str) -> str:
        """Detect the format type of a filename."""
        # Common org-roam formats
        patterns = {
            # 2025-06-05-23-32-18-git-fundamentals
            "YYYY-MM-DD-HH-MM-SS-slug": r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-',
            # 20241223T1005-coarse-graining-philosophy  
            "YYYYMMDDTHHmm-slug": r'^\d{8}T\d{4}-',
            # 2025-06-27-some-title (org-roam template default)
            "YYYY-MM-DD-slug": r'^\d{4}-\d{2}-\d{2}-[^-]',
            # 20250627-some-title
            "YYYYMMDD-slug": r'^\d{8}-',
            # 20250627123456-some-title
            "YYYYMMDDHHmmss-slug": r'^\d{14}-',
            # lit-2025-06-27-some-paper
            "prefix-YYYY-MM-DD-slug": r'^[a-z]+-\d{4}-\d{2}-\d{2}-',
            # 42-3a-some-title (Luhmann style)
            "luhmann-slug": r'^\d+(-\d+)*[a-z]*-',
        }
        
        for format_name, pattern in patterns.items():
            if re.match(pattern, base_name):
                return format_name
        
        return "unknown"
    
    def get_format_summary(self) -> Dict[str, Dict[str, any]]:
        """Get summary of detected formats."""
        return {
            format_type: {
                "count": count,
                "example": self.format_examples.get(format_type, "")
            }
            for format_type, count in self.detected_formats.items()
        }


class TemplateStructureValidator(BaseValidator):
    """Validates slips follow org-roam template structure."""
    
    def __init__(self, require_template_fields: bool = True):
        """Initialize validator.
        
        Args:
            require_template_fields: Whether to require template-generated fields.
        """
        self.require_template_fields = require_template_fields
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check slip follows template structure."""
        violations = []
        
        if not self.require_template_fields:
            return violations
        
        # Check for template-generated structure markers
        content_lines = slip.content.split('\n')
        
        # Look for signs of manual creation vs template
        has_property_drawer = False
        has_standard_structure = False
        
        for i, line in enumerate(content_lines[:20]):  # Check first 20 lines
            if line.strip() == ":PROPERTIES:":
                has_property_drawer = True
            
            # Check for standard template patterns
            if line.startswith("#+title:") or line.startswith("#+filetags:"):
                has_standard_structure = True
        
        # Detect if slip might be manually created
        if not has_property_drawer:
            violations.append(Violation(
                rule="MISSING_PROPERTY_DRAWER", 
                message="No :PROPERTIES: drawer found. Slip may not use org-roam template.",
                severity=Severity.INFO
            ))
        
        # Check filename matches content
        if slip.properties.title:
            expected_slug = self._title_to_slug(slip.properties.title)
            filename_slug = self._extract_slug_from_filename(slip.file_path.stem)
            
            # Only warn if slugs are significantly different
            # Disable this check as it's too strict for practical use
            # if filename_slug and expected_slug:
            #     similarity = self._calculate_similarity(expected_slug, filename_slug)
            #     if similarity < 0.5:  # Less than 50% similar
            #         violations.append(Violation(
            #             rule="FILENAME_TITLE_MISMATCH",
            #             message=f"Filename slug '{filename_slug}' doesn't match title '{slip.properties.title}'",
            #             severity=Severity.INFO
            #         ))
        
        return violations
    
    def _title_to_slug(self, title: str) -> str:
        """Convert title to slug format."""
        # Simple slugification
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _extract_slug_from_filename(self, stem: str) -> Optional[str]:
        """Extract slug portion from filename."""
        # Try to extract slug after timestamp
        patterns = [
            r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-(.*)',  # YYYY-MM-DD-HH-MM-SS-slug
            r'^\d{8}T\d{4}-(.*)',  # YYYYMMDDTHHmm-slug
            r'^\d{4}-\d{2}-\d{2}-(.*)',  # YYYY-MM-DD-slug
            r'^\d{8}-(.*)',  # YYYYMMDD-slug
            r'^\d{14}-(.*)',  # YYYYMMDDHHmmss-slug
            r'^[a-z]+-\d{4}-\d{2}-\d{2}-(.*)',  # prefix-YYYY-MM-DD-slug
        ]
        
        for pattern in patterns:
            match = re.match(pattern, stem)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple similarity between two strings."""
        # Simple character-based similarity
        if not s1 or not s2:
            return 0.0
        
        # Convert to sets of words
        words1 = set(s1.split('-'))
        words2 = set(s2.split('-'))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0


class TemplateFieldValidator(BaseValidator):
    """Validates required template fields are present and properly filled."""
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check for required template fields."""
        violations = []
        
        # Check for empty CUSTOM_ID (template creates it empty)
        if slip.properties.custom_id == "":
            violations.append(Violation(
                rule="EMPTY_CUSTOM_ID",
                message="CUSTOM_ID is empty. Should be filled with Luhmann number.",
                severity=Severity.WARNING
            ))
        
        # Check for empty filetags
        if slip.properties.filetags is not None and len(slip.properties.filetags) == 0:
            violations.append(Violation(
                rule="EMPTY_FILETAGS", 
                message="Filetags property exists but is empty. Add relevant tags.",
                severity=Severity.INFO
            ))
        
        # Check for template placeholders
        if slip.content:
            # Check for actual template variables, not shell syntax
            template_patterns = [
                (r'\$\{(slug|title|id)\}', 'Template variable'),  # ${slug}, ${title}, etc
                (r'%\?', 'Cursor position marker'),  # %?
                (r'%\(org-id-new\)', 'Function call marker'),  # %(org-id-new)
            ]
            
            for pattern, description in template_patterns:
                if re.search(pattern, slip.content):
                    violations.append(Violation(
                        rule="TEMPLATE_PLACEHOLDER_REMAINS",
                        message=f"{description} found in content",
                        severity=Severity.WARNING
                    ))
            
            # Also check for shell variable syntax in non-code contexts
            # Only flag ${} if it's not in a code block and looks like a template
            if '${' in slip.content and not self._is_in_code_block(slip.content, '${}'):
                # Check if it looks like a template variable (single word)
                template_var_pattern = r'\$\{[a-zA-Z_]\w*\}'
                if re.search(template_var_pattern, slip.content):
                    violations.append(Violation(
                        rule="TEMPLATE_PLACEHOLDER_REMAINS",
                        message="Possible template variable found outside code block",
                        severity=Severity.INFO
                    ))
        
        return violations
    
    def _is_in_code_block(self, content: str, text: str) -> bool:
        """Check if text appears within a code block."""
        lines = content.split('\n')
        in_src_block = False
        
        for line in lines:
            # Check for source block boundaries
            if line.strip().startswith('#+begin_src'):
                in_src_block = True
            elif line.strip().startswith('#+end_src'):
                in_src_block = False
            elif in_src_block and text in line:
                return True
        
        return False


class TemplateComplianceValidator(BaseValidator):
    """Meta-validator for all template compliance checks."""
    
    def __init__(self, expected_formats: Optional[List[str]] = None,
                 require_template_fields: bool = True):
        """Initialize with configuration.
        
        Args:
            expected_formats: List of regex patterns for valid filenames.
            require_template_fields: Whether to require template fields.
        """
        # Convert string patterns to compiled regexes
        if expected_formats:
            self.expected_format_patterns = [re.compile(fmt) for fmt in expected_formats]
        else:
            self.expected_format_patterns = None
            
        self.filename_validator = FilenameFormatValidator(self.expected_format_patterns)
        self.validators = [
            self.filename_validator,
            TemplateStructureValidator(require_template_fields),
            TemplateFieldValidator()
        ]
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all template validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations
    
    def get_format_summary(self) -> Dict[str, Dict[str, any]]:
        """Get summary of detected filename formats."""
        return self.filename_validator.get_format_summary()