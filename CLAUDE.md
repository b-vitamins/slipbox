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
- **Capture bibliographical references** - Keep a separate system for sources
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

### Implementation Notes

- All notes in single `notes/` directory
- IDs are UUIDs (Org-Roam standard)
- Tags indicate type (`:fleeting:`, `:concept:`, `:literature:`)
- Timestamp prefixes for chronological ordering
- Plain text (Org format) ensures longevity
- Database (org-roam.db) enables fast searching but is rebuildable