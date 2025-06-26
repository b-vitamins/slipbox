"""Tests for link validators."""

import pytest
from pathlib import Path
import tempfile
import os

from validator.validators.links import (
    InternalLinkValidator,
    OrphanDetector
)
from validator.models import Slip, SlipProperties, Link, LinkType, Severity


class TestInternalLinkValidator:
    """Test cases for InternalLinkValidator."""

    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.slips_dir = Path(self.temp_dir)
        
        # Create test slips
        self._create_test_slip("slip1.org", "id1", "1/1", "Test Slip 1")
        self._create_test_slip("slip2.org", "id2", "1/2", "Test Slip 2")
        
        self.validator = InternalLinkValidator(self.slips_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_slip(self, filename: str, slip_id: str, custom_id: str, title: str):
        """Create a test slip file."""
        content = f"""
:PROPERTIES:
:ID: {slip_id}
:CUSTOM_ID: {custom_id}
:END:
#+TITLE: {title}
#+FILETAGS: :test:

Test content.
"""
        slip_path = self.slips_dir / filename
        with open(slip_path, 'w') as f:
            f.write(content)

    def test_valid_internal_link(self):
        """Test slip with valid internal link."""
        # Create a slip that links to existing slip
        properties = SlipProperties(
            id="id3",
            custom_id="1/3",
            title="Test Slip 3",
            filetags=["test"]
        )
        
        # Link to existing slip by ID
        link = Link(
            source_slip="id3",
            target="id:id1",  # Links to slip1
            link_type=LinkType.INTERNAL,
            line_number=5,
            context="Link to [[id:id1][Test Slip 1]]"
        )
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_valid_custom_id_link(self):
        """Test slip with valid custom ID link."""
        properties = SlipProperties(
            id="id3",
            custom_id="1/3",
            title="Test Slip 3",
            filetags=["test"]
        )
        
        # Link to existing slip by custom ID
        link = Link(
            source_slip="id3",
            target="1/1",  # Links to slip1 by custom ID
            link_type=LinkType.INTERNAL,
            line_number=5,
            context="Link to [[1/1][Test Slip 1]]"
        )
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_broken_internal_link(self):
        """Test slip with broken internal link."""
        properties = SlipProperties(
            id="id3",
            custom_id="1/3",
            title="Test Slip 3",
            filetags=["test"]
        )
        
        # Link to non-existent slip
        link = Link(
            source_slip="id3",
            target="id:nonexistent",
            link_type=LinkType.INTERNAL,
            line_number=5,
            context="Link to [[id:nonexistent][Broken Link]]"
        )
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "BROKEN_INTERNAL_LINK"
        assert violations[0].severity == Severity.ERROR
        assert "nonexistent" in violations[0].message

    def test_broken_id_link_org_roam_priority(self):
        """Test broken ID link with Org-roam priority (ERROR)."""
        validator = InternalLinkValidator(self.slips_dir, org_roam_priority=True)
        
        properties = SlipProperties(
            id="id3",
            custom_id="1/3", 
            title="Test Slip 3",
            filetags=["test"]
        )
        
        # Broken ID link
        link = Link(
            source_slip="id3",
            target="id:nonexistent",
            link_type=LinkType.INTERNAL,
            line_number=5,
            context="Link to [[id:nonexistent][Broken ID Link]]"
        )
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "BROKEN_INTERNAL_LINK"
        assert violations[0].severity == Severity.ERROR
        assert "breaks Org-roam functionality" in violations[0].message

    def test_broken_luhmann_link_org_roam_priority(self):
        """Test broken Luhmann link with Org-roam priority (WARNING)."""
        validator = InternalLinkValidator(self.slips_dir, org_roam_priority=True)
        
        properties = SlipProperties(
            id="id3",
            custom_id="1/3",
            title="Test Slip 3", 
            filetags=["test"]
        )
        
        # Broken Luhmann link
        link = Link(
            source_slip="id3",
            target="99/99",  # Non-existent Luhmann number
            link_type=LinkType.INTERNAL,
            line_number=5,
            context="Link to [[99/99][Broken Luhmann Link]]"
        )
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "BROKEN_INTERNAL_LINK" 
        assert violations[0].severity == Severity.WARNING
        assert "human readable convenience" in violations[0].message

    def test_broken_link_non_org_roam_mode(self):
        """Test broken links in non-Org-roam mode (all ERROR)."""
        validator = InternalLinkValidator(self.slips_dir, org_roam_priority=False)
        
        properties = SlipProperties(
            id="id3",
            custom_id="1/3",
            title="Test Slip 3",
            filetags=["test"]
        )
        
        # Both ID and Luhmann links should be ERROR in non-Org-roam mode
        links = [
            Link(
                source_slip="id3",
                target="id:nonexistent",
                link_type=LinkType.INTERNAL,
                line_number=5,
                context="[[id:nonexistent][Broken ID]]"
            ),
            Link(
                source_slip="id3", 
                target="99/99",
                link_type=LinkType.INTERNAL,
                line_number=6,
                context="[[99/99][Broken Luhmann]]"
            )
        ]
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=links,
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 2
        assert all(v.rule == "BROKEN_INTERNAL_LINK" for v in violations)
        assert all(v.severity == Severity.ERROR for v in violations)

    def test_external_links_ignored(self):
        """Test that external links are not validated."""
        properties = SlipProperties(
            id="id3",
            custom_id="1/3",
            title="Test Slip 3",
            filetags=["test"]
        )
        
        # External link should be ignored
        link = Link(
            source_slip="id3",
            target="https://example.com",
            link_type=LinkType.EXTERNAL,
            line_number=5,
            context="Link to [[https://example.com][External Link]]"
        )
        
        slip = Slip(
            file_path=Path("slip3.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0


class TestOrphanDetector:
    """Test cases for OrphanDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.slips_dir = Path(self.temp_dir)
        
        # Create test slips with connections
        self._create_connected_slips()
        
        self.validator = OrphanDetector(self.slips_dir, grace_period_days=0)  # No grace period for testing

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_connected_slips(self):
        """Create test slips with connections."""
        # Slip 1 links to Slip 2
        slip1_content = """
:PROPERTIES:
:ID: id1
:CUSTOM_ID: 1/1
:END:
#+TITLE: Connected Slip 1
#+FILETAGS: :test:

This links to [[1/2][Slip 2]].
"""
        
        # Slip 2 links back to Slip 1
        slip2_content = """
:PROPERTIES:
:ID: id2
:CUSTOM_ID: 1/2
:END:
#+TITLE: Connected Slip 2
#+FILETAGS: :test:

This links back to [[1/1][Slip 1]].
"""
        
        # Orphaned slip with no connections
        orphan_content = """
:PROPERTIES:
:ID: id3
:CUSTOM_ID: 1/3
:END:
#+TITLE: Orphaned Slip
#+FILETAGS: :test:

This slip has no connections.
"""
        
        with open(self.slips_dir / "slip1.org", 'w') as f:
            f.write(slip1_content)
        with open(self.slips_dir / "slip2.org", 'w') as f:
            f.write(slip2_content)
        with open(self.slips_dir / "orphan.org", 'w') as f:
            f.write(orphan_content)

    def test_connected_slip_not_orphaned(self):
        """Test that connected slips are not marked as orphaned."""
        from validator.parser import OrgParser
        parser = OrgParser()
        
        # Test slip 1 (has outgoing link)
        slip1 = parser.parse_slip(self.slips_dir / "slip1.org")
        violations = self.validator.validate(slip1)
        
        orphan_violations = [v for v in violations if v.rule == "ORPHANED_SLIP"]
        assert len(orphan_violations) == 0

    def test_orphaned_slip_detected(self):
        """Test that orphaned slips are detected."""
        from validator.parser import OrgParser
        parser = OrgParser()
        
        # Test orphaned slip
        orphan_slip = parser.parse_slip(self.slips_dir / "orphan.org")
        violations = self.validator.validate(orphan_slip)
        
        orphan_violations = [v for v in violations if v.rule == "ORPHANED_SLIP"]
        assert len(orphan_violations) == 1
        assert orphan_violations[0].severity == Severity.WARNING

