#!/usr/bin/env python3
"""
List all available ETLs in the etls/ directory
"""

import sys
from pathlib import Path


def list_etls():
    """
    Discover all ETL projects in the etls/ directory

    Returns:
        List of ETL names
    """
    etls_dir = Path("etls")

    if not etls_dir.exists():
        print("Error: etls/ directory not found", file=sys.stderr)
        return []

    etls = []
    for item in etls_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            # Check if it has required files
            if (item / "pyproject.toml").exists() and (item / "resources" / "config.yaml").exists():
                etls.append(item.name)

    return sorted(etls)


def main():
    """Main entry point"""
    etls = list_etls()

    if not etls:
        print("No ETLs found in etls/ directory")
        return

    print("Available ETLs:")
    print("=" * 50)
    for etl in etls:
        print(f"  - {etl}")
    print("=" * 50)
    print(f"Total: {len(etls)} ETL(s)")


if __name__ == "__main__":
    main()
