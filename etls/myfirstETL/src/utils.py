"""
Utility functions for myfirstETL
"""

from typing import Any


def validate_config(config: dict) -> bool:
    """
    Validate ETL configuration

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, raises ValueError otherwise
    """
    required_keys = ["name", "schedule", "compute", "parameters", "gcp"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    return True


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human readable string

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
