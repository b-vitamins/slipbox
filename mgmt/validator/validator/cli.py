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
    ExternalResourceValidator,
    TemplateComplianceValidator,
    HeadlineNodesValidator,
    TagAnalysisValidator,
    ConsistencyValidator
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
            SlipLinkValidator(slips_dir, config.validation.orphan_grace_period_days, config.validation.org_roam_priority),
            TemplateComplianceValidator(expected_formats=config.validation.expected_formats),
            HeadlineNodesValidator(check_duplicate_ids=True),
            TagAnalysisValidator()  # Tag inheritance and consistency
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
@click.option("--show-formats", is_flag=True, help="Show detected filename formats")
@click.option("--expected-format", multiple=True, help="Expected filename format patterns (regex)")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def template(show_formats: bool, expected_format: list[str], path: Path) -> None:
    """Validate template compliance and filename consistency."""
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create template validator
        validators = [TemplateComplianceValidator(
            expected_formats=list(expected_format) if expected_format else None
        )]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Show format summary if requested
        if show_formats or not expected_format:
            template_validator = validators[0]
            format_summary = template_validator.get_format_summary()
            
            if format_summary:
                click.echo("\nDetected filename formats:")
                total_files = sum(info["count"] for info in format_summary.values())
                
                for format_type, info in sorted(format_summary.items(), 
                                              key=lambda x: x[1]["count"], 
                                              reverse=True):
                    percentage = (info["count"] / total_files * 100) if total_files > 0 else 0
                    click.echo(f"  {format_type}: {info['count']} files ({percentage:.1f}%)")
                    if info["example"]:
                        click.echo(f"    Example: {info['example']}")
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Template validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def headlines(path: Path) -> None:
    """Validate headline nodes within slips."""
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create headline validator
        validators = [HeadlineNodesValidator(check_duplicate_ids=True)]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Count headline nodes found
        total_nodes = 0
        files_with_nodes = 0
        for result in results:
            # Parse the slip to get headline count
            from .parser import OrgParser
            parser = OrgParser()
            try:
                slip = parser.parse_slip(result.file_path)
                if slip.headline_nodes:
                    files_with_nodes += 1
                    total_nodes += len(slip.headline_nodes)
            except:
                pass
        
        if total_nodes == 0:
            click.echo("\n✓ No headline nodes found in slipbox")
        else:
            click.echo(f"\nFound {total_nodes} headline node(s) in {files_with_nodes} file(s)")
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Headline validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--show-stats", is_flag=True, help="Show tag usage statistics")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def tags(show_stats: bool, path: Path) -> None:
    """Analyze tag usage and inheritance."""
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create tag validator
        validators = [TagAnalysisValidator()]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Show tag statistics if requested
        if show_stats:
            from collections import Counter
            from .parser import OrgParser
            
            tag_counts = Counter()
            parser = OrgParser()
            
            for result in results:
                try:
                    slip = parser.parse_slip(result.file_path)
                    if slip.properties.filetags:
                        tag_counts.update(slip.properties.filetags)
                except:
                    pass
            
            if tag_counts:
                click.echo("\nTag usage statistics:")
                for tag, count in tag_counts.most_common(20):
                    click.echo(f"  {tag}: {count} files")
                
                if len(tag_counts) > 20:
                    click.echo(f"  ... and {len(tag_counts) - 20} more tags")
            else:
                click.echo("\nNo tags found in slipbox")
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Tag analysis failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--db-path", type=click.Path(exists=True, path_type=Path), 
              help="Path to org-roam.db file")
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def consistency(db_path: Optional[Path], path: Path) -> None:
    """Check consistency with org-roam database."""
    # Find slipbox root and load configuration
    slipbox_root = find_slipbox_root(path)
    config = SlipboxConfig.find_and_load(slipbox_root)
    slips_dir = find_slips_directory(slipbox_root, config)
    
    try:
        # Create consistency validator
        validators = [ConsistencyValidator(db_path)]
        engine = ValidationEngine(validators)
        
        results = engine.validate_slipbox(slips_dir)
        
        # Report results
        reporter = ConsoleReporter()
        reporter.report_results(results)
        
        # Check if database was found
        consistency_validator = validators[0]
        if consistency_validator.db_validator.db_available:
            click.echo(f"\n✓ Connected to org-roam database at {consistency_validator.db_validator.db_path}")
            click.echo(f"  Found {len(consistency_validator.db_validator.db_nodes)} nodes in database")
        else:
            click.echo("\n⚠ No org-roam database found. Install org-roam and run 'M-x org-roam-db-sync'")
        
        # Exit with error code if any validation failed
        if any(not result.passed for result in results):
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Consistency check failed: {str(e)}", err=True)
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