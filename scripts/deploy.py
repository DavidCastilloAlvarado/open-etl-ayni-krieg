#!/usr/bin/env python3
"""
Deploy ETL to Vertex AI
"""

import argparse
import os
import sys
from pathlib import Path

import yaml
from google.cloud import aiplatform
from kfp import compiler

# Add project root to Python path to import kubeflow module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kubeflow.pipelines.base_pipeline import create_pipeline_for_etl  # noqa: E402


def load_etl_config(etl_name: str) -> dict:
    """Load ETL config from resources/config.yaml"""
    config_path = Path(f"etls/{etl_name}/resources/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"ETL config not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def load_env_config(environment: str) -> dict:
    """Load configuration from environment variables"""
    # All configuration comes from environment variables
    required_vars = [
        "GCP_PROJECT_ID",
        "GCP_REGION",
        "GCP_SERVICE_ACCOUNT",
        "GCP_BUCKET",
        "CONTAINER_REGISTRY",
        "CONTAINER_REGISTRY_PROJECT",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"See SECURITY.md for configuration details."
        )

    # Build config from environment variables
    config = {
        "environment": environment,
        "gcp": {
            "project_id": os.getenv("GCP_PROJECT_ID"),
            "region": os.getenv("GCP_REGION"),
            "bucket": os.getenv("GCP_BUCKET"),
            "service_account": os.getenv("GCP_SERVICE_ACCOUNT"),
        },
        "vertex_ai": {
            "pipeline_root": f"gs://{os.getenv('GCP_BUCKET')}/pipelines",
        },
        "container_registry": {
            "registry": os.getenv("CONTAINER_REGISTRY", "gcr.io"),
            "project": os.getenv("CONTAINER_REGISTRY_PROJECT"),
        },
    }

    return config


def get_pipeline_function(etl_name: str, image: str):
    """
    Create pipeline function dynamically from ETL config
    Args:
        etl_name: Name of the ETL
        image: Docker image URI
    Returns:
        Pipeline function
    """
    try:
        return create_pipeline_for_etl(etl_name, image)
    except Exception as e:
        print(f"Error: Could not create pipeline for {etl_name}: {e}", file=sys.stderr)
        sys.exit(1)


def compile_pipeline(etl_name: str, image: str, output_path: str):
    """Compile Kubeflow pipeline to JSON"""
    print(f"Compiling pipeline for {etl_name}...")

    pipeline_func = get_pipeline_function(etl_name, image)

    compiler.Compiler().compile(pipeline_func=pipeline_func, package_path=output_path)

    print(f"✅ Pipeline compiled: {output_path}")


def deploy_pipeline(
    etl_name: str,
    environment: str,
    pipeline_path: str,
):
    """Deploy pipeline to Vertex AI"""
    print("\n" + "=" * 70)
    print(f"Deploying {etl_name} to Vertex AI")
    print("=" * 70)

    # Load configurations
    etl_config = load_etl_config(etl_name)
    env_config = load_env_config(environment)

    # Initialize Vertex AI
    aiplatform.init(
        project=env_config["gcp"]["project_id"],
        location=env_config["gcp"]["region"],
    )

    print(f"Project:     {env_config['gcp']['project_id']}")
    print(f"Region:      {env_config['gcp']['region']}")
    print(f"Environment: {environment}")
    print("=" * 70)

    # Create pipeline job
    job = aiplatform.PipelineJob(
        display_name=f"{etl_name}-{environment}",
        template_path=pipeline_path,
        pipeline_root=env_config["vertex_ai"]["pipeline_root"],
        enable_caching=False,
    )

    # Submit the pipeline
    print("\nSubmitting pipeline job...")
    job.submit(service_account=env_config["gcp"]["service_account"])

    print("\n✅ Pipeline job submitted!")
    print(f"Job Name: {job.display_name}")
    print(f"Job URL:  {job._dashboard_uri()}")

    # Create or update schedule
    if "schedule" in etl_config:
        schedule_name = f"{etl_name}-schedule-{environment}"
        print(f"\nManaging schedule: {etl_config['schedule']}")

        try:
            # Delete existing schedules with the same display name
            existing_schedules = aiplatform.PipelineJobSchedule.list(
                filter=f'display_name="{schedule_name}"'
            )
            
            for existing_schedule in existing_schedules:
                print(f"Deleting existing schedule: {existing_schedule.resource_name}")
                existing_schedule.delete()
            
            # Create new schedule
            schedule = aiplatform.PipelineJobSchedule(
                pipeline_job=job,
                display_name=schedule_name,
            )

            schedule.create(
                cron=etl_config["schedule"],
                max_concurrent_run_count=1,
                max_run_count=None,  # Run indefinitely
                service_account=env_config["gcp"]["service_account"],
            )

            print(f"✅ Schedule created: {etl_config['schedule']}")
            print(f"Schedule Name: {schedule.display_name}")

        except Exception as e:
            print(f"⚠️  Warning: Could not manage schedule: {e}", file=sys.stderr)
            print("You may need to manage the schedule manually.")

    print("\n" + "=" * 70)
    print("Deployment completed successfully!")
    print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy ETL to Vertex AI")
    parser.add_argument("--etl-name", required=True, help="Name of the ETL")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "prod"],
        help="Target environment",
    )
    parser.add_argument(
        "--image",
        help="Docker image URI (if not provided, will be constructed)",
    )
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="Skip pipeline compilation",
    )

    args = parser.parse_args()

    # Construct image name if not provided
    if not args.image:
        env_config = load_env_config(args.environment)
        registry = env_config["container_registry"]["registry"]
        project = env_config["container_registry"]["project"]
        # Convert entire image name to lowercase for Docker compatibility
        args.image = f"{registry}/{project}/{args.etl_name}:latest".lower()

    # Pipeline output path
    pipeline_path = f"/tmp/{args.etl_name}_pipeline.json"

    # Compile pipeline
    if not args.skip_compile:
        compile_pipeline(args.etl_name, args.image, pipeline_path)

    # Deploy to Vertex AI
    deploy_pipeline(args.etl_name, args.environment, pipeline_path)


if __name__ == "__main__":
    main()
