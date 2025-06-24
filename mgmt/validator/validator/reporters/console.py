"""Console output for validation results."""

from typing import List
from pathlib import Path

from ..models import ValidationResult, Violation, Severity


class ConsoleReporter:
    """Pretty-print validation results to console."""
    
    def __init__(self, use_colors: bool = True):
        """Initialize reporter with optional color support."""
        self.use_colors = use_colors
    
    def report_results(self, results: List[ValidationResult]) -> None:
        """Report validation results with violations grouped by file."""
        if not results:
            self._print("No files to validate", "yellow")
            return
        
        total_files = len(results)
        failed_files = [r for r in results if not r.passed]
        total_violations = sum(len(r.violations) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        
        # Print results for each file
        for result in results:
            if result.passed and not result.warnings:
                continue  # Skip files with no issues
                
            # File header
            status = "✗" if not result.passed else "⚠"
            color = "red" if not result.passed else "yellow"
            self._print(f"\n{status} {result.file_path}", color, bold=True)
            
            # Print violations
            if result.violations:
                for violation in result.violations:
                    self._print_violation(violation, "red")
            
            # Print warnings  
            if result.warnings:
                for warning in result.warnings:
                    self._print_violation(warning, "yellow")
        
        # Summary
        self._print_summary(total_files, len(failed_files), total_violations, total_warnings)
    
    def _print_violation(self, violation: Violation, color: str) -> None:
        """Print a single violation with formatting."""
        # Format line number if available
        location = f":{violation.line_number}" if violation.line_number else ""
        
        # Format severity indicator
        if violation.severity == Severity.ERROR:
            indicator = "ERROR"
        elif violation.severity == Severity.WARNING:
            indicator = "WARNING"
        else:
            indicator = "INFO"
        
        # Print formatted violation
        self._print(f"  {indicator}{location}: {violation.message}", color)
        if violation.rule:
            self._print(f"    Rule: {violation.rule}", "dim")
    
    def _print_summary(self, total_files: int, failed_files: int, 
                      total_violations: int, total_warnings: int) -> None:
        """Print validation summary."""
        self._print("\n" + "="*60, "dim")
        
        # Files summary
        if failed_files == 0:
            self._print(f"✓ All {total_files} files passed validation", "green", bold=True)
        else:
            self._print(f"✗ {failed_files}/{total_files} files failed validation", "red", bold=True)
        
        # Issues summary
        if total_violations > 0:
            self._print(f"  {total_violations} error(s)", "red")
        if total_warnings > 0:
            self._print(f"  {total_warnings} warning(s)", "yellow")
        
        if total_violations == 0 and total_warnings == 0:
            self._print("  No issues found", "green")
    
    def _print(self, message: str, color: str = "default", bold: bool = False) -> None:
        """Print message with optional color and formatting."""
        if not self.use_colors:
            print(message)
            return
        
        # ANSI color codes
        colors = {
            "red": "\033[91m",
            "green": "\033[92m", 
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "dim": "\033[90m",
            "default": "\033[0m"
        }
        
        color_code = colors.get(color, colors["default"])
        bold_code = "\033[1m" if bold else ""
        reset_code = "\033[0m"
        
        print(f"{bold_code}{color_code}{message}{reset_code}")
    
    def summary(self, results: List[ValidationResult]) -> None:
        """Print just the summary without detailed violations."""
        total_files = len(results)
        failed_files = len([r for r in results if not r.passed])
        total_violations = sum(len(r.violations) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        
        self._print_summary(total_files, failed_files, total_violations, total_warnings)