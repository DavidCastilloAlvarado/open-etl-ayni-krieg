"""
Main pipeline for myfirstETL
ETL process using pandas and scikit-learn
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml
from sklearn.preprocessing import StandardScaler


def load_config():
    """Load configuration from resources/config.yaml"""
    config_path = Path(__file__).parent.parent / "resources" / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def extract_data(input_path: str) -> pd.DataFrame:
    """
    Extract data from source

    Args:
        input_path: Path to input CSV file

    Returns:
        DataFrame with extracted data
    """
    print(f"Extracting data from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Extracted {len(df)} rows")
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data using scikit-learn

    Args:
        df: Input DataFrame

    Returns:
        Transformed DataFrame
    """
    print("Transforming data...")
    scaler = StandardScaler()

    # Example transformation - scale numeric columns
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_cols) > 0:
        df[f"{numeric_cols[0]}_scaled"] = scaler.fit_transform(df[[numeric_cols[0]]])

    print("Transformation complete")
    return df


def load_data(df: pd.DataFrame, output_path: str):
    """
    Load transformed data to destination

    Args:
        df: Transformed DataFrame
        output_path: Path to output CSV file
    """
    print(f"Loading data to: {output_path}")
    df.to_csv(output_path, index=False)
    print(f"ETL completed: {len(df)} rows processed")


def run_etl(input_path: str = None, output_path: str = None):
    """
    Main ETL execution

    Args:
        input_path: Optional input path (overrides config)
        output_path: Optional output path (overrides config)
    """
    print("=" * 50)
    print("Starting myfirstETL")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Use provided paths or default from config
    input_path = input_path or config["parameters"]["input_path"]
    output_path = output_path or config["parameters"]["output_path"]

    # ETL Process
    df = extract_data(input_path)
    df = transform_data(df)
    load_data(df, output_path)

    print("=" * 50)
    print("ETL completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="myfirstETL pipeline")
    parser.add_argument("--input-path", type=str, help="Path to input data")
    parser.add_argument("--output-path", type=str, help="Path to output data")
    
    args = parser.parse_args()
    
    # Run ETL with provided arguments
    run_etl(input_path=args.input_path, output_path=args.output_path)
