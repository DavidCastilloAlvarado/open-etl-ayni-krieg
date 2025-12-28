import argparse
import logging
import os
import signal
import sys
from pathlib import Path

import pandas as pd
import requests
import yaml

from transforms import (
    filter_and_agg_violent_deaths,
    render_year_trend_and_change,
    select_and_clean_columns,
)
from utils import upload_to_gcs


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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    }

    cookies = {
        '_ga_2VDX9N2E9M': 'GS2.1.s1766243911$o1$g0$t1766243913$j58$l0$h0',
        '_ga': 'GA1.1.522129251.1766241622',
        '__Host-nc_sameSiteCookielax': 'true',
        '__Host-nc_sameSiteCookiestrict': 'true',
        '_ga_F3MSER51W2': 'GS2.1.s1766280361$o3$g0$t1766280366$j55$l0$h0',
        '_ga_H4TV4M96SY': 'GS2.1.s1766294636$o4$g0$t1766294636$j60$l0$h0',
        'ocys5xdczo5m': '45fec6c6e200c7b283a4cfa233e1cc54',
        'oc_sessionPassphrase': '2yPaYiOujtOAtS1qb1SOPbhmit0Caud9wcYPvd4A7PTX4wlhtUpWt2%2BLYCQ03kd43mWYAGyks%2BRziqbhiu3ny%2FuO6a6EmpDABhDclLiF7LxpgM7xiCsiRsq24Tga6%2Fuv',
        '__cf_bm': 'HaVDlhD6lwmjC1W.yb99MNkU1Fp4dIIcywFv2hheBM4-1766963090-1.0.1.1-Ay6uRG5H4TBZcxAykROodEois6pF9GYte_usP9NkpsBfylZ7a872vISUmVxsaDF3DqSoEnuzSC9SL7OIvDg9qIS4fawOf.2z0NvxdcBIBVg',
    }
    response = requests.get(url, headers=headers, cookies=cookies)

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
        output_path: Path to GCS location (gs://bucket/path/file.csv) or local path
    """
    # Save locally first
    local_path = "data/homicidios_detallado.csv"
    os.makedirs("data", exist_ok=True)
    df.to_csv(local_path, index=False)
    logging.info(f"Saved locally: {local_path}")

    # Upload to GCS if output_path is a GCS path
    if output_path.startswith("gs://"):
        upload_to_gcs(local_path, output_path)

    logging.info(f"ETL completed: {len(df)} rows processed")


def run_etl(input_path: str = None, output_path: str = None):
    """
    Main ETL execution

    Args:
        input_path: Optional input path (overrides config)
        output_path: Optional output path (overrides config)
    """
    logging.info("Starting Sinadef Analysis ETL")
    # Load configuration
    config = load_config()

    # Use provided paths or default from config
    input_path = input_path or config["parameters"]["input_path"]
    output_path = output_path or config["parameters"]["output_path"]

    # ETL Process
    df_raw = extract_data(input_path)
    df = transform_data(df_raw)
    render_year_trend_and_change(df)
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
    parser = argparse.ArgumentParser(description="sinadef analysis pipeline")
    parser.add_argument("--input-path", type=str, help="Path to input data")
    parser.add_argument("--output-path", type=str, help="Path to output data")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")

    args = parser.parse_args()

    # Set timeout if provided
    if args.timeout:

        def timeout_handler(signum, frame):
            raise TimeoutError(f"ETL execution exceeded timeout of {args.timeout} seconds")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(args.timeout)
        logging.info(f"Timeout set to {args.timeout} seconds")

    try:
        # Run ETL with provided arguments
        run_etl(input_path=args.input_path, output_path=args.output_path)
    finally:
        if args.timeout:
            signal.alarm(0)  # Disable alarm
