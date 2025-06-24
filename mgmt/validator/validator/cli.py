"""Command-line interface for slipbox validation."""

import click
from pathlib import Path
from typing import Optional


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
    click.echo(f"Validating slipbox at {path} (format: {format}, fix: {fix})")
    # TODO: Implement validation logic


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def structure(path: Path) -> None:
    """Validate slip structure (properties, word count)."""
    click.echo(f"Validating slip structure at {path}")
    # TODO: Implement structure validation


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def links(path: Path) -> None:
    """Validate link integrity."""
    click.echo(f"Validating links at {path}")
    # TODO: Implement link validation


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=".")
def orphans(path: Path) -> None:
    """Find orphaned slips with no connections."""
    click.echo(f"Finding orphans at {path}")
    # TODO: Implement orphan detection


if __name__ == "__main__":
    main()