"""
Unit tests for myfirstETL pipeline
"""

import pandas as pd
import pytest

from pipeline import transform_data
from transforms import normalize_column, remove_outliers, standardize_column
from utils import format_size, validate_config


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


def test_format_size():
    """Test size formatting"""
    assert format_size(1024) == "1.00 KB"
    assert format_size(1048576) == "1.00 MB"
    assert format_size(500) == "500.00 B"


def test_transform_data():
    """Test data transformation"""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
    result = transform_data(df)

    assert len(result) == 5
    assert "value_scaled" in result.columns or len(result.columns) > 1


def test_standardize_column():
    """Test column standardization"""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
    result = standardize_column(df, "value")

    assert "value_standardized" in result.columns
    assert abs(result["value_standardized"].mean()) < 0.01  # Close to 0
    assert abs(result["value_standardized"].std() - 1.0) < 0.01  # Close to 1


def test_normalize_column():
    """Test column normalization"""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
    result = normalize_column(df, "value")

    assert "value_normalized" in result.columns
    assert result["value_normalized"].min() == 0.0
    assert result["value_normalized"].max() == 1.0


def test_remove_outliers():
    """Test outlier removal"""
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 100]})  # 100 is an outlier
    result = remove_outliers(df, "value", n_std=2.0)

    assert len(result) < len(df)  # Some rows removed
    assert 100 not in result["value"].values  # Outlier removed
