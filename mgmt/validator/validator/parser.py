"""Org file parsing for slipbox validation."""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import Slip, SlipProperties, Link, LinkType, ConnectionPoint


class OrgParser:
    """Parser for Org-mode files containing slips."""

    def parse_slip(self, file_path: Path) -> Slip:
        """Parse an org file into a Slip object."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        properties = self.extract_properties(content)
        links = self.extract_links(content)
        word_count = self.count_words(content)
        connection_points = self.find_connection_points(content)

        return Slip(
            file_path=file_path,
            properties=properties,
            content=content,
            links=links,
            word_count=word_count,
            connection_points=connection_points
        )

    def extract_properties(self, content: str) -> SlipProperties:
        """Extract :PROPERTIES: block from org content."""
        # Match properties block
        props_pattern = r':PROPERTIES:\s*\n(.*?):END:'
        props_match = re.search(props_pattern, content, re.DOTALL)
        
        if not props_match:
            raise ValueError("No :PROPERTIES: block found")
        
        props_content = props_match.group(1)
        
        # Extract individual properties
        id_match = re.search(r':ID:\s*([^\n]+)', props_content)
        custom_id_match = re.search(r':CUSTOM_ID:\s*([^\n]+)', props_content)
        
        # Extract title
        title_match = re.search(r'#\+TITLE:\s*([^\n]+)', content)
        
        # Extract filetags
        filetags_match = re.search(r'#\+FILETAGS:\s*([^\n]+)', content)
        filetags = []
        if filetags_match:
            # Parse tags like :tag1:tag2:tag3:
            tags_str = filetags_match.group(1).strip()
            if tags_str.startswith(':') and tags_str.endswith(':'):
                filetags = [tag for tag in tags_str[1:-1].split(':') if tag]
        
        return SlipProperties(
            id=id_match.group(1).strip() if id_match else "",
            custom_id=custom_id_match.group(1).strip() if custom_id_match else "",
            title=title_match.group(1).strip() if title_match else "",
            filetags=filetags
        )

    def extract_links(self, content: str) -> List[Link]:
        """Find all [[link][desc]] patterns in content."""
        links = []
        
        # Pattern for org links: [[target][description]] or [[target]]
        link_pattern = r'\[\[([^\]]+)\](?:\[([^\]]*)\])?\]'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for match in re.finditer(link_pattern, line):
                target = match.group(1)
                description = match.group(2) or ""
                
                # Determine link type
                link_type = self._classify_link(target)
                
                links.append(Link(
                    source_slip="",  # Will be set by caller
                    target=target,
                    link_type=link_type,
                    line_number=line_num,
                    context=line.strip()
                ))
        
        return links

    def _classify_link(self, target: str) -> LinkType:
        """Classify a link target by its format."""
        if target.startswith('id:'):
            return LinkType.INTERNAL
        elif target.startswith('http://') or target.startswith('https://'):
            return LinkType.EXTERNAL
        elif target.startswith('cite:'):
            return LinkType.BIBLIOGRAPHY
        elif target.startswith('file:'):
            return LinkType.MEDIA
        elif re.match(r'^\d+(/\d+)*[a-z]*\d*$', target):  # Luhmann number
            return LinkType.INTERNAL
        else:
            # Default to internal for custom IDs
            return LinkType.INTERNAL

    def count_words(self, content: str) -> int:
        """Count words excluding markup and metadata."""
        # Remove properties block
        content = re.sub(r':PROPERTIES:.*?:END:', '', content, flags=re.DOTALL)
        
        # Remove title and filetags
        content = re.sub(r'#\+TITLE:.*?\n', '', content)
        content = re.sub(r'#\+FILETAGS:.*?\n', '', content)
        
        # Remove org markup
        content = re.sub(r'\*([^*]+)\*', r'\\1', content)  # *bold*
        content = re.sub(r'/([^/]+)/', r'\\1', content)    # /italic/
        content = re.sub(r'=([^=]+)=', r'\\1', content)    # =code=
        content = re.sub(r'~([^~]+)~', r'\\1', content)    # ~verbatim~
        
        # Remove links but keep description
        content = re.sub(r'\[\[[^\]]+\]\[([^\]]*)\]\]', r'\\1', content)
        content = re.sub(r'\[\[([^\]]+)\]\]', '', content)
        
        # Count words (whitespace-separated tokens)
        words = content.split()
        return len([word for word in words if word.strip()])

    def find_connection_points(self, content: str) -> List[ConnectionPoint]:
        """Detect marked connection points in content."""
        connection_points = []
        
        # Patterns for connection markers
        patterns = [
            r'→\s*(\d+(/\d+)*[a-z]*\d*)',      # → 57/12a
            r'\[→(\d+(/\d+)*[a-z]*\d*)\]',     # [→57/12a]
            r'@@connection:\s*([^@]+)@@'        # @@connection: 57/12a@@
        ]
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    target = match.group(1)
                    connection_points.append(ConnectionPoint(
                        line_number=line_num,
                        marker=match.group(0),
                        branches=[target]
                    ))
        
        return connection_points