"""Base validator framework."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..models import Slip, Violation, ValidationResult, Severity
from ..parser import OrgParser


class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    @abstractmethod
    def validate(self, slip: Slip) -> List[Violation]:
        """Validate a slip and return list of violations."""
        pass


class ValidationEngine:
    """Main validation engine that coordinates multiple validators."""
    
    def __init__(self, validators: List[BaseValidator]):
        """Initialize with list of validators to run."""
        self.validators = validators
        self.parser = OrgParser()
    
    def validate_slip(self, slip: Slip) -> ValidationResult:
        """Run all validators on a single slip."""
        violations = []
        warnings = []
        
        for validator in self.validators:
            try:
                slip_violations = validator.validate(slip)
                for violation in slip_violations:
                    if violation.severity == Severity.WARNING:
                        warnings.append(violation)
                    else:
                        violations.append(violation)
            except Exception as e:
                # Add error as violation
                violations.append(Violation(
                    rule="VALIDATOR_ERROR",
                    message=f"Validator {validator.__class__.__name__} failed: {str(e)}",
                    severity=Severity.ERROR
                ))
        
        passed = len(violations) == 0
        return ValidationResult(
            file_path=slip.file_path,
            passed=passed,
            violations=violations,
            warnings=warnings
        )
    
    def validate_slipbox(self, slips_dir: Path) -> List[ValidationResult]:
        """Validate all org files in a directory."""
        results = []
        
        if not slips_dir.exists():
            raise FileNotFoundError(f"Slips directory not found: {slips_dir}")
        
        # Find all .org files
        org_files = list(slips_dir.glob("*.org"))
        
        for org_file in org_files:
            try:
                slip = self.parser.parse_slip(org_file)
                result = self.validate_slip(slip)
                results.append(result)
            except Exception as e:
                # Create failed result for unparseable files
                results.append(ValidationResult(
                    file_path=org_file,
                    passed=False,
                    violations=[Violation(
                        rule="PARSE_ERROR",
                        message=f"Failed to parse file: {str(e)}",
                        severity=Severity.ERROR
                    )],
                    warnings=[]
                ))
        
        return results