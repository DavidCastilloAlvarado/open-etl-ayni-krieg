#!/usr/bin/env python3
"""
Test script to list Vertex AI Pipeline Schedules
"""

import os
from google.cloud import aiplatform

# Load environment variables
project_id = os.getenv("GCP_PROJECT_ID")
region = os.getenv("GCP_REGION")

if not project_id or not region:
    print("Error: Set GCP_PROJECT_ID and GCP_REGION environment variables")
    exit(1)

# Initialize Vertex AI
aiplatform.init(project=project_id, location=region)

print(f"Listing schedules in project: {project_id}, region: {region}\n")

# Test 1: List all schedules
print("=" * 70)
print("All schedules:")
print("=" * 70)
all_schedules = aiplatform.PipelineJobSchedule.list()
for schedule in all_schedules:
    print(f"  Name: {schedule.display_name}")
    print(f"  Resource: {schedule.resource_name}")
    print(f"  State: {schedule.state}")
    print("-" * 70)

print(f"\nTotal schedules: {len(all_schedules)}\n")

# Test 2: Filter by display name
schedule_name = "myfirstETL-schedule-dev"
print("=" * 70)
print(f"Filtered schedules (display_name=\"{schedule_name}\"):")
print("=" * 70)
filtered_schedules = aiplatform.PipelineJobSchedule.list(
    filter=f'display_name="{schedule_name}"'
)
for schedule in filtered_schedules:
    print(f"  Name: {schedule.display_name}")
    print(f"  Resource: {schedule.resource_name}")
    print(f"  State: {schedule.state}")
    print("-" * 70)

print(f"\nFiltered schedules: {len(filtered_schedules)}")
