# Slipbox Conventions

*Formal rules for Zettelkasten method with modern technology*

## Core Philosophy

- **Authentic Zettelkasten principles** - Non-hierarchical, emergent structure, productive accidents
- **Machine-readable format** - Programmatically verifiable for automation at scale
- **Housekeeping hygiene** - Save precious thinking time through systematic conventions
- **Technology-enhanced, not technology-driven** - Tools serve the method, not vice versa

## ID System (Hybrid)

- **Technical ID**: UUID for robust linking (`550e8400-e29b-41d4-a716-446655440000`)
- **Human ID**: Slip numbering for semantic structure (`42/3a`, `57/12`)
- **Implementation**: Both in PROPERTIES block
  ```org
  :PROPERTIES:
  :ID: [UUID]
  :CUSTOM_ID: [slip-number]
  :END:
  ```

## Slip Structure Requirements

### Required Properties
- `ID` - UUID (never change)
- `CUSTOM_ID` - Slip number (human readable)
- `TITLE` - Clear, searchable title
- `FILETAGS` - Type and domain classification

### Required Sections
- Content with marked connection points
- Links to other slips

## Individual Slip Rules

### Size Constraint
- **Maximum 500 words per slip** - Forces atomic thinking and clear formulation
- **One core idea per slip** - Prevents essay-writing, maintains surprise factor
- **Complex arguments become networks** - Chain related slips rather than expanding linearly

### Content Structure
- **Mark connection points within text** - Indicate where branches/links attach
- **Multiple connection points allowed** - Single slip can branch in several directions
- **Write for future surprise** - Formulate to reveal unexpected relationships to future self

### Mathematical/Technical Content
- **Break at logical boundaries** - Natural proof structure:
  - Theorem statement + intuition
  - Key lemmas as separate slips  
  - Proof steps as sequential branches
  - Applications/corollaries as connections
- **Sequential chains allowed** - Use numbering like 57/12a1, 57/12a2 for dependent steps
- **Special tags for sequences** - Mark with `:sequence:` when linear dependency required

### Writing Strategy
- **Avoid obvious categorization** - Don't file under generic terms like "art" or "physics"
- **Seek connecting formulations** - Look for angles that relate heterogeneous concepts
- **Problem-oriented approach** - Frame content as questions that invite connections

## Literature Processing

### Reading Strategy for Theoretical Texts
- **Selective focus** - Only small portion contains conceptually decisive words
- **Network-oriented extraction** - Look for "extensively networked references"
- **Long-term memory required** - Distinguish essential from non-essential, new from repeated
- **Frame awareness** - Pay attention to schemata of observation and conditions

### Literature Slip Creation
- **Reformulate, don't excerpt** - "Condensed reformulations of what has been read"
- **Re-description trains observation** - Forces attention to underlying frames and assumptions
- **Question exclusions** - "What is not meant, what is excluded when something is asserted?"
- **Challenge assumptions** - If text says "human rights," what about non-human rights? Historical cultures without them?

### Processing Principles
- **Transform through understanding** - Active re-description rather than passive quotation
- **Identify conceptual frames** - What enables this argument? What's taken for granted?
- **Extract connection potential** - Which concepts bridge to other domains?
- **Avoid name-dropping** - Focus on problems and connections, not just "Marx said X"

### Literature Slip Structure
- **Author/work reference** - Proper citation to bibliography
- **Reformulated core insight** - Your re-description of key points
- **Exclusion analysis** - What does author not consider?
- **Connection potential** - Links to existing slips and concepts
- **Frame critique** - Underlying assumptions and limitations

## Content Rules

### Communication Partnership
- **The slip box must surprise you** - System becomes communication partner, not mere storage
- **Productive accidents are the goal** - Look for formulations that relate heterogeneous things
- **Independence from the beginning** - Give system autonomy to develop its own internal life

### Structural Principles  
- **Fixed numbering, never change** - Once assigned, ID is permanent (enables arbitrary branching)
- **No thematic hierarchy** - Avoid systematic ordering by topics (binds you to decisions for decades)
- **Internal branching anywhere** - Connect to particular words: 57/12 → 57/12a → 57/12a1
- **Mark connection points** - Indicate within text where branches/links attach

### Linking Strategy
- **Link generously and immediately** - Create references radially to related concepts
- **No privileged slips** - Every slip gets quality only from network connections
- **Multiple storage via links** - Same concept can be referenced from many contexts

### System Properties
- **Disorder with non-arbitrary structure** - Apparent chaos but internal organization emerges
- **Critical mass required** - System needs years to become communication partner vs container
- **Register maintenance** - Constantly update keyword index for rediscovery
- **Some things will be lost** - Accept that not all slips will be rediscovered

## System Evolution & Scale

### Temporal Handling
- **Timestamps**: Git tracking sufficient, Org auto-timestamps for discovery patterns
- **Outdated thinking**: Don't update old slips - create new ones that reference/critique (preserves intellectual evolution)
- **Current thinking snapshot**: Slips represent present understanding, history tracked via git
- **Versioning**: Commit-level tracking adequate for slip-level changes

### Register/Index System
- **Keyword strategy**: Hybrid approach
  - Formal FILETAGS for basic classification (`:literature:`, `:physics:`, `:concept:`)
  - Emergent keywords from usage patterns and content analysis
- **Maintenance**: Semi-automated extraction + manual curation
- **Orphan detection**: Automated analysis to find slips lacking incoming/outgoing links
- **Scale considerations**: Multiple specialized indices may emerge at 1000+ slips

### External Integration
- **Link freely**: URLs, papers, books, figures/images via Org's linking capabilities
- **Bibliography coupling**: Literature slips reference bibliography entries seamlessly
- **Media inclusion**: Images, figures, diagrams as first-class content
- **No link type restrictions**: Org accommodates virtually any reference target

### Connection Philosophy
- **No artificial taxonomies**: Avoid classifying link "strength" or "type"
- **Emergent relationship types**: Let connection patterns reveal themselves naturally
- **Equal slip principle**: No privileged slips, value emerges from network position

## Discovery & Navigation

### Serendipity Mechanisms
- **Random slip selection**: Automated "surprise me" function for forgotten connections
- **Temporal clustering**: Browse slips from similar time periods (what was I thinking then?)
- **Orphan alerts**: Surface slips that haven't been accessed recently
- **Weak connection discovery**: Find slips sharing keywords but not directly linked
- **Path traversal**: Follow random link chains to unexpected destinations

### Entry Points (Emergent, Not Imposed)
- **Hub detection**: Track slips with high connection density (natural emergence)
- **Bridge identification**: Slips connecting different domains (high betweenness centrality)
- **Recent activity portals**: Use current work as navigation starting points
- **Domain gateways**: Let certain slips naturally become topic entry points

## Maintenance Workflows

### Review Cycles
- **Monthly**: Orphan slip detection and connection opportunities
- **Quarterly**: External link validation (URLs, files, bibliography)
- **Annually**: Connection audit - missing links between related concepts
- **Ongoing**: Keyword extraction and index refinement

### Link Integrity
- **Automated URL checking**: Detect dead external links
- **Bibliography validation**: Ensure references remain accessible
- **Media file verification**: Check images/figures still exist
- **Git tracking**: Monitor when external references break

## Quality Indicators (Observational, Not Enforced)

### Slip Health Metrics (For Observation Only)
- **Connection richness**: Pattern observation, not density targets
- **Surprise factor**: Does it bridge unexpected domains?
- **Reformulation quality**: For literature slips - clarity of re-description
- **Longevity**: Slips referenced across long time periods
- **Clarity of connection points**: Well-marked branching locations

### Anti-Patterns to Avoid
- **Gamification**: No scoring or ranking systems
- **Artificial metrics**: Don't optimize for numbers over thinking quality
- **Forced connections**: Links should feel natural, not obligatory
- **Over-categorization**: Resist urge to create elaborate taxonomies

## Machine-Readable Conventions

*To be expanded as system grows...*

## Validation Rules

*Programmatic checks to be implemented...*

## Automation Opportunities

*Scripts and workflows to be developed...*

---
*File created during initial system setup - expand as conventions emerge*
