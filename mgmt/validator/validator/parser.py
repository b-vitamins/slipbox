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
        roam_aliases_match = re.search(r':ROAM_ALIASES:\s*([^\n]+)', props_content)
        roam_refs_match = re.search(r':ROAM_REFS:\s*([^\n]+)', props_content)
        
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
        
        # Parse ROAM_ALIASES (space-separated values)
        roam_aliases = []
        if roam_aliases_match:
            aliases_str = roam_aliases_match.group(1).strip()
            # Handle both quoted and unquoted aliases
            if aliases_str.startswith('"') and aliases_str.endswith('"'):
                aliases_str = aliases_str[1:-1]  # Remove quotes
            roam_aliases = [alias.strip() for alias in aliases_str.split() if alias.strip()]
        
        # Parse ROAM_REFS (space-separated values)
        roam_refs = []
        if roam_refs_match:
            refs_str = roam_refs_match.group(1).strip()
            # Handle both quoted and unquoted refs
            if refs_str.startswith('"') and refs_str.endswith('"'):
                refs_str = refs_str[1:-1]  # Remove quotes
            roam_refs = [ref.strip() for ref in refs_str.split() if ref.strip()]
        
        return SlipProperties(
            id=id_match.group(1).strip() if id_match else "",
            custom_id=custom_id_match.group(1).strip() if custom_id_match else "",
            title=title_match.group(1).strip() if title_match else "",
            filetags=filetags,
            roam_aliases=roam_aliases if roam_aliases else None,
            roam_refs=roam_refs if roam_refs else None
        )

    def extract_links(self, content: str) -> List[Link]:
        """Find all [[link][desc]] patterns in content, excluding code blocks."""
        links = []
        
        # Pattern for org links: [[target][description]] or [[target]]
        link_pattern = r'\[\[([^\]]+)\](?:\[([^\]]*)\])?\]'
        
        lines = content.split('\n')
        in_code_block = False
        
        for line_num, line in enumerate(lines, 1):
            # Track code block boundaries
            if line.strip().startswith('#+begin_'):
                in_code_block = True
                continue
            elif line.strip().startswith('#+end_'):
                in_code_block = False
                continue
            
            # Skip link extraction inside code blocks
            if in_code_block:
                continue
                
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
        elif target.startswith('cite:'):  # Both cite:key and cite:@key
            return LinkType.BIBLIOGRAPHY
        elif target.startswith('file:'):
            return LinkType.MEDIA
        elif re.match(r'^\d+(/\d+)*[a-z]*\d*$', target):  # Luhmann number
            return LinkType.INTERNAL
        else:
            # Default to internal for custom IDs
            return LinkType.INTERNAL

    def count_words(self, content: str) -> int:
        """Count words excluding markup, metadata, and code blocks."""
        lines = content.split('\n')
        content_lines = []
        in_code_block = False
        
        for line in lines:
            # Track code block boundaries and exclude code block content
            if line.strip().startswith('#+begin_'):
                in_code_block = True
                continue
            elif line.strip().startswith('#+end_'):
                in_code_block = False
                continue
            
            # Skip content inside code blocks
            if in_code_block:
                continue
                
            content_lines.append(line)
        
        # Rejoin content without code blocks
        content = '\n'.join(content_lines)
        
        # Remove properties block
        content = re.sub(r':PROPERTIES:.*?:END:', '', content, flags=re.DOTALL)
        
        # Remove title and filetags
        content = re.sub(r'#\+TITLE:.*?\n', '', content)
        content = re.sub(r'#\+FILETAGS:.*?\n', '', content)
        content = re.sub(r'#\+SETUPFILE:.*?\n', '', content)
        
        # Remove other org directives
        content = re.sub(r'#\+[A-Z_]+:.*?\n', '', content)
        
        # Remove org markup (preserve content, remove formatting)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)  # *bold*
        content = re.sub(r'/([^/]+)/', r'\1', content)    # /italic/
        content = re.sub(r'=([^=]+)=', r'\1', content)    # =code=
        content = re.sub(r'~([^~]+)~', r'\1', content)    # ~verbatim~
        
        # Remove links but keep description (more precise regex)
        content = re.sub(r'\[\[[^\[\]]+\]\[([^\[\]]*)\]\]', r'\1', content)  # [[link][desc]] -> desc
        content = re.sub(r'\[\[([^\[\]]+)\]\]', '', content)  # [[link]] -> remove
        
        # Remove org headers (*, **, ***, etc.)
        content = re.sub(r'^[*]+ ', '', content, flags=re.MULTILINE)
        
        # Count words (whitespace-separated tokens)
        words = content.split()
        return len([word for word in words if word.strip()])

    def find_connection_points(self, content: str) -> List[ConnectionPoint]:
        """Detect marked connection points in content."""
        connection_points = []
        
        # Patterns for connection markers (ordered by specificity to avoid overlaps)
        patterns = [
            (r'\[→(\d+(/\d+)*[a-z]*\d*)\]', 1),     # [→57/12a] - more specific, check first
            (r'@@connection:\s*([^@]+)@@', 1),       # @@connection: 57/12a@@
            (r'(?<!\[)→\s*(\d+(/\d+)*[a-z]*\d*)', 1)  # → 57/12a - but not [→ (negative lookbehind)
        ]
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Track what's already matched to avoid overlaps
            matched_ranges = []
            
            for pattern, group_idx in patterns:
                for match in re.finditer(pattern, line):
                    start, end = match.span()
                    
                    # Check if this overlaps with already matched ranges
                    overlaps = any(start < m_end and end > m_start for m_start, m_end in matched_ranges)
                    
                    if not overlaps:
                        target = match.group(group_idx)
                        connection_points.append(ConnectionPoint(
                            line_number=line_num,
                            marker=match.group(0),
                            branches=[target]
                        ))
                        matched_ranges.append((start, end))
        
        return connection_points