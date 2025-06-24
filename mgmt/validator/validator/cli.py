"""Command-line interface for slipbox validation."""

import sys
import click
from pathlib import Path
from typing import Optional

from .validators import (
    ValidationEngine, 
    SlipStructureValidator, 
    SlipLinkValidator, 
    OrphanDetector,
    ExternalResourceValidator
)
from .reporters import ConsoleReporter
from .config import SlipboxConfig


def find_slipbox_root(start_path: Path) -> Path:
    """Find slipbox root directory (contains slips/ and potentially slipbox.toml)."""
    current = start_path.resolve()
    
    # Look for slipbox.toml or slips/ directory
    while current != current.parent:
        if (current / "slipbox.toml").exists() or (current / "slips").exists():
            return current
        current = current.parent
    
    # Default to start_path if nothing found
    return start_path


def find_slips_directory(slipbox_root: Path, config: SlipboxConfig) -> Path:
    """Find slips directory using configuration."""
    slips_dir = slipbox_root / config.paths.slips_dir
    if slips_dir.exists():
        return slips_dir
    
    # Fallback to various common patterns
    for pattern in ["slips/", "notes/", "."]:
        candidate = slipbox_root / pattern
        if candidate.exists():
            return candidate
    
    return slips_dir  # Return configured path even if it doesn't exist


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
@click.option("--no-external", is_flag=True, help="Skip external resource validation")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def check(format: str, fix: bool, no_external: bool, path: Path) -> None:
    """Run all validation checks on slipbox."""
    if fix:
        click.echo("Auto-fix not yet implemented", err=True)
        sys.exit(1)
    
    if format != "console":
        click.echo("Only console format currently supported", err=True)
        sys.exit(1)
    
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Run all available validators
        validators = [
            SlipStructureValidator(
                config.validation.word_limit,
                config.validation.org_roam_priority,
                config.validation.require_custom_id,
                check_duplicate_aliases=True
            ),
            SlipLinkValidator(slips_dir, config.validation.orphan_grace_period_days, config.validation.org_roam_priority)
        ]
        
        # Add external validation unless disabled
        if not no_external:
            validators.append(ExternalResourceValidator(
                slipbox_root,
                check_urls=config.validation.check_external_links,
                url_timeout=config.validation.url_timeout_seconds
            ))
        
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
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create structure validator
        validators = [SlipStructureValidator(
            config.validation.word_limit,
            config.validation.org_roam_priority,
            config.validation.require_custom_id,
            check_duplicate_aliases=True
        )]
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
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create link validator
        validators = [SlipLinkValidator(slips_dir, config.validation.orphan_grace_period_days)]
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
@click.option("--grace-days", type=int, default=None, help="Grace period for new slips (days)")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def orphans(grace_days: Optional[int], path: Path) -> None:
    """Find orphaned slips with no connections."""
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    # Use command line value or config default
    grace_period = grace_days if grace_days is not None else config.validation.orphan_grace_period_days
    
    try:
        # Create orphan detector
        validators = [OrphanDetector(slips_dir, grace_period)]
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
            click.echo(f"✓ No orphaned slips found (grace period: {grace_period} days)", color="green")
        else:
            click.echo(f"Found {orphan_count} orphaned slip(s) (grace period: {grace_period} days)")
            
    except Exception as e:
        click.echo(f"Orphan detection failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--no-urls", is_flag=True, help="Skip URL reachability checks")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def external(no_urls: bool, path: Path) -> None:
    """Validate external resources (bibliography, URLs, media files)."""
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create external validator
        check_urls = config.validation.check_external_links and not no_urls
        validators = [ExternalResourceValidator(
            slipbox_root,
            check_urls=check_urls,
            url_timeout=config.validation.url_timeout_seconds
        )]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"External validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("output_path", type=click.Path(path_type=Path), default="slipbox.toml")
def init_config(output_path: Path) -> None:
    """Create a sample slipbox.toml configuration file."""
    from .config import create_sample_config
    
    if output_path.exists():
        click.echo(f"Configuration file already exists: {output_path}", err=True)
        if not click.confirm("Overwrite existing file?"):
            sys.exit(1)
    
    try:
        create_sample_config(output_path)
        click.echo(f"Created sample configuration: {output_path}")
        click.echo("Edit this file to customize validation settings.")
    except Exception as e:
        click.echo(f"Failed to create configuration: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()