# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Luhmann's Zettelkasten Principles

This is a digital implementation of Niklas Luhmann's Zettelkasten method. The system is designed to be a communication partner, not mere storage.

### Core Principles

1. **The slip box must surprise you** - Information emerges from unexpected connections between notes
2. **Fixed numbering, not topical organization** - Arbitrary internal branching (e.g., 57/12 → 57/12a → 57/12a1)
3. **Every note is equal** - No privileged notes; quality comes only from network connections
4. **Productive accidents are the goal** - The system should produce unexpected combinations
5. **Critical mass is required** - The system needs years to become a true communication partner

### Essential Rules

#### DO:
- **Use fixed IDs** - Once assigned, never change a note's ID
- **Link generously** - Create both forward links AND back-links immediately
- **Embrace disorder** - The apparent disorder has "non-arbitrary internal structure"
- **Allow organic growth** - Let notes branch internally at any point
- **Maintain the register** - Constantly update keyword indices for rediscovery
- **Capture bibliographical references** - Maintain BibTeX files in `/bibliography/` directory, create literature slips that link to concepts
- **Think in networks** - A note without connections will be forgotten by the system
- **Work with what emerges** - Follow the system's suggestions, not preconceived plans

#### DON'T:
- **Don't impose topical hierarchy** - This binds you to decisions for decades
- **Don't worry about placement** - With proper linking, location matters less
- **Don't expect immediate returns** - The system needs time to reach critical mass
- **Don't force systematic order** - Let structure emerge from connections
- **Don't treat notes as final** - They gain meaning only through their relations

### Technical Implementation

#### Note Structure
```
:PROPERTIES:
:ID:       [UUID - never change this]
:END:
#+TITLE: [Clear, searchable title]
#+FILETAGS: [Type and domain tags]

[Content with internal reference points marked]
[[id:UUID][Links to other notes]]
```

#### Numbering Patterns
- Base note: `57/12`
- Branch at end: `57/13`
- Internal branch: `57/12a`, `57/12b`
- Deep branching: `57/12a1`, `57/12a2`

#### Linking Strategy
1. When creating a link, immediately create the back-link
2. Mark connection points within text (Luhmann used red marks)
3. Central concepts should accumulate many links
4. Links solve the "multiple storage" problem

#### Register/Index Maintenance
- Keywords that map to note IDs
- Author names for bibliographical connections
- Concept clusters that emerge from use
- Regular review to discover orphaned notes

### Practical Patterns

#### Creating Notes
1. Capture the thought immediately (fleeting note)
2. Assign a permanent ID
3. Find connection points to existing notes
4. Create bidirectional links
5. Update relevant registers
6. Let the note find its own importance through connections

#### Working with the System
1. Start with a question or trigger
2. Follow unexpected connections
3. Look for "formulations of problems that relate heterogeneous things"
4. Trust what emerges over what you planned
5. Work with preferred centers and clusters that naturally form

#### Anti-Patterns to Avoid
- Creating elaborate category systems
- Trying to predict future organization needs
- Keeping notes isolated without connections
- Expecting the system to work like hierarchical storage
- Treating the register as optional
- Ignoring back-links

### Growth Stages

1. **Container phase** (early years) - Simple retrieval of what you put in
2. **Critical mass** - System begins suggesting connections
3. **Communication partner** - System surprises you with insights
4. **Autonomous system** - Has its own internal life independent of author

### Bibliography Workflow

#### Managing Academic Sources
1. **Collect papers** in domain-specific BibTeX files (`bibliography/*.bib`)
2. **Create literature notes** for papers that spark connections (`slips/`)
3. **Link immediately** - connect new papers to existing concepts via `[[id:UUID][links]]`
4. **Extract concepts** - create separate concept slips for key ideas that transcend individual papers
5. **Build networks** - look for patterns across papers that reveal research programs or paradigm shifts

#### BibTeX to Zettelkasten Bridge
- **One paper, multiple slips**: A single paper may spawn several concept slips
- **Cite by key**: Reference BibTeX entries in literature slips for proper attribution
- **Tag strategically**: Use tags like `:literature:`, `:physics:`, `:neurosymbolic:` for discovery
- **Time-delay insights**: Papers may not show their importance until connected to later discoveries

#### Research Area Development
- **Conference collections**: Maintain separate `.bib` files for major venues (ICLR, ICML, NeurIPS)
- **Topic clusters**: Let domain-specific bibliographies emerge organically (e.g., `neurosymbolic.bib`)
- **Cross-domain pollination**: Look for physics papers that inform ML, philosophy papers that clarify AI concepts
- **Living bibliography**: Update and refine collections as understanding evolves

### Implementation Notes

#### Directory Structure
- **`slips/`** - All Zettelkasten slips in flat structure following Luhmann's principles
- **`bibliography/`** - Separate system for bibliographical references
  - BibTeX files for conference proceedings (`.bib`)
  - Domain-specific collections (e.g., `neurosymbolic.bib`)
- **`.claude/`** - Claude Code configuration and local settings

#### Note Organization
- IDs are UUIDs (Org-Roam standard) - never change once assigned
- Tags indicate type (`:fleeting:`, `:concept:`, `:literature:`)
- Timestamp prefixes for chronological ordering when needed
- Plain text (Org format) ensures longevity
- Database (org-roam.db) enables fast searching but is rebuildable

#### Bibliography Integration
- **Separate but linked**: Bibliography entries live in `/bibliography/` but connect to literature slips
- **BibTeX standard**: Use proper academic citation format
- **Literature slips**: Create dedicated slips for papers with `[[id:UUID][Title]]` links to concepts
- **Domain organization**: Group by research area (ML conferences, specific topics)

#### Research Context
- **Current focus**: Neurosymbolic AI, physics-informed ML, statistical mechanics in neural networks
- **Conference tracking**: ICLR, ICML, NeurIPS papers with physics/symbolic components
- **Cross-pollination**: Look for connections between statistical physics and symbolic reasoning

#### Version Control Workflow
- **Atomic commits**: Each logical change to knowledge structure
- **Descriptive messages**: Explain the conceptual development, not just file changes
- **Bibliography updates**: Separate commits for reference additions vs. note developments
- **Branching**: Use feature branches for major research directions or literature reviews

#### Commit Conventions

**Format**: `type: brief description`

For management subprojects: `mgmt:subproject: description`

**Types**:
- `add:` - New slips or concepts
- `remove:` - Deleting slips or content  
- `connect:` - Links between existing ideas
- `source:` - Bibliography and references
- `update:` - Changes to existing content
- `mgmt:` - Management tools and maintenance scripts
- `mgmt:validator:` - Slip validation and linting tools

**Examples**:
```
add: statistical mechanics note 57/12a

- Thermodynamic analogies for neural networks
- Links to entropy and information theory concepts

connect: symbolic logic to probabilistic reasoning

- Bridge between slips 42/3a and 57/12
- New research direction identified

source: add Jaynes maximum entropy papers

- 8 entries in physics.bib
- Foundation for information-theoretic ML

mgmt: add word count validator

- Check 500-word limit per slip
- Report violations with line numbers
- Skip slips tagged with :extended:

mgmt:validator: implement org file parser

- Extract properties, links, and word counts
- Support all link types (internal, external, bibliography)
- Add connection point detection
```

## Org-roam Integration

This slipbox uses Org-roam for enhanced node management, link tracking, and database caching. Understanding Org-roam concepts is essential for proper validation and maintenance.

### Node Definition

**Org-roam Node**: Any headline or top-level file with an `:ID:` property

**Two Node Types**:
1. **File nodes**: Top-level files with `:ID:` property and `#+title`
2. **Headline nodes**: Headlines within files with `:ID:` property

**Example**:
```org
:PROPERTIES:
:ID:       foo
:END:
#+title: Foo

* Bar
:PROPERTIES:
:ID:       bar
:END:
```
Creates two nodes: file node "Foo" (id: foo) and headline node "Bar" (id: bar).

### Hybrid ID System

This slipbox uses both Org-roam and Luhmann identification:
- **`:ID:` property**: UUID for Org-roam compatibility (e.g., `d2e3f4a5-b6c7-4d8e-9fa0-b1c2d3e4f5a6`)
- **`:CUSTOM_ID:` property**: Luhmann number for traditional Zettelkasten (e.g., `42/3a`)

**Link Formats**:
- `[[id:UUID][Description]]` - Primary format for Org-roam
- `[[42/3a][Description]]` - Traditional Luhmann reference
- Both should work, but `id:` links preferred for database relationships

### Link System

**Org-roam Link Priority**: Only `[[id:UUID]]` links counted for node relationships and graph computation

**Link Types Cached**:
- Internal ID links: `[[id:foo]]` 
- External URLs: `[[https://...]]`
- Citations: `[cite:@key]` or `cite:key`
- Files: `[[file:path]]`
- All other Org link types

**Important**: While all links are cached, only ID links create relationships in the Org-roam database.

### Database and Caching

**Aggressive Caching**: Org-roam crawls all files in `org-roam-directory` and maintains database of links/nodes

**Performance Settings**:
- **Default**: Eager caching on every file save (`org-roam-db-update-on-save: t`)
- **Alternative**: Manual sync via `org-roam-db-sync` for large files
- **Auto-sync**: `org-roam-db-autosync-mode` maintains cache consistency

**Cache Contents**: All Org properties (outline level, todo, priority, scheduled, deadline, tags), node relationships, link targets

### Metadata System

#### Titles and Aliases
- **File titles**: `#+title:` property
- **Headline titles**: Main headline text  
- **Aliases**: `ROAM_ALIASES` property for alternative names/acronyms
- **Search**: All titles and aliases available in completion

#### Tags and Inheritance
- **File tags**: `#+filetags:` inherited by all headlines in file
- **Headline tags**: Regular Org tags at headline level
- **Design limitation**: No selective tag inheritance (all or nothing)

#### References (ROAM_REFS)
- **Purpose**: Unique identifiers for external references
- **Citation keys**: `@author2024paper` for academic papers
- **URLs**: `https://example.com` for web resources
- **Multiple refs**: One node can have multiple identifiers
- **Reference backlinks**: External links to refs show as connections

### Citation Integration

**Two Citation Systems Supported**:
1. **Org-cite** (Org 9.5+): `[cite:@key]` format
2. **Org-ref** (legacy): `cite:key` format

**Academic Workflow**:
```org
* Paper Title
:PROPERTIES:
:ID:       uuid-here
:ROAM_REFS: @citation-key
:END:
```

**Citation Links**: Create "reference backlinks" separate from internal ID links

### Template System

**Capture Templates**: `org-roam-capture-templates` extends org-capture

**Default Template Structure**:
```lisp
(("d" "default" plain "%?"
  :target (file+head "%<%Y%m%d%H%M%S>-${slug}.org"
                     "#+title: ${title}\n")
  :unnarrowed t))
```

**Variable Expansion**: `${foo}` syntax substitutes:
1. Function `foo` called with current node
2. `org-roam-node-foo` accessor function
3. Lookup in `org-roam-capture--info`
4. Prompt via `completing-read`

**Available Variables**: `file`, `id`, `level`, `title`, `tags`, `aliases`, `refs`, etc.

### Org-roam Buffer Interface

**Purpose**: Visual interface for node relationships (backlinks, references, unlinked mentions)

**Commands**:
- `org-roam-buffer-toggle`: Dynamic buffer tracking current node
- `org-roam-buffer-display-dedicated`: Fixed buffer for specific node

**Three Widget Types**:
1. **Backlinks**: Nodes linking TO this node
2. **Reference Links**: Nodes referencing this node (via ROAM_REFS)  
3. **Unlinked References**: Text matches without links (disabled by default, slow)

**Configuration**:
```lisp
(setq org-roam-mode-sections
      (list #'org-roam-backlinks-section
            #'org-roam-reflinks-section))
```

### Node Creation Workflow

**Interactive Commands**:
- `org-roam-node-insert`: Create node + insert link at point
- `org-roam-node-find`: Create node + visit it
- `org-roam-capture`: Create node via templates

**Completion**: Available anywhere via `completion-at-point` or with `org-roam-completion-everywhere`

### Validation Implications

**Critical Requirements**:
- Every slip must have `:ID:` property for Org-roam functionality
- ID links must resolve to existing nodes
- Missing `:CUSTOM_ID:` breaks traditional Zettelkasten referencing
- Broken ID links create empty/incorrect buffer displays
- Orphaned nodes (no connections) violate Zettelkasten principles

**Link Validation Priority**:
1. **Essential**: `[[id:UUID]]` links for Org-roam relationships
2. **Traditional**: `[[42/3a]]` links for Luhmann numbering
3. **External**: Citation and URL links for academic workflow

**Database Health**: Proper caching requires valid Org properties and link structure
