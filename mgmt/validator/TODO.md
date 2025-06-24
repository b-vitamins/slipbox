# Validator Development TODO

*Systematic development plan with entry/exit criteria for session resumption*

## Current Status: Foundation Complete
- ✅ Project structure and packaging
- ✅ Data models (Slip, Link, ValidationResult, etc.)
- ✅ Org parser (properties, links, word counting)
- ✅ CLI framework with click
- ✅ Basic test structure

---

## Phase 1: Basic Structure Validation
**Goal:** Working structure validation that can check real slips

### Entry Criteria
- [x] Parser can extract properties and count words
- [x] CLI framework accepts commands
- [x] Data models defined

### Tasks

#### 1.1 Implement Structure Validators ✅ COMPLETE
**File:** `validator/validators/structure.py`

```python
# Required implementations:
class RequiredPropertiesValidator(BaseValidator):
    # Check ID, CUSTOM_ID, TITLE, FILETAGS exist and are valid
    
class WordCountValidator(BaseValidator):
    # Check content ≤ 500 words (with :extended: exception)
    
class LuhmannNumberValidator(BaseValidator):
    # Validate CUSTOM_ID format: \d+(/\d+)*[a-z]*\d*
```

**Specific requirements:**
- [x] `RequiredPropertiesValidator.validate()` returns violations for missing properties
- [x] `WordCountValidator.validate()` counts words correctly (excluding markup)
- [x] `WordCountValidator.validate()` skips slips tagged with `:extended:`
- [x] `LuhmannNumberValidator.validate()` validates custom ID format
- [x] All validators inherit from `BaseValidator` interface

#### 1.2 Create Base Validator Framework ✅ COMPLETE
**File:** `validator/validators/base.py`

```python
class BaseValidator:
    def validate(self, slip: Slip) -> List[Violation]:
        # Override in subclasses
        
class ValidationEngine:
    def __init__(self, validators: List[BaseValidator])
    def validate_slip(self, slip: Slip) -> ValidationResult
    def validate_slipbox(self, slips_dir: Path) -> List[ValidationResult]
```

**Requirements:**
- [x] `BaseValidator` provides clean interface for all validators
- [x] `ValidationEngine` runs multiple validators on single slip
- [x] `ValidationEngine.validate_slipbox()` discovers and validates all .org files
- [x] Error handling for unreadable files (skip with warning)

#### 1.3 Wire CLI Commands to Validators ✅ COMPLETE
**File:** `validator/cli.py`

**Requirements:**
- [x] `slipbox-validate structure` runs structure validators and shows results
- [x] `slipbox-validate check` runs all available validators  
- [x] Commands discover slips directory automatically (default to current dir)
- [x] Commands accept explicit path argument
- [x] Error handling for missing directories

#### 1.4 Implement Console Reporter ✅ COMPLETE
**File:** `validator/reporters/console.py`

```python
class ConsoleReporter:
    def report_results(self, results: List[ValidationResult]) -> None:
        # Pretty-print violations with colors, line numbers
        
    def summary(self, results: List[ValidationResult]) -> None:
        # Show overall pass/fail counts
```

**Requirements:**
- [x] Show violations grouped by file
- [x] Include line numbers when available
- [x] Color coding (red=error, yellow=warning, green=pass)
- [x] Summary stats (X files, Y violations, Z warnings)
- [x] Human-readable violation messages

### Exit Criteria ✅ PHASE 1 COMPLETE
- [x] `slipbox-validate structure` runs without errors
- [x] Validates actual slips and shows meaningful output
- [x] At least 5 unit tests covering core validation logic (13 tests total)
- [x] Documentation updated in README.md with examples

### Testing Requirements ✅ COMPLETE
- [x] Unit tests for each validator with sample org content
- [x] Integration test running full structure validation
- [x] Test with malformed org files (missing properties, etc.)
- [x] Test with existing slips to verify realistic behavior (found 76 missing CUSTOM_IDs)

---

## Phase 2: Link Validation ✅ COMPLETE
**Goal:** Validate internal link integrity and detect orphans

### Entry Criteria  
- [x] Phase 1 complete (structure validation working)
- [x] Parser can extract links reliably

### Tasks

#### 2.1 Implement Link Validators ✅ COMPLETE
**File:** `validator/validators/links.py`

```python
class InternalLinkValidator(BaseValidator):
    # Verify [[id:UUID]] and [[42/3a]] links resolve to existing slips
    
class OrphanDetector(BaseValidator):
    # Find slips with no incoming/outgoing links (with grace period)
    
class BidirectionalLinkAnalyzer(BaseValidator):
    # Suggest missing back-links (warnings, not errors)
```

#### 2.2 Build Slip Graph ✅ COMPLETE
**File:** `validator/validators/links.py` (integrated into validators)

```python
# Graph functionality integrated into:
# - InternalLinkValidator._build_slip_index()
# - OrphanDetector._build_connection_graph() 
# - BidirectionalLinkAnalyzer._collect_all_links()
```

#### 2.3 Add Links Commands ✅ COMPLETE
**Requirements:**
- [x] `slipbox-validate links` checks link integrity
- [x] `slipbox-validate orphans` finds disconnected slips (with --grace-days option)
- [x] Commands integrated into `slipbox-validate check`

### Exit Criteria ✅ PHASE 2 COMPLETE
- [x] Can detect broken internal links in real slipbox (found many broken UUID links)
- [x] Orphan detection working with configurable grace period (0 orphans found)
- [x] Link validation integrated into main check command (structure + links)

---

## Phase 3: External Validation ✅ COMPLETE
**Goal:** Bibliography links, external URLs, media files

### Entry Criteria
- [x] Phase 2 complete (internal links working)

### Tasks

#### 3.1 Bibliography Integration ✅ COMPLETE
- [x] Parse .bib files in bibliography/ directory
- [x] Validate [[cite:key]] links reference existing entries
- [x] Integration with existing bibliography structure

#### 3.2 External Resource Validation ✅ COMPLETE
- [x] Optional HTTP checking for [[https://...]] links
- [x] File existence checking for [[file:...]] links
- [x] Configurable timeouts and error handling

#### 3.3 Configuration System ✅ COMPLETE
**File:** `validator/config.py`
- [x] Read slipbox.toml configuration
- [x] Override defaults for word limits, grace periods, etc.
- [x] Configuration validation and error reporting

### Exit Criteria ✅ PHASE 3 COMPLETE
- [x] All link types validated (internal, external, bibliography, media)
- [x] Configuration system working (slipbox.toml support)
- [x] External validation optional/configurable (--no-external, --no-urls flags)

---

## Phase 4: Advanced Features
**Goal:** Polish and advanced functionality

### Entry Criteria
- [x] Phase 3 complete (all validation working)

### Tasks

#### 4.1 Enhanced Reporting
- [ ] JSON output format for tool integration
- [ ] HTML report generation
- [ ] Violation trend tracking

#### 4.2 Auto-fixing
- [ ] `--fix` flag implementation
- [ ] Safe automatic corrections (formatting, etc.)
- [ ] Backup and rollback capabilities

#### 4.3 Git Integration
- [ ] Pre-commit hook integration
- [ ] Validate only changed files
- [ ] Integration with existing commit-msg hook

#### 4.4 Performance Optimization
- [ ] Parallel slip processing
- [ ] Incremental validation (only changed files)
- [ ] Large slipbox optimization (1000+ slips)

### Exit Criteria
- [ ] Production-ready validator
- [ ] Git workflow integration
- [ ] Documented and tested auto-fix features

---

## Development Guidelines

### Session Resumption Protocol
1. **Check current phase** - Look at last completed exit criteria
2. **Review task status** - Check off completed items in current phase
3. **Run existing tests** - Ensure no regressions
4. **Continue from next incomplete task**

### Testing Strategy
- **Unit tests** - Each validator has comprehensive test coverage
- **Integration tests** - Full validation runs on sample slipboxes
- **Real data testing** - Regular validation of actual slips
- **Performance tests** - Ensure scalability to large slipboxes

### Code Quality Standards
- **Type hints** - All functions have proper typing
- **Documentation** - Docstrings for all public methods
- **Error handling** - Graceful failure with meaningful messages
- **Configurability** - Hard-coded values in configuration files

### Phase Transition Checklist
Before moving to next phase:
- [ ] All exit criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] No known regressions
- [ ] Code reviewed for quality

---

## Phase 5: Org-roam Integration
**Goal:** Align validator with Org-roam requirements and priorities

### Entry Criteria
- [x] Phase 3 complete (external validation working)
- [x] Understanding of Org-roam node model and database caching
- [x] Knowledge of Org-roam vs traditional Zettelkasten requirements

### Tasks

#### 5.1 Adjust Validation Priorities for Org-roam ✅ COMPLETE
**File:** `validator/validators/structure.py`

**Requirements:**
- [x] Missing `:ID:` property = **ERROR** (breaks Org-roam functionality)
- [x] Missing `:CUSTOM_ID:` property = **WARNING** (breaks traditional Zettelkasten)
- [x] Update severity levels in RequiredPropertiesValidator
- [x] Add configuration option for ID priority mode
- [x] Update CLI to pass configuration options
- [x] Add comprehensive tests for both modes
- [x] Update slipbox.toml with new options
- [x] Verify behavior on real slipbox (76 warnings instead of 76 errors)

#### 5.2 Enhanced Citation Format Support ✅ COMPLETE
**File:** `validator/validators/external.py`, `validator/parser.py`, `validator/models.py`

**Requirements:**
- [x] Support `[cite:@key]` format (org-cite) - handled as `cite:@key` link target
- [x] Support `cite:key` format (org-ref) - already supported, enhanced extraction
- [x] Support `@key` in ROAM_REFS property - new extraction and validation
- [x] Maintain backward compatibility with existing `[[cite:key]]` - fully compatible
- [x] Enhanced citation key extraction with multiple format support
- [x] Added ROAM_ALIASES and ROAM_REFS property support to SlipProperties model
- [x] Updated parser to extract ROAM_ALIASES and ROAM_REFS from properties block
- [x] Enhanced BibliographyValidator to validate citation keys in ROAM_REFS
- [x] Added comprehensive tests for all citation formats (34 tests total passing)

#### 5.3 ROAM_ALIASES and ROAM_REFS Validation ✅ COMPLETE
**File:** `validator/validators/structure.py`

**Requirements:**
- [x] Validate ROAM_ALIASES format (multiple space-separated values) - warns on invalid format
- [x] Validate ROAM_REFS format (URLs, citation keys) - distinguishes URLs vs citation keys 
- [x] Check for duplicate aliases across slips - warns when aliases are reused
- [x] Verify citation keys in ROAM_REFS exist in bibliography - integrated with BibliographyValidator
- [x] Support multiple ROAM_REFS values per slip - parser handles space-separated values
- [x] Added RoamPropertiesValidator with comprehensive format validation
- [x] Integrated into SlipStructureValidator meta-validator
- [x] Added 6 comprehensive tests covering valid/invalid formats and duplicate detection
- [x] Updated CLI to enable duplicate alias checking
- [x] Tested on real slipbox (no ROAM properties found, working correctly)

#### 5.4 Link Priority Adjustment ✅ COMPLETE
**File:** `validator/validators/links.py`

**Requirements:**
- [x] `[[id:UUID]]` broken links = **ERROR** (essential for relationships)
- [x] `[[42/3a]]` broken links = **WARNING** (traditional convenience)
- [x] Update InternalLinkValidator severity logic with `_get_link_severity_and_message()`
- [x] Add configuration for link priority mode via `org_roam_priority` parameter
- [x] Updated SlipLinkValidator to pass configuration 
- [x] Updated CLI to pass org_roam_priority from config
- [x] Added 3 comprehensive tests for both modes (ERROR vs WARNING)
- [x] Tested on real slipbox: 59 ID link errors + 18 Luhmann link warnings

### Exit Criteria
- [ ] Validation severity reflects Org-roam vs traditional priorities
- [ ] All citation formats supported (org-cite, org-ref, traditional)
- [ ] ROAM_ALIASES and ROAM_REFS properly validated
- [ ] Link validation prioritizes ID links appropriately
- [ ] Configuration allows switching between strict Org-roam and hybrid modes

---

## Phase 6: Advanced Org-roam Features
**Goal:** Support headline nodes, template compliance, and database consistency

### Entry Criteria
- [ ] Phase 5 complete (Org-roam integration working)

### Tasks

#### 6.1 Headline Node Support ⏳ PENDING
**File:** `validator/parser.py`, `validator/validators/structure.py`

**Requirements:**
- [ ] Parse headline nodes with `:ID:` properties
- [ ] Validate headline-level nodes separately from file nodes
- [ ] Support nested headlines with IDs
- [ ] Handle headline title validation vs file `#+title`
- [ ] Update slip index to include headline nodes

#### 6.2 Template Compliance Validation ⏳ PENDING
**File:** `validator/validators/template.py`

**Requirements:**
- [ ] Validate timestamp filename format: `%<%Y%m%d%H%M%S>-${slug}.org`
- [ ] Check for proper template-generated structure
- [ ] Validate required template fields (title, filetags)
- [ ] Optional validation for custom template compliance

#### 6.3 Tag Inheritance Analysis ⏳ PENDING
**File:** `validator/validators/structure.py`

**Requirements:**
- [ ] Understand `#+filetags` inheritance to headlines
- [ ] Detect tag conflicts and redundancy
- [ ] Validate proper tag hierarchy
- [ ] Warn about unintended tag inheritance

#### 6.4 Database Consistency Checks ⏳ PENDING
**File:** `validator/validators/consistency.py`

**Requirements:**
- [ ] Compare validator findings with org-roam database (if available)
- [ ] Detect cache staleness issues
- [ ] Warn about performance implications
- [ ] Optional org-roam-db integration for cross-validation

### Exit Criteria
- [ ] Full headline node support implemented
- [ ] Template compliance validation working
- [ ] Tag inheritance properly analyzed
- [ ] Database consistency checking available
- [ ] Advanced features configurable and well-tested

---

## Phase 4: Advanced Features (Revised)
**Goal:** Polish, auto-fixing, and production features

### Entry Criteria
- [ ] Phase 6 complete (advanced Org-roam features working)

### Tasks

#### 4.1 Enhanced Reporting
- [ ] JSON output format for tool integration
- [ ] HTML report generation with Org-roam buffer-style display
- [ ] Violation trend tracking
- [ ] Export validation results for external analysis

#### 4.2 Auto-fixing
- [ ] `--fix` flag implementation
- [ ] Safe automatic corrections (formatting, missing properties)
- [ ] Backup and rollback capabilities
- [ ] Interactive fixing mode with user confirmation

#### 4.3 Git Integration
- [ ] Pre-commit hook integration
- [ ] Validate only changed files
- [ ] Integration with existing commit-msg hook
- [ ] Git-aware validation reporting

#### 4.4 Performance Optimization
- [ ] Parallel slip processing
- [ ] Incremental validation (only changed files)
- [ ] Large slipbox optimization (1000+ slips)
- [ ] Memory-efficient processing for huge slipboxes

### Exit Criteria
- [ ] Production-ready validator with auto-fix capabilities
- [ ] Full Git workflow integration
- [ ] Optimized for large-scale slipboxes
- [ ] Comprehensive reporting and export options

---

## Current Priority: Phase 5 (Org-roam Integration)
**Focus:** Align validation priorities with Org-roam requirements

**Phase 1 Status:** ✅ COMPLETE - Basic structure validation working
**Phase 2 Status:** ✅ COMPLETE - Link validation working  
**Phase 3 Status:** ✅ COMPLETE - External validation and configuration working
**Phase 4 Status:** ⏳ DEFERRED - Advanced features moved after Org-roam integration
**Phase 5 Status:** ✅ COMPLETE - Org-roam integration fully implemented

### Completed in Phase 5:
1. ✅ **Adjusted validation priorities** - Missing `:ID:` = ERROR, missing `:CUSTOM_ID:` = WARNING
2. ✅ **Enhanced citation support** - Full org-cite and org-ref format validation
3. ✅ **ROAM_ALIASES/ROAM_REFS validation** - Complete format validation and duplicate detection
4. ✅ **Link priority adjustment** - `[[id:UUID]]` links = ERROR, `[[42/3a]]` links = WARNING

### Exit Criteria ✅ PHASE 5 COMPLETE
- [x] Validation severity reflects Org-roam vs traditional priorities
- [x] All citation formats supported (org-cite, org-ref, traditional)
- [x] ROAM_ALIASES and ROAM_REFS properly validated
- [x] Link validation prioritizes ID links appropriately
- [x] Configuration allows switching between strict Org-roam and hybrid modes