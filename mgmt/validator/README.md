# Slipbox Validator

Validation and linting tools for Luhmann-style Zettelkasten slip boxes.

## Installation

```bash
# Development installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Validate entire slipbox
slipbox-validate check

# Validate specific aspects
slipbox-validate structure    # Properties, word count
slipbox-validate links        # Link integrity
slipbox-validate orphans      # Find disconnected slips

# Get help
slipbox-validate --help
```

## Validation Rules

### Structure Validation
- **Required Properties**: Every slip must have `:ID:`, `:CUSTOM_ID:`, `#+TITLE:`, `#+FILETAGS:`
- **Word Limit**: Content ≤ 500 words (excluding markup and metadata)
- **Luhmann Numbering**: Custom IDs must follow pattern `\d+(/\d+)*[a-z]*\d*`

### Link Validation
- **Internal Links**: Must resolve to existing slips
- **External Links**: URLs should be reachable (optional)
- **Bibliography Links**: Must reference entries in `.bib` files
- **Media Links**: Files must exist

### Network Analysis
- **Orphan Detection**: Find slips with no incoming/outgoing links
- **Connection Points**: Validate marked connection syntax

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/
ruff --fix src/ tests/

# Type checking
mypy src/

# Install pre-commit hooks
pre-commit install
```

## Configuration

Create `slipbox.toml` in your slipbox root:

```toml
[validation]
word_limit = 500
check_external_links = true
orphan_grace_period_days = 7

[paths]
slips_dir = "slips/"
bibliography_dir = "bibliography/"
media_dir = "assets/"
```