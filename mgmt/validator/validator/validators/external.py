"""External resource validation for slips."""

import re
from pathlib import Path
from typing import List, Dict, Set
import urllib.request
import urllib.error
from urllib.parse import urlparse

from .base import BaseValidator
from ..models import Slip, Violation, Severity, LinkType


class BibliographyValidator(BaseValidator):
    """Validates that bibliography links reference existing entries."""
    
    def __init__(self, bibliography_dir: Path):
        """Initialize with bibliography directory."""
        self.bibliography_dir = bibliography_dir
        self.bib_entries = self._load_bibliography_entries()
    
    def _load_bibliography_entries(self) -> Set[str]:
        """Load all bibliography keys from .bib files."""
        entries = set()
        
        if not self.bibliography_dir.exists():
            return entries
        
        for bib_file in self.bibliography_dir.glob("*.bib"):
            try:
                with open(bib_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find BibTeX entry keys: @article{key, @book{key, etc.
                entry_pattern = r'@\w+\s*\{\s*([^,\s]+)'
                matches = re.findall(entry_pattern, content, re.IGNORECASE)
                entries.update(matches)
                
            except Exception:
                # Skip files that can't be read
                continue
        
        return entries
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check that bibliography links reference existing entries."""
        violations = []
        
        for link in slip.links:
            if link.link_type == LinkType.BIBLIOGRAPHY:
                # Extract citation key from cite:key format
                target = link.target
                if target.startswith("cite:"):
                    cite_key = target[5:]  # Remove "cite:" prefix
                else:
                    cite_key = target
                
                if cite_key not in self.bib_entries:
                    violations.append(Violation(
                        rule="MISSING_BIBLIOGRAPHY_ENTRY",
                        message=f"Bibliography entry not found: {cite_key}. "
                               f"Check .bib files in {self.bibliography_dir}",
                        line_number=link.line_number,
                        severity=Severity.ERROR
                    ))
        
        return violations


class ExternalURLValidator(BaseValidator):
    """Validates that external URLs are reachable."""
    
    def __init__(self, check_urls: bool = True, timeout_seconds: int = 10):
        """Initialize with configuration."""
        self.check_urls = check_urls
        self.timeout_seconds = timeout_seconds
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check that external URLs are reachable."""
        violations = []
        
        if not self.check_urls:
            return violations
        
        for link in slip.links:
            if link.link_type == LinkType.EXTERNAL:
                if not self._is_url_reachable(link.target):
                    violations.append(Violation(
                        rule="UNREACHABLE_URL",
                        message=f"External URL is not reachable: {link.target}",
                        line_number=link.line_number,
                        severity=Severity.WARNING  # Warning since URLs can be temporarily down
                    ))
        
        return violations
    
    def _is_url_reachable(self, url: str) -> bool:
        """Check if URL is reachable with HEAD request."""
        try:
            # Parse URL to validate format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Create request with timeout and user agent
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'slipbox-validator/1.0')
            request.get_method = lambda: 'HEAD'  # Use HEAD to avoid downloading content
            
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return response.status < 400
                
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
            return False


class MediaFileValidator(BaseValidator):
    """Validates that media file links point to existing files."""
    
    def __init__(self, slipbox_root: Path):
        """Initialize with slipbox root directory."""
        self.slipbox_root = slipbox_root
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check that media files exist."""
        violations = []
        
        for link in slip.links:
            if link.link_type == LinkType.MEDIA:
                if not self._file_exists(link.target):
                    violations.append(Violation(
                        rule="MISSING_MEDIA_FILE",
                        message=f"Media file not found: {link.target}",
                        line_number=link.line_number,
                        severity=Severity.ERROR
                    ))
        
        return violations
    
    def _file_exists(self, file_path: str) -> bool:
        """Check if file exists relative to slipbox root."""
        try:
            # Remove file: prefix if present
            if file_path.startswith("file:"):
                file_path = file_path[5:]
            
            # Resolve path relative to slipbox root
            full_path = self.slipbox_root / file_path
            return full_path.exists() and full_path.is_file()
            
        except (OSError, ValueError):
            return False


class ExternalResourceValidator(BaseValidator):
    """Meta-validator that runs all external resource validations."""
    
    def __init__(self, slipbox_root: Path, check_urls: bool = True, url_timeout: int = 10):
        """Initialize with configuration."""
        self.slipbox_root = slipbox_root
        bibliography_dir = slipbox_root / "bibliography"
        
        self.validators = [
            BibliographyValidator(bibliography_dir),
            ExternalURLValidator(check_urls, url_timeout),
            MediaFileValidator(slipbox_root)
        ]
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all external resource validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations