
import logging

from google.cloud import storage


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


def upload_to_gcs(local_path: str, gcs_path: str):
    """
    Upload a local file to Google Cloud Storage

    Args:
        local_path: Path to local file
        gcs_path: GCS destination path (gs://bucket/path/to/file)
    Raises:
        ValueError: If gcs_path doesn't start with 'gs://'
    """
    if not gcs_path.startswith('gs://'):
        raise ValueError(f"GCS path must start with 'gs://': {gcs_path}")

    # Parse GCS path: gs://bucket/path/to/file.csv
    gcs_path_clean = gcs_path.replace('gs://', '')
    bucket_name = gcs_path_clean.split('/')[0]
    blob_name = '/'.join(gcs_path_clean.split('/')[1:])

    logging.info(f"Uploading to GCS: {gcs_path}")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    logging.info(f"Successfully uploaded to {gcs_path}")
