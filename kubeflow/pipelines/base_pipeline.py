"""
Base pipeline utilities for Kubeflow
Dynamic pipeline creation based on ETL configuration
"""

import os
from pathlib import Path
from typing import Any

import yaml
from jinja2 import StrictUndefined, Template
from kfp import dsl


def load_etl_config(etl_name: str) -> dict[str, Any]:
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
    def dynamic_pipeline():
        """
        Dynamically generated pipeline
        All parameters are passed directly to the container from the ETL config.
        """
        # Build container arguments from parameters
        arguments = []
        for key, value in default_params.items():
            if key != "image":  # Skip image parameter
                # Render template if value contains {{ }}
                if isinstance(value, str) and "{{" in value and "}}" in value:
                    template = Template(value, undefined=StrictUndefined)
                    value = template.render(**os.environ)
                arguments.extend([f"--{key.replace('_', '-')}", str(value)])

        # Create ETL task using KFP v2 container component
        @dsl.container_component
        def etl_component():
            return dsl.ContainerSpec(
                image=image,
                command=["python", "src/pipeline.py"],
                args=arguments,
            )

        # Create the task
        task = etl_component()

        # Set resource limits using KFP v2 API
        task.set_cpu_limit(config["compute"]["cpu"])
        task.set_memory_limit(config["compute"]["memory"])

        # Set timeout if configured
        if "timeout" in config["compute"]:
            timeout_seconds = int(config["compute"]["timeout"])
            task.set_timeout(seconds=timeout_seconds)

        # Set retry policy
        task.set_retry(num_retries=config["retry"]["max_retries"],
                       backoff_duration=config["retry"]["backoff_duration"],
                       backoff_factor=config["retry"]["backoff_factor"])

    return dynamic_pipeline
