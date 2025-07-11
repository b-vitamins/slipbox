"""Link validation for slips."""

from pathlib import Path
from typing import List, Dict, Set
import re

from .base import BaseValidator, is_autosave_or_backup
from ..models import Slip, Violation, Severity, LinkType
from ..parser import OrgParser


class InternalLinkValidator(BaseValidator):
    """Validates that internal links resolve to existing slips."""
    
    def __init__(self, slips_dir: Path, org_roam_priority: bool = True):
        """Initialize with slips directory to build slip index."""
        self.slips_dir = slips_dir
        self.org_roam_priority = org_roam_priority
        self.slip_index = self._build_slip_index()
    
    def _build_slip_index(self) -> Dict[str, Path]:
        """Build index of all slips by ID and CUSTOM_ID."""
        index = {}
        parser = OrgParser()
        
        if not self.slips_dir.exists():
            return index
        
        for org_file in self.slips_dir.glob("*.org"):
            if is_autosave_or_backup(org_file):
                continue
            try:
                slip = parser.parse_slip(org_file)
                
                # Index by UUID (without id: prefix)
                if slip.properties.id:
                    index[slip.properties.id] = org_file
                    index[f"id:{slip.properties.id}"] = org_file
                
                # Index by CUSTOM_ID (Luhmann number)
                if slip.properties.custom_id:
                    index[slip.properties.custom_id] = org_file
                
            except Exception:
                # Skip files that can't be parsed
                continue
        
        return index
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check that all internal links resolve to existing slips."""
        violations = []
        
        for link in slip.links:
            if link.link_type == LinkType.INTERNAL:
                if not self._link_resolves(link.target):
                    # Determine severity based on link type and Org-roam priority
                    severity, message = self._get_link_severity_and_message(link.target)
                    
                    violations.append(Violation(
                        rule="BROKEN_INTERNAL_LINK",
                        message=message,
                        line_number=link.line_number,
                        severity=severity
                    ))
        
        return violations
    
    def _get_link_severity_and_message(self, target: str) -> tuple[Severity, str]:
        """Get appropriate severity and message based on link type."""
        is_id_link = target.startswith('id:')
        
        if self.org_roam_priority:
            if is_id_link:
                # ID links are critical for Org-roam relationships
                return (Severity.ERROR, 
                       f"ID link does not resolve: [[{target}]] (breaks Org-roam functionality)")
            else:
                # Luhmann links are human readable convenience
                return (Severity.WARNING, 
                       f"Luhmann link does not resolve: [[{target}]] (human readable convenience)")
        else:
            # Non-Org-roam mode - all broken links are errors
            return (Severity.ERROR, f"Internal link does not resolve: [[{target}]]")
    
    def _link_resolves(self, target: str) -> bool:
        """Check if a link target resolves to an existing slip."""
        return target in self.slip_index


class OrphanDetector(BaseValidator):
    """Detects slips with no incoming or outgoing connections."""
    
    def __init__(self, slips_dir: Path, grace_period_days: int = 7):
        """Initialize with slips directory and grace period for new slips."""
        self.slips_dir = slips_dir
        self.grace_period_days = grace_period_days
        self.connection_graph = self._build_connection_graph()
    
    def _build_connection_graph(self) -> Dict[str, Set[str]]:
        """Build graph of connections between slips."""
        graph = {}
        parser = OrgParser()
        
        if not self.slips_dir.exists():
            return graph
        
        # First pass: collect all slip IDs
        slip_ids = set()
        slip_files = {}
        
        for org_file in self.slips_dir.glob("*.org"):
            if is_autosave_or_backup(org_file):
                continue
            try:
                slip = parser.parse_slip(org_file)
                slip_id = slip.properties.custom_id or slip.properties.id
                if slip_id:
                    slip_ids.add(slip_id)
                    slip_files[slip_id] = org_file
                    graph[slip_id] = set()
            except Exception:
                continue
        
        # Second pass: build connections
        for org_file in self.slips_dir.glob("*.org"):
            if is_autosave_or_backup(org_file):
                continue
            try:
                slip = parser.parse_slip(org_file)
                source_id = slip.properties.custom_id or slip.properties.id
                
                if not source_id:
                    continue
                
                for link in slip.links:
                    if link.link_type == LinkType.INTERNAL:
                        # Normalize link target
                        target = link.target
                        if target.startswith("id:"):
                            target = target[3:]  # Remove id: prefix
                        
                        if target in slip_ids:
                            graph[source_id].add(target)
                            # Also track reverse connections
                            if target not in graph:
                                graph[target] = set()
                            graph[target].add(source_id)
                            
            except Exception:
                continue
        
        return graph
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Check if slip is orphaned (no connections)."""
        violations = []
        
        slip_id = slip.properties.custom_id or slip.properties.id
        if not slip_id:
            return violations
        
        # Count outgoing connections from this slip
        outgoing = 0
        for link in slip.links:
            if link.link_type == LinkType.INTERNAL:
                outgoing += 1
        
        # Count incoming connections by checking if this slip ID appears in other slips' connections
        incoming = 0
        for other_id, other_connections in self.connection_graph.items():
            if other_id != slip_id and slip_id in other_connections:
                incoming += 1
        
        if outgoing == 0 and incoming == 0:
            # Check if slip is new (within grace period)
            slip_age_days = self._get_slip_age_days(slip.file_path)
            
            if slip_age_days >= self.grace_period_days:  # Changed > to >= for testing
                violations.append(Violation(
                    rule="ORPHANED_SLIP",
                    message=f"Slip has no incoming or outgoing connections "
                           f"(age: {slip_age_days} days, grace period: {self.grace_period_days} days)",
                    severity=Severity.WARNING
                ))
        
        return violations
    
    def _get_slip_age_days(self, file_path: Path) -> int:
        """Calculate age of slip in days based on file creation time."""
        try:
            import time
            file_time = file_path.stat().st_ctime
            current_time = time.time()
            age_seconds = current_time - file_time
            return int(age_seconds / (24 * 3600))
        except Exception:
            return 0  # Default to new file


class SlipLinkValidator(BaseValidator):
    """Meta-validator that runs all link validations."""
    
    def __init__(self, slips_dir: Path, grace_period_days: int = 7, org_roam_priority: bool = True):
        """Initialize with configuration."""
        self.validators = [
            InternalLinkValidator(slips_dir, org_roam_priority),
            OrphanDetector(slips_dir, grace_period_days)
        ]
    
    def validate(self, slip: Slip) -> List[Violation]:
        """Run all link validators."""
        violations = []
        
        for validator in self.validators:
            violations.extend(validator.validate(slip))
        
        return violations