"""
Data transformation functions for myfirstETL
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def standardize_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Standardize a column using StandardScaler (mean=0, std=1)

    Args:
        df: Input DataFrame
        column: Column name to standardize

    Returns:
        DataFrame with standardized column
    """
    scaler = StandardScaler()
    df[f"{column}_standardized"] = scaler.fit_transform(df[[column]])
    return df


def normalize_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Normalize a column using MinMaxScaler (range 0-1)

    Args:
        df: Input DataFrame
        column: Column name to normalize

    Returns:
        DataFrame with normalized column
    """
    scaler = MinMaxScaler()
    df[f"{column}_normalized"] = scaler.fit_transform(df[[column]])
    return df


def remove_outliers(df: pd.DataFrame, column: str, n_std: float = 3.0) -> pd.DataFrame:
    """
    Remove outliers beyond n standard deviations

    Args:
        df: Input DataFrame
        column: Column name to check
        n_std: Number of standard deviations

    Returns:
        DataFrame with outliers removed
    """
    mean = df[column].mean()
    std = df[column].std()
    return df[(df[column] >= mean - n_std * std) & (df[column] <= mean + n_std * std)]
