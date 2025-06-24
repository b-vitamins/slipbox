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

## Phase 3: External Validation
**Goal:** Bibliography links, external URLs, media files

### Entry Criteria
- [x] Phase 2 complete (internal links working)

### Tasks

#### 3.1 Bibliography Integration
- [ ] Parse .bib files in bibliography/ directory
- [ ] Validate [[cite:key]] links reference existing entries
- [ ] Integration with existing bibliography structure

#### 3.2 External Resource Validation  
- [ ] Optional HTTP checking for [[https://...]] links
- [ ] File existence checking for [[file:...]] links
- [ ] Configurable timeouts and error handling

#### 3.3 Configuration System
**File:** `validator/config.py`
- [ ] Read slipbox.toml configuration
- [ ] Override defaults for word limits, grace periods, etc.
- [ ] Configuration validation and error reporting

### Exit Criteria
- [ ] All link types validated
- [ ] Configuration system working
- [ ] External validation optional/configurable

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

## Current Priority: Phase 3, Task 3.1
**Next action:** Implement bibliography validation in `validator/validators/external.py`

**Phase 1 Status:** ✅ COMPLETE - Basic structure validation working
**Phase 2 Status:** ✅ COMPLETE - Link validation working  
- InternalLinkValidator detects broken [[id:UUID]] and [[42/3a]] links
- OrphanDetector finds disconnected slips (grace period configurable)
- BidirectionalLinkAnalyzer suggests missing back-links
- All 20 tests passing (7 new link validation tests)
- CLI commands: structure, links, orphans, check all functional