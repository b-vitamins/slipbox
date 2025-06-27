"""Configuration management for slipbox validation."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Use tomllib for Python 3.11+ or tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
    def load_toml(file_path):
        with open(file_path, 'rb') as f:
            return tomllib.load(f)
else:
    import tomli
    def load_toml(file_path):
        with open(file_path, 'rb') as f:
            return tomli.load(f)

# For writing TOML files, use a simple implementation
def dump_toml(data, file_path):
    """Simple TOML writer for configuration files."""
    lines = []
    
    for section, values in data.items():
        lines.append(f"[{section}]")
        for key, value in values.items():
            if isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key} = {value}")
            else:
                lines.append(f"{key} = \"{value}\"")
        lines.append("")
    
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))


@dataclass
class ValidationConfig:
    """Configuration for validation settings."""
    word_limit: int = 500
    check_external_links: bool = True
    orphan_grace_period_days: int = 7
    url_timeout_seconds: int = 10
    # Org-roam integration settings
    org_roam_priority: bool = True  # Prioritize ID properties for Org-roam compatibility
    require_custom_id: bool = True  # Whether CUSTOM_ID is required (traditional Zettelkasten)
    expected_formats: Optional[list[str]] = None  # Expected filename formats (regex patterns)


@dataclass
class PathConfig:
    """Configuration for directory paths."""
    slips_dir: str = "slips/"
    bibliography_dir: str = "bibliography/"
    media_dir: str = "assets/"


@dataclass
class SlipboxConfig:
    """Complete slipbox configuration."""
    validation: ValidationConfig
    paths: PathConfig
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'SlipboxConfig':
        """Load configuration from slipbox.toml file."""
        # Default configuration
        validation_config = ValidationConfig()
        path_config = PathConfig()
        
        # Try to load from file
        if config_path and config_path.exists():
            try:
                config_data = load_toml(config_path)
                
                # Load validation settings
                if "validation" in config_data:
                    val_data = config_data["validation"]
                    validation_config = ValidationConfig(
                        word_limit=val_data.get("word_limit", validation_config.word_limit),
                        check_external_links=val_data.get("check_external_links", validation_config.check_external_links),
                        orphan_grace_period_days=val_data.get("orphan_grace_period_days", validation_config.orphan_grace_period_days),
                        url_timeout_seconds=val_data.get("url_timeout_seconds", validation_config.url_timeout_seconds),
                        org_roam_priority=val_data.get("org_roam_priority", validation_config.org_roam_priority),
                        require_custom_id=val_data.get("require_custom_id", validation_config.require_custom_id),
                        expected_formats=val_data.get("expected_formats")
                    )
                
                # Load path settings
                if "paths" in config_data:
                    path_data = config_data["paths"]
                    path_config = PathConfig(
                        slips_dir=path_data.get("slips_dir", path_config.slips_dir),
                        bibliography_dir=path_data.get("bibliography_dir", path_config.bibliography_dir),
                        media_dir=path_data.get("media_dir", path_config.media_dir)
                    )
                    
            except Exception:
                # Use defaults if config file is malformed
                pass
        
        return cls(validation=validation_config, paths=path_config)
    
    @classmethod
    def find_and_load(cls, start_path: Path) -> 'SlipboxConfig':
        """Find and load slipbox.toml starting from given path."""
        # Look for slipbox.toml in current directory or parent directories
        current = start_path.resolve()
        
        while current != current.parent:
            config_file = current / "slipbox.toml"
            if config_file.exists():
                return cls.load(config_file)
            current = current.parent
        
        # No config found, use defaults
        return cls.load(None)


def create_sample_config(output_path: Path) -> None:
    """Create a sample slipbox.toml configuration file."""
    sample_config = {
        "validation": {
            "word_limit": 500,
            "check_external_links": True,
            "orphan_grace_period_days": 7,
            "url_timeout_seconds": 10,
            "org_roam_priority": True,
            "require_custom_id": True,
            "expected_formats": ["^\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}-\\d{2}-"]
        },
        "paths": {
            "slips_dir": "slips/",
            "bibliography_dir": "bibliography/",
            "media_dir": "assets/"
        }
    }
    
    dump_toml(sample_config, output_path)