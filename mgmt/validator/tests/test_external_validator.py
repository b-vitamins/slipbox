"""Tests for external resource validators."""

import pytest
from pathlib import Path
import tempfile
import shutil

from validator.validators.external import (
    BibliographyValidator,
    ExternalURLValidator,
    MediaFileValidator
)
from validator.models import Slip, SlipProperties, Link, LinkType, Severity


class TestBibliographyValidator:
    """Test cases for BibliographyValidator."""

    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.bibliography_dir = Path(self.temp_dir) / "bibliography"
        self.bibliography_dir.mkdir()
        
        # Create test .bib file
        bib_content = """
@article{luhmann1992,
    title={Communicating with Slip Boxes},
    author={Luhmann, Niklas},
    journal={Sociologia Internationalis},
    year={1992}
}

@book{alexander2002,
    title={A Pattern Language},
    author={Alexander, Christopher},
    year={2002}
}
"""
        with open(self.bibliography_dir / "test.bib", 'w') as f:
            f.write(bib_content)
        
        self.validator = BibliographyValidator(self.bibliography_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_valid_bibliography_link(self):
        """Test slip with valid bibliography reference."""
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # Link to existing bibliography entry
        link = Link(
            source_slip="id1",
            target="cite:luhmann1992",
            link_type=LinkType.BIBLIOGRAPHY,
            line_number=5,
            context="Reference to [[cite:luhmann1992][Luhmann's paper]]"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_missing_bibliography_entry(self):
        """Test slip with missing bibliography reference."""
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # Link to non-existent bibliography entry
        link = Link(
            source_slip="id1",
            target="cite:nonexistent",
            link_type=LinkType.BIBLIOGRAPHY,
            line_number=5,
            context="Reference to [[cite:nonexistent][Missing paper]]"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "MISSING_BIBLIOGRAPHY_ENTRY"
        assert violations[0].severity == Severity.ERROR
        assert "nonexistent" in violations[0].message

    def test_bibliography_without_cite_prefix(self):
        """Test bibliography link without cite: prefix."""
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # Link with bare citation key (no cite: prefix)
        link = Link(
            source_slip="id1",
            target="alexander2002",  # No cite: prefix
            link_type=LinkType.BIBLIOGRAPHY,
            line_number=5,
            context="Reference to alexander2002"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0


class TestExternalURLValidator:
    """Test cases for ExternalURLValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ExternalURLValidator(check_urls=True, timeout_seconds=5)

    def test_valid_url_format(self):
        """Test with valid URL format (but don't actually check reachability)."""
        # Use validator that doesn't check URLs for this test
        validator = ExternalURLValidator(check_urls=False)
        
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        link = Link(
            source_slip="id1",
            target="https://example.com",
            link_type=LinkType.EXTERNAL,
            line_number=5,
            context="Link to [[https://example.com][Example]]"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 0

    def test_url_checking_disabled(self):
        """Test that URL checking can be disabled."""
        validator = ExternalURLValidator(check_urls=False)
        
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # This URL definitely doesn't exist
        link = Link(
            source_slip="id1",
            target="https://definitely-does-not-exist-12345.com",
            link_type=LinkType.EXTERNAL,
            line_number=5,
            context="Link to non-existent site"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 0  # Should be 0 because checking is disabled


class TestMediaFileValidator:
    """Test cases for MediaFileValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.slipbox_root = Path(self.temp_dir)
        
        # Create test media file
        self.media_dir = self.slipbox_root / "assets"
        self.media_dir.mkdir()
        
        test_file = self.media_dir / "test-image.png"
        test_file.write_text("fake image content")
        
        self.validator = MediaFileValidator(self.slipbox_root)

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_existing_media_file(self):
        """Test slip with link to existing media file."""
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # Link to existing file
        link = Link(
            source_slip="id1",
            target="file:assets/test-image.png",
            link_type=LinkType.MEDIA,
            line_number=5,
            context="Image: [[file:assets/test-image.png][Test Image]]"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_missing_media_file(self):
        """Test slip with link to missing media file."""
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # Link to non-existent file
        link = Link(
            source_slip="id1",
            target="file:assets/missing-image.png",
            link_type=LinkType.MEDIA,
            line_number=5,
            context="Image: [[file:assets/missing-image.png][Missing Image]]"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "MISSING_MEDIA_FILE"
        assert violations[0].severity == Severity.ERROR
        assert "missing-image.png" in violations[0].message

    def test_media_file_without_file_prefix(self):
        """Test media file link without file: prefix."""
        properties = SlipProperties(
            id="id1",
            custom_id="1/1",
            title="Test Slip",
            filetags=["test"]
        )
        
        # Link without file: prefix
        link = Link(
            source_slip="id1",
            target="assets/test-image.png",  # No file: prefix
            link_type=LinkType.MEDIA,
            line_number=5,
            context="Image: assets/test-image.png"
        )
        
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[link],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0  # Should find the file even without prefix