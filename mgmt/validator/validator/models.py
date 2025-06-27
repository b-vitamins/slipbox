"""Data models for slipbox validation."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class LinkType(Enum):
    """Types of links in slips."""
    INTERNAL = "internal"      # [[id:UUID][Description]] or [[CUSTOM_ID][Description]]
    EXTERNAL = "external"      # [[URL][Description]]
    BIBLIOGRAPHY = "bibliography"  # [[cite:key][Description]]
    MEDIA = "media"           # [[file:path][Description]]


class Severity(Enum):
    """Validation result severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SlipProperties:
    """Properties block of a slip."""
    id: str              # UUID, never changes
    custom_id: str       # Luhmann number (42/3a)
    title: str           # Clear, searchable title
    filetags: List[str]  # Type and domain tags
    created: Optional[datetime] = None  # Optional timestamp
    roam_aliases: List[str] = None  # Alternative names for search/completion
    roam_refs: List[str] = None     # External references (URLs, citation keys)


@dataclass
class Link:
    """A link between slips or to external resources."""
    source_slip: str     # Source slip ID
    target: str          # Target (slip ID, URL, file path, etc.)
    link_type: LinkType  # Type of link
    line_number: int     # Location in source slip
    context: str         # Surrounding text for validation


@dataclass
class ConnectionPoint:
    """A marked connection point within a slip."""
    line_number: int
    marker: str          # What marks this connection (red text equivalent)
    branches: List[str]  # Slip IDs that branch from this point


@dataclass
class HeadlineNode:
    """A headline within a slip that has its own ID property."""
    level: int  # Org headline level (1 = *, 2 = **, etc.)
    title: str  # Headline text
    properties: SlipProperties  # Can have full properties block
    line_number: int  # Where in file this headline starts
    parent_id: Optional[str] = None  # ID of parent node (file or headline)


@dataclass
class Slip:
    """A complete slip with all its components."""
    file_path: Path
    properties: SlipProperties
    content: str
    links: List[Link]
    word_count: int
    connection_points: List[ConnectionPoint]
    headline_nodes: List[HeadlineNode] = None  # Headlines with ID properties


@dataclass
class Violation:
    """A validation rule violation."""
    rule: str           # "WORD_LIMIT", "MISSING_PROPERTY", etc.
    message: str        # Human readable description
    line_number: Optional[int] = None  # Location of violation
    severity: Severity = Severity.ERROR


@dataclass
class ValidationResult:
    """Result of validating a single slip."""
    file_path: Path
    passed: bool
    violations: List[Violation]
    warnings: List[Violation]  # Violations with severity WARNING