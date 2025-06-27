"""Database consistency checks for Org-roam integration."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime

from .base import BaseValidator
from ..models import Slip, Violation, Severity


class DatabaseConsistencyValidator(BaseValidator):
    """Validates consistency between validator findings and org-roam database."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with optional database path.
        
        Args:
            db_path: Path to org-roam.db file. If None, will try to find it.
        """
        self.db_path = db_path
        self.db_nodes: Dict[str, Dict] = {}  # Cache of database nodes
        self.db_available = False
        
        # Try to load database
        if self.db_path and self.db_path.exists():
            self._load_database()
        else:
            # Try common locations
            for location in [
                Path.home() / ".cache/emacs/org-roam.db",
                Path.home() / ".emacs.d/org-roam.db",
                Path("~/.cache/org-roam.db").expanduser()
            ]:
                if location.exists():
                    self.db_path = location
                    self._load_database()
                    break
    
    def _load_database(self):
        """Load node information from org-roam database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all nodes from database
            cursor.execute("""
                SELECT id, file, title, level
                FROM nodes
            """)
            
            for node_id, file_path, title, level in cursor.fetchall():
                self.db_nodes[node_id] = {
                    'file': file_path,
                    'title': title,
                    'level': level  # 0 = file node, > 0 = headline node
                }
            
            conn.close()
            self.db_available = True
        except Exception:
            # Database might be locked or incompatible
            self.db_available = False
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check consistency between slip and database."""
        violations = []
        
        if not self.db_available:
            # Can't validate without database
            return violations
        
        # Check if slip ID exists in database
        if slip.properties.id and slip.properties.id not in self.db_nodes:
            violations.append(Violation(
                rule="MISSING_FROM_DATABASE",
                message=f"Slip ID '{slip.properties.id}' not found in org-roam database. "
                       f"Run 'M-x org-roam-db-sync' in Emacs.",
                severity=Severity.WARNING
            ))
        
        # Check if database info matches slip
        if slip.properties.id in self.db_nodes:
            db_info = self.db_nodes[slip.properties.id]
            
            # Check title consistency
            if db_info['title'] != slip.properties.title:
                violations.append(Violation(
                    rule="TITLE_MISMATCH_DATABASE",
                    message=f"Title mismatch with database. "
                           f"Slip: '{slip.properties.title}', "
                           f"Database: '{db_info['title']}'",
                    severity=Severity.INFO
                ))
        
        # Check headline nodes
        if slip.headline_nodes:
            for node in slip.headline_nodes:
                if node.properties.id and node.properties.id not in self.db_nodes:
                    violations.append(Violation(
                        rule="HEADLINE_MISSING_FROM_DATABASE",
                        message=f"Headline node '{node.title}' (ID: {node.properties.id}) "
                               f"not in database",
                        line_number=node.line_number,
                        severity=Severity.WARNING
                    ))
        
        return violations


class CacheStalenessValidator(BaseValidator):
    """Detects potential org-roam cache staleness issues."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with database path."""
        self.db_path = db_path
        self.db_mtime: Optional[datetime] = None
        
        if self.db_path and self.db_path.exists():
            self.db_mtime = datetime.fromtimestamp(self.db_path.stat().st_mtime)
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check if file is newer than database."""
        violations = []
        
        if not self.db_mtime:
            return violations
        
        file_mtime = datetime.fromtimestamp(slip.file_path.stat().st_mtime)
        
        if file_mtime > self.db_mtime:
            time_diff = file_mtime - self.db_mtime
            violations.append(Violation(
                rule="FILE_NEWER_THAN_DATABASE",
                message=f"File modified {time_diff} after last database sync. "
                       f"Consider running 'M-x org-roam-db-sync'.",
                severity=Severity.INFO
            ))
        
        return violations


class PerformanceAdvisor(BaseValidator):
    """Provides performance advice based on slipbox size and structure."""
    
    def __init__(self, total_slips: int = 0):
        """Initialize with total slip count."""
        self.total_slips = total_slips
        self.link_count = 0
        self.node_count = 0
    
    def set_counts(self, total_slips: int, link_count: int, node_count: int):
        """Set counts for performance analysis."""
        self.total_slips = total_slips
        self.link_count = link_count
        self.node_count = node_count
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Provide performance advice for large slips."""
        violations = []
        
        # Check for slips with many links
        if len(slip.links) > 50:
            violations.append(Violation(
                rule="HIGH_LINK_COUNT",
                message=f"Slip has {len(slip.links)} links. "
                       f"Consider splitting or using headline nodes.",
                severity=Severity.INFO
            ))
        
        # Check for slips with many headline nodes
        if slip.headline_nodes and len(slip.headline_nodes) > 20:
            violations.append(Violation(
                rule="HIGH_NODE_COUNT",
                message=f"Slip has {len(slip.headline_nodes)} headline nodes. "
                       f"This may impact org-roam performance.",
                severity=Severity.INFO
            ))
        
        # Global advice (only on first slip to avoid spam)
        if self.total_slips > 1000 and slip.file_path.name.startswith("2025-06-05"):
            if self.total_slips > 5000:
                violations.append(Violation(
                    rule="LARGE_SLIPBOX_ADVICE",
                    message=f"Slipbox has {self.total_slips} slips. "
                           f"Consider: 1) Using SQLite full-text search, "
                           f"2) Enabling org-roam-db-autosync-mode, "
                           f"3) Increasing gc-cons-threshold in Emacs.",
                    severity=Severity.INFO
                ))
        
        return violations


class ConsistencyValidator(BaseValidator):
    """Meta-validator for database consistency checks."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with optional database path."""
        self.db_validator = DatabaseConsistencyValidator(db_path)
        self.staleness_validator = CacheStalenessValidator(db_path)
        self.performance_advisor = PerformanceAdvisor()
        
        self.validators = [
            self.db_validator,
            self.staleness_validator,
            self.performance_advisor
        ]
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all consistency validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations
    
    def set_performance_counts(self, total_slips: int, link_count: int, node_count: int):
        """Set counts for performance advisor."""
        self.performance_advisor.set_counts(total_slips, link_count, node_count)