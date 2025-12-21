"""
Unit tests for pipeline
"""

import pytest

from utils import validate_config


def test_validate_config():
    """Test configuration validation"""
    valid_config = {
        "name": "test",
        "schedule": "0 8 * * *",
        "compute": {},
        "parameters": {},
        "gcp": {},
    }
    assert validate_config(valid_config) is True

    invalid_config = {"name": "test"}
    with pytest.raises(ValueError):
        validate_config(invalid_config)
