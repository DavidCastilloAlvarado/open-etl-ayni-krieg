#!/usr/bin/env python3
"""
Validate ETL configurations
"""

import sys
from pathlib import Path

import yaml


def validate_etl_config(etl_dir: Path) -> list[str]:
    """
    Validate a single ETL configuration

    Args:
        etl_dir: Path to ETL directory

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    config_path = etl_dir / "resources" / "config.yaml"

    if not config_path.exists():
        errors.append(f"{etl_dir.name}: Missing resources/config.yaml")
        return errors

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        required_keys = ["name", "schedule", "compute", "parameters"]
        for key in required_keys:
            if key not in config:
                errors.append(f"{etl_dir.name}: Missing required key '{key}'")

        # Validate compute section
        if "compute" in config:
            compute_keys = ["cpu", "memory"]
            for key in compute_keys:
                if key not in config["compute"]:
                    errors.append(f"{etl_dir.name}: Missing compute.{key}")

    except yaml.YAMLError as e:
        errors.append(f"{etl_dir.name}: Invalid YAML - {e}")
    except Exception as e:
        errors.append(f"{etl_dir.name}: {str(e)}")

    return errors


def main():
    """Main entry point"""
    etls_dir = Path("etls")

    if not etls_dir.exists():
        print("Error: etls/ directory not found")
        sys.exit(1)

    all_errors = []

    for etl_dir in etls_dir.iterdir():
        if not etl_dir.is_dir() or etl_dir.name.startswith("."):
            continue

        errors = validate_etl_config(etl_dir)
        if not errors:
            print(f"✅ {etl_dir.name}: Valid configuration")
        else:
            all_errors.extend(errors)

    if all_errors:
        print("\n❌ Configuration errors found:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)

    print("\n✅ All ETL configurations are valid!")


if __name__ == "__main__":
    main()
