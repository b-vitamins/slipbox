"""Tests for structure validators."""

import pytest
from pathlib import Path
from validator.validators.structure import (
    RequiredPropertiesValidator,
    LuhmannNumberValidator,
    WordCountValidator
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