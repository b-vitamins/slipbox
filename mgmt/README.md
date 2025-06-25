# Management Workspace

*Infrastructure and tooling for the slipbox Zettelkasten system*

## Overview

This workspace contains management tools and infrastructure that support the intellectual work happening in the slipbox. These tools serve the Zettelkasten method, not the other way around.

## Philosophy

- **Slipbox is primary** - Tools are infrastructure supporting the thinking system
- **Polyglot workspace** - Use the best language/tool for each job
- **Independent projects** - Each tool has its own structure, testing, packaging
- **Shared conventions** - All tools implement the same slipbox requirements

## Current Projects

### validator/
**Language:** Python  
**Purpose:** Validation and linting tools for slip format compliance

```bash
cd mgmt/validator
pip install -e .
slipbox-validate check    # Validate entire slipbox
slipbox-validate structure # Check properties, word count
slipbox-validate links     # Verify link integrity
slipbox-validate orphans   # Find disconnected slips
```

See [validator/README.md](validator/README.md) for detailed usage.

## Future Projects (Planned)

### analyzer/
**Language:** TBD (possibly Rust/C++ for performance)  
**Purpose:** Graph analysis, network metrics, connection discovery

### ui/
**Language:** TypeScript/React  
**Purpose:** Web interface for "Communicating with Slipboxes" - conversational interaction with the knowledge system

### scripts/
**Language:** Shell  
**Purpose:** Quick utilities, git hooks, maintenance tasks

## Conventions

All management tools must implement the slipbox conventions documented in [CONVENTIONS.md](CONVENTIONS.md). This ensures:

- Consistent slip format validation
- Shared understanding of link types and structures  
- Compatible data models across tools
- Unified approach to Zettelkasten principles

## Architecture

High-level system design and integration points are documented in [ARCHITECTURE.md](ARCHITECTURE.md).

## Development Workflow

### Adding New Tools

1. **Create project directory:** `mgmt/newtool/`
2. **Set up proper structure:** Language-appropriate packaging, testing, docs
3. **Implement conventions:** Follow requirements in `CONVENTIONS.md`
4. **Update workspace docs:** Add to this README and `ARCHITECTURE.md`

### Commit Conventions

- **General management:** `mgmt: description`  
- **Specific project:** `mgmt:projectname: description`

Examples:
```
mgmt: add analyzer project for graph analysis
mgmt:validator: implement word count validation
mgmt:ui: create conversational interface prototype
```

### Integration Testing

While each project has its own test suite, integration between tools should be tested to ensure:

- Compatible data formats
- Consistent validation results
- Shared understanding of slip structure

## Getting Started

1. **Understand the conventions:** Read `CONVENTIONS.md` thoroughly
2. **Choose your tool:** Each project has independent setup instructions
3. **Follow the architecture:** See `ARCHITECTURE.md` for system integration
4. **Contribute:** Follow commit conventions and add tests

The goal is sophisticated tooling that amplifies thinking without overwhelming the intellectual work at the heart of the Zettelkasten.
