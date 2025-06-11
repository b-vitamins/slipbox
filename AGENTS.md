# Slipbox management guidelines

## Overview

This is a Org-Roam Zettelkasten designed for academic and research notes. Most feature heavy LaTeX content. All operations must go through the provided scripts to ensure consistency and proper Org-Roam integration.

## Repository Structure

```
notes/
├── daily/          # Daily notes (YYYY-MM-DD.org)
├── fleeting/       # Quick captures, temporary thoughts
├── literature/     # Book notes, paper summaries, quotes
├── concept/        # Core concepts, permanent notes
├── problem/        # Problem sets, exercises, solutions
├── index/          # Index/MOC (Map of Content) files
├── attachments/    # Images, PDFs, other files
└── archive/        # Archived notes
```

## Note Types and Templates

### 1. Fleeting Notes
Quick captures for temporary thoughts. Two variants:
- **Regular**: `./scripts/create-node.sh fleeting "Title"`
- **Timed**: `./scripts/create-node.sh fleeting-timed "Title"`

### 2. Concept Notes
Permanent, atomic ideas - the core of the Zettelkasten:
- **Regular**: `./scripts/create-node.sh concept "Title"`
- **Timed**: `./scripts/create-node.sh concept-timed "Title"`

### 3. Literature Notes
Summaries of books, papers, and external sources:
- **Regular**: `./scripts/create-node.sh literature "Title"`
- **Paper import**: `./scripts/paper-import.sh "Title" "Authors" "Year" "Venue"`

### 4. Problem Notes
Exercises with solutions:
- **Regular**: `./scripts/create-node.sh problem "Title"`
- **Timed**: `./scripts/create-node.sh problem-timed "Title"`

### 5. Index/MOC Notes
Topic hubs that organize related notes. These notes should be timestamped just like any other node. Use the creation script:
- `./scripts/create-index.sh "Topic Name"`

### 6. Daily Notes
- `./scripts/daily-note.sh` - Creates or opens today's daily note

## Quick Reference

### Essential Commands
```bash
# Node Creation
./scripts/create-node.sh [type] "Title"          # Create typed node
./scripts/quick-capture.sh "Content"             # Quick fleeting note
./scripts/daily-note.sh                          # Today's daily note
./scripts/create-index.sh "Topic"                # Create index/MOC

# Search and Discovery
./scripts/find-node.sh "search term"             # Search by title/content
./scripts/find-by-tag.sh "tag"                   # Find by tag
./scripts/find-similar.sh "node-id"              # Find related nodes
./scripts/find-orphans.sh                        # Find unlinked nodes

# Link Management
./scripts/link-nodes.sh "source-id" "target-id"  # Create link
./scripts/show-backlinks.sh "node-id"            # Show what links to node

# LaTeX Operations
./scripts/format-latex.sh "node-id"              # Format LaTeX
./scripts/lint-latex.sh "node-id"                # Check LaTeX errors
./scripts/extract-equations.sh ["topic"]         # Extract all equations

# Maintenance
./scripts/sync-db.sh                             # Rebuild database
./scripts/weekly-maintenance.sh                  # Weekly cleanup
./scripts/check-health.sh                        # System health check
./scripts/show-stats.sh                          # Repository statistics
```

## Working with Content

### Creating Nodes from Raw Input

When given unstructured text:
1. Determine the appropriate type (fleeting, concept, literature, problem)
2. Extract the core idea for the title
3. Use the appropriate create command
4. Content will be properly formatted with ID, title, and tags

Example:
```bash
# From rough notes about attention mechanisms
./scripts/create-node.sh concept "Attention Mechanisms in Neural Networks"
```

### LaTeX Content

All notes support LaTeX. Use standard Org-mode syntax:
- Inline math: `\$\alpha + \beta = \gamma$`
- Display math: `\[ E = mc^2 \]` or `$$E = mc^2$$`
- LaTeX blocks: `#+BEGIN_EXPORT latex ... #+END_EXPORT`

The setupfile includes common physics and math packages:
- `amsmath`, `amssymb`, `amsthm`
- `physics` package for notation
- `mathtools` for enhanced commands
- `tikz` for diagrams

### Linking Strategy

1. **Always check for linkable concepts** before creating new nodes
2. **Use node IDs** for links: `[[id:UUID][Link text]]`
3. **Create bidirectional links** when concepts are strongly related
4. **Build index nodes** for major topics

### Node Quality Standards

#### Titles
- Clear and specific
- Include key searchable terms
- Do not duplicate the title as a heading
- Examples:
  ✓ "Variational Autoencoders - Latent Space Structure"
  ✗ "VAE Notes"

#### Content Structure
1. **Definition/Overview** - What is this concept?
2. **Key Properties** - Important characteristics
3. **Mathematical Formulation** - Equations and derivations
4. **Examples** - Concrete instances
5. **Related Concepts** - Links to other nodes
6. **References** - Sources and citations

#### Tags
- Type tags are automatic: `:fleeting:`, `:concept:`, etc.
- Add domain tags: `:physics:`, `:ml:`, `:mathematics:`
- Status tags: `:draft:`, `:review:`, `:polished:`

## Maintenance Workflows

### Daily
1. Create daily note: `./scripts/daily-note.sh`
2. Quick capture thoughts: `./scripts/quick-capture.sh "idea"`
3. Process fleeting notes into permanent notes

### Weekly
Run `./scripts/weekly-maintenance.sh` which:
- Archives old fleeting notes (>30 days)
- Identifies orphaned nodes
- Syncs database
- Shows statistics

### Monthly
1. Review and upgrade fleeting notes to concepts
2. Update index nodes with new entries
3. Check for knowledge gaps in topics
4. Archive completed problems

## Advanced Operations

### Splitting Large Nodes
When a node covers multiple concepts:
1. Identify the distinct concepts
2. Create new nodes for each concept
3. Replace original content with links
4. Update the original as an index

### Creating Learning Paths
```bash
./scripts/create-learning-path.sh "Basic Concept" "Advanced Concept"
```
Then manually create an index node ordering the intermediate steps.

### Bulk Imports
For importing multiple papers:
```bash
# Import papers from a conference
for paper in paper1 paper2 paper3; do
    ./scripts/paper-import.sh "$paper" "Authors" "2024" "NeurIPS"
done
```

### Report Generation
```bash
./scripts/generate-report.sh week progress    # Weekly progress
./scripts/generate-report.sh month links      # Monthly link analysis
```

## Troubleshooting

### Database Issues
If the database seems out of sync:
```bash
./scripts/sync-db.sh
```

### Finding Problems
```bash
./scripts/check-health.sh    # Full system check
./scripts/find-orphans.sh    # Find unlinked notes
```

### Node ID Issues
All nodes must have a `:ID:` property. If missing, the node won't be recognized by Org-Roam.

## Best Practices

1. **One concept per note** - Keep notes atomic
2. **Link generously** - But meaningfully
3. **Use descriptive link text** - Not just "link"
4. **Process fleeting notes quickly** - Don't let them accumulate
5. **Create index nodes** - For major topics
6. **Include examples** - Especially for abstract concepts
7. **Track time** - For research sessions use timed variants

## Important Notes

- The `org-roam.db` is auto-generated and should never be committed
- All operations must use the provided scripts
- Scripts use Emacs batch mode to ensure proper Org-Roam functionality
- Always include `#+SETUPFILE: ../../setupfile.org` for consistency
- Node IDs are UUIDs generated automatically
- All note files are timestamped by the creation scripts

## Getting Started

1. Create your first daily note: `./scripts/daily-note.sh`
2. Capture ideas: `./scripts/quick-capture.sh "My first idea"`
3. Create a concept: `./scripts/create-node.sh concept "My First Concept"`
4. Find and link: `./scripts/find-node.sh "first"`
5. Check statistics: `./scripts/show-stats.sh`

Remember: This system is designed to grow organically. Start simple and let the connections emerge naturally.
