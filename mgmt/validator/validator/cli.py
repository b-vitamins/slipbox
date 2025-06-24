"""Command-line interface for slipbox validation."""

import sys
import click
from pathlib import Path
from typing import Optional

from .validators import ValidationEngine, SlipStructureValidator, SlipLinkValidator, OrphanDetector
from .reporters import ConsoleReporter


def find_slips_directory(start_path: Path) -> Path:
    """Find slips directory starting from given path."""
    # Try current directory first
    if (start_path / "slips").exists():
        return start_path / "slips"
    
    # If start_path is already slips directory
    if start_path.name == "slips" and start_path.exists():
        return start_path
    
    # Default to start_path if nothing else works
    return start_path


@click.group()
@click.version_option()
def main() -> None:
    """Slipbox validation and linting tools."""
    pass


@main.command()
@click.option(
    "--format",
    type=click.Choice(["console", "json"]),
    default="console",
    help="Output format",
)
@click.option("--fix", is_flag=True, help="Auto-fix violations when possible")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def check(format: str, fix: bool, path: Path) -> None:
    """Run all validation checks on slipbox."""
    if fix:
        click.echo("Auto-fix not yet implemented", err=True)
        sys.exit(1)
    
    if format != "console":
        click.echo("Only console format currently supported", err=True)
        sys.exit(1)
    
    slips_dir = find_slips_directory(path)
    
    try:
        # Run all available validators
        validators = [
            SlipStructureValidator(),
            SlipLinkValidator(slips_dir)
        ]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def structure(path: Path) -> None:
    """Validate slip structure (properties, word count)."""
    slips_dir = find_slips_directory(path)
    
    try:
        # Create structure validator
        validators = [SlipStructureValidator()]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Structure validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def links(path: Path) -> None:
    """Validate link integrity."""
    slips_dir = find_slips_directory(path)
    
    try:
        # Create link validator
        validators = [SlipLinkValidator(slips_dir)]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Link validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--grace-days", default=7, help="Grace period for new slips (days)")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def orphans(grace_days: int, path: Path) -> None:
    """Find orphaned slips with no connections."""
    slips_dir = find_slips_directory(path)
    
    try:
        # Create orphan detector
        validators = [OrphanDetector(slips_dir, grace_days)]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Show summary of orphans found
        orphan_count = sum(
            len([v for v in result.violations + result.warnings if v.rule == "ORPHANED_SLIP"])
            for result in results
        )
        
        if orphan_count == 0:
            click.echo(f"✓ No orphaned slips found (grace period: {grace_days} days)", color="green")
        else:
            click.echo(f"Found {orphan_count} orphaned slip(s) (grace period: {grace_days} days)")
            
    except Exception as e:
        click.echo(f"Orphan detection failed: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()