"""Tests for the org file parser."""

import pytest
from validator.parser import OrgParser
from validator.models import LinkType


class TestOrgParser:
    """Test cases for OrgParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = OrgParser()

    def test_extract_properties(self):
        """Test properties block extraction."""
        content = """
:PROPERTIES:
:ID: 550e8400-e29b-41d4-a716-446655440000
:CUSTOM_ID: 42/3a
:END:
#+TITLE: Test Slip
#+FILETAGS: :concept:logic:

This is test content.
"""
        properties = self.parser.extract_properties(content)
        
        assert properties.id == "550e8400-e29b-41d4-a716-446655440000"
        assert properties.custom_id == "42/3a"
        assert properties.title == "Test Slip"
        assert properties.filetags == ["concept", "logic"]

    def test_extract_links(self):
        """Test link extraction."""
        content = """
This links to [[id:123][another slip]] and [[https://example.com][external site]].
Also references [[cite:luhmann1992][Luhmann's paper]] and [[42/5b][related concept]].
"""
        links = self.parser.extract_links(content)
        
        assert len(links) == 4
        assert links[0].target == "id:123"
        assert links[0].link_type == LinkType.INTERNAL
        assert links[1].target == "https://example.com"
        assert links[1].link_type == LinkType.EXTERNAL
        assert links[2].target == "cite:luhmann1992"
        assert links[2].link_type == LinkType.BIBLIOGRAPHY
        assert links[3].target == "42/5b"
        assert links[3].link_type == LinkType.INTERNAL

    def test_count_words(self):
        """Test word counting."""
        content = """
:PROPERTIES:
:ID: test-id
:END:
#+TITLE: Test Title
#+FILETAGS: :test:

This is *bold* and /italic/ text with =code= and [[link][description]].
That should be exactly ten words after markup removal.
"""
        word_count = self.parser.count_words(content)
        assert word_count == 19  # Excluding markup, properties, title, filetags

    def test_find_connection_points(self):
        """Test connection point detection."""
        content = """
This text has a connection → 57/12a here.
Another connection [→42/3b] in brackets.
And an @@connection: 23/5c@@ macro style.
"""
        connection_points = self.parser.find_connection_points(content)
        
        assert len(connection_points) == 3
        assert "57/12a" in connection_points[0].branches
        assert "42/3b" in connection_points[1].branches
        assert "23/5c" in connection_points[2].branches