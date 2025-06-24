# Slipbox Validation Architecture

*Software Architecture Document for implementing slipbox validation tools*

## Data Models

### Slip Representation
```python
@dataclass
class Slip:
    file_path: Path
    properties: SlipProperties
    content: str
    links: List[Link]
    word_count: int
    connection_points: List[ConnectionPoint]
    
@dataclass 
class SlipProperties:
    id: str              # UUID, never changes
    custom_id: str       # Luhmann number (42/3a)
    title: str           # Clear, searchable title
    filetags: List[str]  # Type and domain tags
    created: datetime    # Optional timestamp
```

### Link Types
```python
@dataclass
class Link:
    source_slip: str     # Source slip ID
    target: str          # Target (slip ID, URL, file path, etc.)
    link_type: LinkType  # INTERNAL, EXTERNAL, BIBLIOGRAPHY, MEDIA
    line_number: int     # Location in source slip
    context: str         # Surrounding text for validation

enum LinkType:
    INTERNAL     # [[id:UUID][Description]] or [[CUSTOM_ID][Description]]  
    EXTERNAL     # [[URL][Description]]
    BIBLIOGRAPHY # [[cite:key][Description]]
    MEDIA        # [[file:path][Description]]
```

### Connection Points
```python
@dataclass  
class ConnectionPoint:
    line_number: int
    marker: str          # What marks this connection (red text equivalent)
    branches: List[str]  # Slip IDs that branch from this point
```

### Validation Results
```python
@dataclass
class ValidationResult:
    file_path: Path
    passed: bool
    violations: List[Violation]
    warnings: List[Warning]

@dataclass
class Violation:
    rule: str           # "WORD_LIMIT", "MISSING_PROPERTY", etc.
    message: str        # Human readable description  
    line_number: int    # Location of violation
    severity: Severity  # ERROR, WARNING, INFO
```

## Validation Rules (Precise Specifications)

### Required Properties
- **Rule**: `REQUIRED_PROPERTIES`
- **Spec**: Every `.org` file in `slips/` must have properties block with:
  - `:ID:` field containing valid UUID
  - `:CUSTOM_ID:` field containing Luhmann number pattern `\d+(/\d+)*[a-z]*\d*`
  - `#+TITLE:` line immediately after properties block
  - `#+FILETAGS:` line with at least one tag
- **Validation**: Regex parsing of properties block, UUID validation
- **Error**: Missing required property, malformed UUID, invalid Luhmann number

### Word Count Limit
- **Rule**: `WORD_LIMIT`
- **Spec**: Content (excluding properties block, title, filetags) ≤ 500 words
- **Word Definition**: Whitespace-separated tokens, excluding:
  - Org markup (`*bold*`, `/italic/`, `=code=`)
  - Link syntax (`[[target][description]]`) 
  - Property blocks and metadata
- **Exceptions**: Slips tagged with `:extended:` or `:sequence:`
- **Validation**: Token counting after markup removal
- **Error**: Word count with actual vs limit

### Connection Point Marking  
- **Rule**: `CONNECTION_POINTS`
- **Spec**: When content references connection points, must be marked clearly
- **Valid Markers**: 
  - `→ 57/12a` (arrow to Luhmann number)
  - `[→57/12a]` (bracketed reference)
  - `@@connection: 57/12a@@` (org macro style)
- **Validation**: Pattern matching, verify referenced slips exist
- **Warning**: Unmarked apparent connections (heuristic detection)

### Link Integrity
- **Rule**: `LINK_INTEGRITY` 
- **Spec**: All internal links must resolve to existing slips or valid external resources
- **Internal Links**: `[[id:UUID]]` or `[[CUSTOM_ID]]` must reference existing slip
- **External Links**: HTTP URLs must be reachable (optional validation)
- **Bibliography Links**: `[[cite:key]]` must exist in `.bib` files
- **Media Links**: File paths must exist relative to repository root
- **Validation**: Graph traversal, HTTP HEAD requests, file system checks
- **Error**: Broken internal link, missing bibliography entry, missing file

### Bidirectional Linking
- **Rule**: `BIDIRECTIONAL_LINKS`
- **Spec**: For every link A→B, should have back-link B→A (warning, not error)
- **Detection**: Build graph of all links, identify unidirectional edges
- **Validation**: Graph analysis to find missing back-links
- **Warning**: Suggest creating back-link (not enforced)

### Orphan Detection  
- **Rule**: `ORPHAN_DETECTION`
- **Spec**: Slips with zero incoming or outgoing links
- **Exception**: Recently created slips (< 7 days) or tagged `:fleeting:`
- **Validation**: Graph analysis for isolated nodes
- **Warning**: List orphaned slips for manual review

## Module Design

### Core Components

```python
# slipbox_validator/
├── __init__.py
├── cli.py              # Command-line interface
├── models.py           # Data models (Slip, Link, etc.)
├── parser.py           # Org file parsing  
├── validators/         # Validation rule implementations
│   ├── __init__.py
│   ├── structure.py    # Properties, word count
│   ├── links.py        # Link integrity, bidirectional
│   ├── network.py      # Orphan detection, graph analysis
│   └── content.py      # Connection points, formatting
├── reporters/          # Output formatting
│   ├── __init__.py  
│   ├── console.py      # Terminal output
│   ├── json.py         # Machine-readable output
│   └── html.py         # Web dashboard (future)
└── utils.py            # Common utilities
```

### Parser Module
```python
class OrgParser:
    def parse_slip(self, file_path: Path) -> Slip:
        """Parse org file into Slip object"""
        
    def extract_properties(self, content: str) -> SlipProperties:
        """Extract :PROPERTIES: block"""
        
    def extract_links(self, content: str) -> List[Link]:
        """Find all [[link][desc]] patterns"""
        
    def count_words(self, content: str) -> int:
        """Count words excluding markup"""
        
    def find_connection_points(self, content: str) -> List[ConnectionPoint]:
        """Detect marked connection points"""
```

### Validator Framework
```python
class BaseValidator:
    def validate(self, slip: Slip) -> List[Violation]:
        """Override in subclasses"""
        
class ValidationEngine:
    def __init__(self, validators: List[BaseValidator]):
        self.validators = validators
        
    def validate_slip(self, slip: Slip) -> ValidationResult:
        """Run all validators on single slip"""
        
    def validate_slipbox(self, slips_dir: Path) -> List[ValidationResult]:
        """Validate entire slipbox"""
```

## CLI Specification

### Command Structure
```bash
slipbox-validate [COMMAND] [OPTIONS] [ARGS]
```

### Commands
```bash
# Validate all slips
slipbox-validate check [--fix] [--format=console|json] [PATH]

# Specific validation types  
slipbox-validate structure [PATH]     # Properties, word count
slipbox-validate links [PATH]         # Link integrity
slipbox-validate network [PATH]       # Orphans, graph analysis
slipbox-validate content [PATH]       # Connection points, formatting

# Maintenance operations
slipbox-validate orphans [PATH]       # Find orphaned slips
slipbox-validate backlinks [PATH]     # Suggest missing back-links
slipbox-validate health [PATH]        # Overall health report

# Utilities
slipbox-validate stats [PATH]         # Count slips, links, words
slipbox-validate graph [PATH]         # Export graph data
```

### Options
```bash
--config FILE       # Configuration file path
--format FORMAT     # Output format: console, json, html
--fix              # Auto-fix violations when possible
--strict           # Treat warnings as errors
--include PATTERN  # Only validate matching files
--exclude PATTERN  # Skip matching files  
--verbose, -v      # Verbose output
--quiet, -q        # Suppress non-error output
--no-external      # Skip external link validation
```

### Exit Codes
```bash
0   # Success, no violations
1   # Validation errors found
2   # Command-line argument errors
3   # File system errors (missing directory, etc.)
```

### Configuration File
```toml
# slipbox.toml
[validation]
word_limit = 500
require_backlinks = false
check_external_links = true
orphan_grace_period_days = 7

[paths]
slips_dir = "slips/"
bibliography_dir = "bibliography/"
media_dir = "assets/"

[output]
format = "console"
show_line_numbers = true
highlight_violations = true
```

## Implementation Priorities

### Phase 1: Core Structure Validation
**Goal**: Basic slip format compliance
**Scope**: 
- Required properties validation
- Word count checking
- Basic org file parsing
- Console output

**Deliverables**:
- `slipbox-validate structure`
- Basic violation reporting
- Configuration file support

### Phase 2: Link Validation  
**Goal**: Internal consistency
**Scope**:
- Link integrity checking
- Orphan detection
- Bidirectional link analysis
- Graph construction

**Deliverables**:
- `slipbox-validate links`
- `slipbox-validate orphans`
- Network analysis utilities

### Phase 3: Content Validation
**Goal**: Connection point compliance
**Scope**:
- Connection point detection
- Content formatting rules
- Bibliography integration
- External link checking

**Deliverables**:
- `slipbox-validate content`
- Bibliography validation
- Media file checking

### Phase 4: Maintenance Tools
**Goal**: Ongoing slipbox health
**Scope**:
- Health dashboards
- Automated reports
- Integration with git hooks
- Performance optimization

**Deliverables**:
- `slipbox-validate health`
- HTML reports
- Git hook integration
- Scheduled validation

## Testing Strategy

### Unit Tests
- Parser functions (properties, links, word counting)
- Individual validators
- Utility functions
- Error handling

### Integration Tests  
- Full validation runs on sample slipboxes
- CLI command execution
- Configuration file handling
- Output format generation

### Test Data
- Sample slips with various violations
- Valid slips covering edge cases
- Broken link scenarios
- Large slipbox performance testing

## Error Handling

### Graceful Degradation
- Skip unreadable files with warning
- Continue validation on parser errors
- Provide partial results when possible

### Error Categories
- **Fatal**: Cannot continue (missing slips directory)
- **Error**: Validation rule violation  
- **Warning**: Potential issue (missing back-link)
- **Info**: Informational (orphan slip)

### User Experience
- Clear error messages with line numbers
- Actionable suggestions for fixes
- Progress indicators for large slipboxes
- Colored output for better readability