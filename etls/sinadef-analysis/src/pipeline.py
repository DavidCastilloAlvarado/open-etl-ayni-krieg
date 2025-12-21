"""
Main pipeline for myfirstETL
ETL process using pandas and scikit-learn
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import requests
import yaml

from transforms import filter_and_agg_violent_deaths, select_and_clean_columns


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
    # Download CSV from URL

    url = input_path
    csv_path = "./data/SINADEF_DATOS_ABIERTOS.csv"

    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Check response status
    if response.status_code != 200:
        logging.error(f"ERROR: HTTP {response.status_code} - Failed to download")
        logging.error("Please download manually")
    # Check content type - should be text/csv or application/octet-stream, not text/html
    elif "text/html" in response.headers.get("Content-Type", ""):
        logging.error("ERROR: Cloudflare is blocking the download (got HTML instead of CSV)")
        logging.error("Please download manually")
    else:
        with open(csv_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Downloaded successfully: {len(response.content) / 1024 / 1024:.2f} MB")
    # Read the CSV
    df_raw = pd.read_csv(csv_path, sep=",", encoding="utf-8")
    return df_raw


def transform_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data using scikit-learn

    Args:
        df: Input DataFrame

    Returns:
        Transformed DataFrame
    """
    logging.info("Transforming data...")
    df = select_and_clean_columns(df_raw)
    df = filter_and_agg_violent_deaths(df)
    return df


def load_data(df: pd.DataFrame, output_path: str):
    """
    Load transformed data to destination
    Args:
        df: Transformed DataFrame
        output_path: Path to output CSV file
    """
    df.to_csv("data/homicidios_detallado.csv", index=False)
    logging.info(f"ETL completed: {len(df)} rows processed")


def run_etl(input_path: str = None, output_path: str = None):
    """
    Main ETL execution

    Args:
        input_path: Optional input path (overrides config)
        output_path: Optional output path (overrides config)
    """
    logging.info("Starting myfirstETL")
    # Load configuration
    config = load_config()

    # Use provided paths or default from config
    input_path = input_path or config["parameters"]["input_path"]
    output_path = output_path or config["parameters"]["output_path"]

    # ETL Process
    df_raw = extract_data(input_path)
    df = transform_data(df_raw)
    load_data(df, output_path)
    logging.info("ETL completed successfully!")


if __name__ == "__main__":
    # Configure logging to stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="myfirstETL pipeline")
    parser.add_argument("--input-path", type=str, help="Path to input data")
    parser.add_argument("--output-path", type=str, help="Path to output data")

    args = parser.parse_args()

    # Run ETL with provided arguments
    run_etl(input_path=args.input_path, output_path=args.output_path)
