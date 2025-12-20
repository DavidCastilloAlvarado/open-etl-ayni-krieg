"""
Base pipeline utilities for Kubeflow
Dynamic pipeline creation based on ETL configuration
"""

from pathlib import Path
from typing import Any, Dict

import yaml
from kfp import dsl


def load_etl_config(etl_name: str) -> Dict[str, Any]:
    """
    Load ETL configuration from resources/config.yaml

    Args:
        etl_name: Name of the ETL

    Returns:
        Configuration dictionary
    """
    config_path = Path(f"etls/{etl_name}/resources/config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


def create_pipeline_for_etl(etl_name: str, image: str):
    """
    Dynamically create a Kubeflow pipeline for any ETL based on its config

    Args:
        etl_name: Name of the ETL
        image: Docker image URI

    Returns:
        Pipeline function
    """
    # Load ETL configuration
    config = load_etl_config(etl_name)

    # Get default parameters
    default_params = config.get("parameters", {})

    @dsl.pipeline(
        name=config["name"],
        description=config.get("description", f"ETL Pipeline for {etl_name}"),
    )
    def dynamic_pipeline(**kwargs):
        """
        Dynamically generated pipeline

        Args:
            **kwargs: Pipeline parameters from config
        """
        # Merge default params with provided kwargs
        params = {**default_params, **kwargs}

        # Build container arguments from parameters
        arguments = []
        for key, value in params.items():
            if key != "image":  # Skip image parameter
                arguments.extend([f"--{key.replace('_', '-')}", str(value)])

        # Create ETL task
        etl_task = dsl.ContainerOp(
            name=f"{etl_name}-task",
            image=image,
            arguments=arguments,
        )

        # Set resource limits
        etl_task = etl_task.set_cpu_limit(config["compute"]["cpu"])
        etl_task = etl_task.set_memory_limit(config["compute"]["memory"])

        # Add retry policy
        etl_task = etl_task.set_retry(
            num_retries=2, backoff_duration="60s", backoff_factor=2.0
        )

        # Set timeout if specified
        if "timeout" in config["compute"]:
            etl_task = etl_task.set_timeout(config["compute"]["timeout"])

        return etl_task

    # Set default parameter values for the pipeline
    dynamic_pipeline.__defaults__ = tuple(default_params.values())

    return dynamic_pipeline

