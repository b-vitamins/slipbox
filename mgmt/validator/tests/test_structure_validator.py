"""Tests for structure validators."""

import pytest
from pathlib import Path
from validator.validators.structure import (
    RequiredPropertiesValidator,
    LuhmannNumberValidator,
    WordCountValidator,
    RoamPropertiesValidator
)
from validator.models import Slip, SlipProperties, Severity


class TestRequiredPropertiesValidator:
    """Test cases for RequiredPropertiesValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RequiredPropertiesValidator()

    def test_valid_properties(self):
        """Test slip with all required properties."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept", "logic"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_missing_id(self):
        """Test slip with missing ID."""
        properties = SlipProperties(
            id="",  # Missing ID
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "MISSING_ID"
        assert violations[0].severity == Severity.ERROR

    def test_invalid_uuid(self):
        """Test slip with invalid UUID."""
        properties = SlipProperties(
            id="not-a-uuid",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "INVALID_ID"
        assert violations[0].severity == Severity.ERROR

    def test_missing_custom_id_org_roam_priority(self):
        """Test slip with missing CUSTOM_ID in Org-roam priority mode (default)."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="",  # Missing CUSTOM_ID
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "MISSING_CUSTOM_ID"
        assert violations[0].severity == Severity.WARNING  # Warning in org-roam mode

    def test_missing_custom_id_non_org_roam_mode(self):
        """Test slip with missing CUSTOM_ID in non-Org-roam mode."""
        validator = RequiredPropertiesValidator(org_roam_priority=False, require_custom_id=True)
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="",  # Missing CUSTOM_ID
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "MISSING_CUSTOM_ID"
        assert violations[0].severity == Severity.ERROR  # Error in non-Org-roam mode

    def test_missing_custom_id_not_required(self):
        """Test slip with missing CUSTOM_ID when CUSTOM_ID not required."""
        validator = RequiredPropertiesValidator(org_roam_priority=True, require_custom_id=False)
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="",  # Missing CUSTOM_ID
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 0  # No violation when CUSTOM_ID not required

    def test_missing_filetags(self):
        """Test slip with missing filetags."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=[]  # Empty filetags
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "EMPTY_FILETAGS"
        assert violations[0].severity == Severity.WARNING


class TestLuhmannNumberValidator:
    """Test cases for LuhmannNumberValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = LuhmannNumberValidator()

    def test_valid_luhmann_numbers(self):
        """Test various valid Luhmann number formats."""
        valid_numbers = ["42", "42/3", "42/3a", "42/3a1", "57/12/5b2"]
        
        for custom_id in valid_numbers:
            properties = SlipProperties(
                id="550e8400-e29b-41d4-a716-446655440000",
                custom_id=custom_id,
                title="Test Slip",
                filetags=["concept"]
            )
            slip = Slip(
                file_path=Path("test.org"),
                properties=properties,
                content="test content",
                links=[],
                word_count=2,
                connection_points=[]
            )
            
            violations = self.validator.validate(slip)
            assert len(violations) == 0, f"Failed for {custom_id}"

    def test_invalid_luhmann_numbers(self):
        """Test invalid Luhmann number formats."""
        invalid_numbers = ["abc", "42/", "42/a", "/42", "42//3", "42/3A"]
        
        for custom_id in invalid_numbers:
            properties = SlipProperties(
                id="550e8400-e29b-41d4-a716-446655440000",
                custom_id=custom_id,
                title="Test Slip",
                filetags=["concept"]
            )
            slip = Slip(
                file_path=Path("test.org"),
                properties=properties,
                content="test content",
                links=[],
                word_count=2,
                connection_points=[]
            )
            
            violations = self.validator.validate(slip)
            assert len(violations) == 1, f"Should fail for {custom_id}"
            assert violations[0].rule == "INVALID_LUHMANN_NUMBER"


class TestWordCountValidator:
    """Test cases for WordCountValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = WordCountValidator(word_limit=10)  # Low limit for testing

    def test_under_limit(self):
        """Test slip under word limit."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=5,  # Under limit
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_over_limit(self):
        """Test slip over word limit."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=15,  # Over limit
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "WORD_LIMIT_EXCEEDED"
        assert violations[0].severity == Severity.ERROR

    def test_extended_tag_exemption(self):
        """Test that :extended: tag exempts from word limit."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept", "extended"]  # Has extended tag
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=15,  # Over limit but should be exempt
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0


class TestRoamPropertiesValidator:
    """Test cases for RoamPropertiesValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RoamPropertiesValidator(check_duplicate_aliases=False)

    def test_valid_roam_aliases(self):
        """Test slip with valid ROAM_ALIASES."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"],
            roam_aliases=["AI", "Artificial Intelligence", "Machine Learning"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_invalid_roam_aliases(self):
        """Test slip with invalid ROAM_ALIASES."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"],
            roam_aliases=["Valid Alias", "", "!!!"]  # Empty and invalid aliases
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 2  # Empty string and "!!!"
        assert all(v.rule == "INVALID_ROAM_ALIAS" for v in violations)
        assert all(v.severity == Severity.WARNING for v in violations)

    def test_valid_roam_refs(self):
        """Test slip with valid ROAM_REFS."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"],
            roam_refs=["@smith2023paper", "https://example.com", "author2024theory"]
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0

    def test_invalid_roam_refs(self):
        """Test slip with invalid ROAM_REFS."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"],
            roam_refs=["@", "ht", "123"]  # Invalid formats
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 3
        assert all(v.rule == "INVALID_ROAM_REFS" for v in violations)
        assert all(v.severity == Severity.WARNING for v in violations)

    def test_duplicate_aliases_detection(self):
        """Test duplicate aliases detection across slips."""
        validator = RoamPropertiesValidator(check_duplicate_aliases=True)
        
        # Set up alias map as if another slip has "AI" alias
        all_aliases = {
            "/path/to/other.org": ["AI", "Artificial Intelligence"],
            "/path/to/current.org": []  # Current slip
        }
        validator.set_all_aliases(all_aliases)
        
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a", 
            title="Test Slip",
            filetags=["concept"],
            roam_aliases=["AI", "Machine Learning"]  # "AI" duplicates other slip
        )
        slip = Slip(
            file_path=Path("/path/to/current.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = validator.validate(slip)
        assert len(violations) == 1
        assert violations[0].rule == "DUPLICATE_ROAM_ALIAS"
        assert "AI" in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_no_roam_properties(self):
        """Test slip without ROAM properties."""
        properties = SlipProperties(
            id="550e8400-e29b-41d4-a716-446655440000",
            custom_id="42/3a",
            title="Test Slip",
            filetags=["concept"]
            # No roam_aliases or roam_refs
        )
        slip = Slip(
            file_path=Path("test.org"),
            properties=properties,
            content="test content",
            links=[],
            word_count=2,
            connection_points=[]
        )
        
        violations = self.validator.validate(slip)
        assert len(violations) == 0