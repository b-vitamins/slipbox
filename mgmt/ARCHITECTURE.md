# Management System Architecture

*High-level design for slipbox infrastructure and tooling*

## System Overview

The management workspace provides infrastructure that supports the Zettelkasten intellectual work. Multiple independent projects collaborate through shared conventions and data formats.

```
slipbox/                    # Zettelkasten (primary system)
├── slips/                  # Intellectual content
├── bibliography/           # Academic sources
└── mgmt/                   # Management infrastructure
    ├── validator/          # Format compliance (Python)
    ├── analyzer/           # Graph analysis (future: Rust/C++)
    ├── ui/                 # Conversational interface (future: TypeScript)
    └── scripts/            # Utilities (future: Shell)
```

## Design Principles

### Separation of Concerns
- **Each project solves one problem well** - Validation, analysis, interaction, utilities
- **Independent development cycles** - Projects can evolve at different rates
- **Language optimization** - Use best tool for each domain (Python/data, Rust/performance, TypeScript/UI)

### Shared Foundations
- **Common conventions** - All tools implement same slip format requirements
- **Compatible data models** - Consistent representation of slips, links, properties
- **Unified validation** - Single source of truth for what constitutes valid slipbox

### Integration Points
- **File system interface** - All tools read/write same slip files
- **Configuration sharing** - Common settings via `slipbox.toml`
- **Data exchange** - JSON/structured formats for tool interoperability

## Component Architecture

### Data Layer

**Slip Repository** (File System)
```
slips/
├── 2025-06-24-concept-emergence.org     # Individual slip files
├── 2025-06-24-luhmann-principles.org    # Standard org format
└── ...                                  # Flat structure, UUID-named
```

**Configuration** (`slipbox.toml`)
```toml
[validation]
word_limit = 500
require_backlinks = false

[paths]
slips_dir = "slips/"
bibliography_dir = "bibliography/"

[analysis]
min_connection_strength = 0.1
orphan_grace_period_days = 7
```

### Core Data Models

**Slip Structure** (Shared across all tools)
```
Slip:
  - file_path: Path to .org file
  - properties: ID, CUSTOM_ID, title, filetags
  - content: Main text content
  - links: All outgoing connections
  - metadata: Word count, timestamps, etc.
```

**Link Types** (Common taxonomy)
```
- INTERNAL: Between slips ([[id:UUID]] or [[42/3a]])
- EXTERNAL: Web resources ([[https://...]])  
- BIBLIOGRAPHY: Academic sources ([[cite:key]])
- MEDIA: Files and images ([[file:path]])
```

### Tool Integration

**Validation → Analysis**
- Validator ensures data quality before analysis
- Common violation reporting format
- Shared understanding of valid slip structure

**Analysis → UI**
- Graph data exported in standard formats (JSON, GraphML)
- Network metrics available for conversational queries
- Connection recommendations feed interactive exploration

**All Tools → Configuration**
- Shared settings reduce duplication
- Consistent behavior across projects
- Single point for customization

## Interface Specifications

### Command Line Interface
```bash
# Consistent naming pattern
slipbox-validate [command] [options] [path]
slipbox-analyze [command] [options] [path]  
slipbox-ui [command] [options] [path]
```

### Data Exchange Formats

**Validation Results**
```json
{
  "file_path": "slips/example.org",
  "passed": false,
  "violations": [
    {
      "rule": "WORD_LIMIT", 
      "message": "Content exceeds 500 words",
      "line_number": 15,
      "severity": "ERROR"
    }
  ]
}
```

**Graph Export**
```json
{
  "nodes": [
    {"id": "42/3a", "title": "Logic", "word_count": 350, "tags": ["concept"]}
  ],
  "edges": [
    {"source": "42/3a", "target": "57/12", "type": "INTERNAL", "strength": 0.8}
  ]
}
```

### Configuration Schema

**Validation Settings**
```toml
[validation]
word_limit = 500
check_external_links = true
require_properties = ["ID", "CUSTOM_ID", "TITLE", "FILETAGS"]
allowed_tags = ["concept", "literature", "fleeting", "sequence"]
```

**Analysis Settings**  
```toml
[analysis]
orphan_grace_period_days = 7
min_connection_strength = 0.1
centrality_algorithms = ["betweenness", "pagerank"]
cluster_detection = true
```

## Extension Points

### Adding New Projects

**Project Structure Template**
```
mgmt/newproject/
├── README.md              # Usage documentation
├── ARCHITECTURE.md        # Implementation details
├── pyproject.toml         # or equivalent packaging
├── newproject/            # Source code
└── tests/                 # Test suite
```

**Integration Checklist**
- [ ] Implements shared data models from `CONVENTIONS.md`
- [ ] Reads `slipbox.toml` configuration  
- [ ] Follows CLI naming patterns
- [ ] Provides structured output for tool chaining
- [ ] Includes integration tests with existing tools

### Future Capabilities

**Conversational Interface** (`mgmt/ui/`)
- Natural language queries about slip content
- Interactive graph exploration
- Guided connection discovery
- "Communicating with Slipboxes" made literal

**Performance Analysis** (`mgmt/analyzer/`)
- Large-scale graph algorithms (10,000+ slips)
- Community detection in knowledge networks
- Temporal analysis of idea development
- Citation network analysis with bibliography integration

**Automation** (`mgmt/scripts/`)
- Git hooks for validation
- Scheduled maintenance tasks
- Slip creation templates
- Bibliography synchronization

## Quality Assurance

### Testing Strategy
- **Unit tests** - Each project tests its own functionality
- **Integration tests** - Cross-project data compatibility  
- **End-to-end tests** - Full validation → analysis → UI workflows
- **Performance tests** - Large slipbox scalability

### Documentation Standards
- **README.md** - User-facing usage instructions
- **ARCHITECTURE.md** - Implementation design decisions
- **API documentation** - For programmatic interfaces
- **Examples** - Sample configurations and workflows

### Monitoring
- **Validation metrics** - Track slip compliance over time
- **Performance metrics** - Tool execution times and memory usage
- **Usage patterns** - Which tools are used together
- **Error tracking** - Common failure modes and improvements

The goal is a robust, extensible platform that scales with the intellectual ambitions of the Zettelkasten while maintaining Luhmann's core principles of organic growth and surprising connections.