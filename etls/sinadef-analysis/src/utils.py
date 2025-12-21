
import logging

from google.cloud import storage

# import tweepy


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
    if not gcs_path.startswith("gs://"):
        raise ValueError(f"GCS path must start with 'gs://': {gcs_path}")

    # Parse GCS path: gs://bucket/path/to/file.csv
    gcs_path_clean = gcs_path.replace("gs://", "")
    bucket_name = gcs_path_clean.split("/")[0]
    blob_name = "/".join(gcs_path_clean.split("/")[1:])

    logging.info(f"Uploading to GCS: {gcs_path}")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    logging.info(f"Successfully uploaded to {gcs_path}")


# def post_to_xcom(image_path: str, message: str = ""):
#     """
#     Post a message with an image to X.com (formerly Twitter)

#     Args:
#         image_path: Path to the image file (e.g., 'doc/report.png')
#         message: Post text content (optional)

#     Raises:
#         FileNotFoundError: If image file doesn't exist
#         ValueError: If required X.com credentials are not set
#         Exception: If posting to X.com fails

#     Environment variables required:
#         XCOM_API_KEY: X.com API key
#         XCOM_API_SECRET: X.com API secret
#         XCOM_ACCESS_TOKEN: X.com access token
#         XCOM_ACCESS_TOKEN_SECRET: X.com access token secret
#     """
#     # Validate image exists
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"Image file not found: {image_path}")

#     # Get X.com credentials from environment variables
#     api_key = os.getenv("XCOM_API_KEY")
#     api_secret = os.getenv("XCOM_API_SECRET")
#     access_token = os.getenv("XCOM_ACCESS_TOKEN")
#     access_token_secret = os.getenv("XCOM_ACCESS_TOKEN_SECRET")

#     if not all([api_key, api_secret, access_token, access_token_secret]):
#         raise ValueError(
#             "Missing X.com credentials. Set XCOM_API_KEY, XCOM_API_SECRET, "
#             "XCOM_ACCESS_TOKEN, and XCOM_ACCESS_TOKEN_SECRET environment variables"
#         )

#     try:
#         # Authenticate with X.com API v2
#         client = tweepy.Client(
#             consumer_key=api_key,
#             consumer_secret=api_secret,
#             access_token=access_token,
#             access_token_secret=access_token_secret
#         )

#         # For media upload, we need API v1.1
#         auth = tweepy.OAuth1UserHandler(
#             api_key, api_secret, access_token, access_token_secret
#         )
#         api = tweepy.API(auth)

#         logging.info(f"Uploading media: {image_path}")
#         media = api.media_upload(filename=image_path)

#         logging.info(f"Posting to X.com with media")
#         response = client.create_tweet(text=message, media_ids=[media.media_id])

#         logging.info(f"Successfully posted to X.com with ID: {response.data['id']}")
#         return response.data["id"]

#     except Exception as e:
#         logging.error(f"Failed to post to X.com: {str(e)}")
#         raise
