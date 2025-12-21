"""
Utility functions for myfirstETL
"""


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
