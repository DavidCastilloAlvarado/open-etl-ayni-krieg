#!/usr/bin/env python3
"""
Build Docker image for an ETL
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml


def load_env_config(environment: str) -> dict:
    """Load configuration from environment variables"""
    # All configuration comes from environment variables
    required_vars = ["CONTAINER_REGISTRY", "CONTAINER_REGISTRY_PROJECT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"See SECURITY.md for configuration details."
        )
    
    return {
        "environment": environment,
        "container_registry": {
            "registry": os.getenv("CONTAINER_REGISTRY", "gcr.io"),
            "project": os.getenv("CONTAINER_REGISTRY_PROJECT"),
        },
    }


def build_image(etl_name: str, environment: str, tag: str = "latest"):
    """
    Build Docker image for an ETL

    Args:
        etl_name: Name of the ETL
        environment: Target environment (dev/prod)
        tag: Docker image tag
    """
    etl_path = Path(f"etls/{etl_name}")

    if not etl_path.exists():
        print(f"Error: ETL not found: {etl_path}", file=sys.stderr)
        sys.exit(1)

    # Load environment config
    env_config = load_env_config(environment)

    # Build image name
    registry = env_config["container_registry"]["registry"]
    project = env_config["container_registry"]["project"]
    image_name = f"{registry}/{project}/{etl_name.lower()}:{tag}"

    print("=" * 70)
    print(f"Building Docker image for {etl_name}")
    print("=" * 70)
    print(f"ETL Path:    {etl_path}")
    print(f"Image:       {image_name}")
    print(f"Environment: {environment}")
    print("=" * 70)

    # Build Docker image
    try:
        subprocess.run(
            ["docker", "build", "-t", image_name, "."],
            cwd=etl_path,
            check=True,
        )
        print("\n✅ Image built successfully!")
        print(f"Image: {image_name}")
        return image_name

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error building image: {e}", file=sys.stderr)
        sys.exit(1)


def push_image(image_name: str):
    """
    Push Docker image to registry

    Args:
        image_name: Full image name with registry
    """
    print("\n" + "=" * 70)
    print(f"Pushing image to registry")
    print("=" * 70)

    try:
        subprocess.run(["docker", "push", image_name], check=True)
        print("\n✅ Image pushed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error pushing image: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build Docker image for an ETL")
    parser.add_argument("--etl-name", required=True, help="Name of the ETL")
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "prod"],
        help="Target environment",
    )
    parser.add_argument(
        "--tag",
        default="latest",
        help="Docker image tag (default: latest)",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push image to registry after building",
    )

    args = parser.parse_args()

    # Build image
    image_name = build_image(args.etl_name, args.environment, args.tag)

    # Push if requested
    if args.push:
        push_image(image_name)


if __name__ == "__main__":
    main()
