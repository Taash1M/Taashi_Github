# architecture_config.py
# This file demonstrates a programmatic approach to defining and managing a multi-cloud data platform configuration.
# At the Director level, this represents a strategic artifact for Infrastructure-as-Code (IaC) planning.

from typing import Dict, Any
import json

# Define a multi-cloud configuration for core data platform resources
PLATFORM_CONFIG: Dict[str, Any] = {
    "aws_prod": {
        "cloud_provider": "AWS",
        "region": "us-west-2",
        "data_lake_bucket": "taashim-prod-data-lake-s3",
        "compute_engine": "Databricks (Photon)",
        "cost_optimization_strategy": "Reserved Instances & Auto-Scaling Clusters",
        "security_model": "IAM Roles & S3 Bucket Policies",
        "data_governance_tool": "AWS Lake Formation"
    },
    "gcp_dev": {
        "cloud_provider": "GCP",
        "region": "us-central1",
        "data_lake_bucket": "taashim-dev-data-lake-gcs",
        "compute_engine": "BigQuery (Standard Slots)",
        "cost_optimization_strategy": "Slot Reservations & Time-based Partitioning",
        "security_model": "Service Accounts & VPC Service Controls",
        "data_governance_tool": "Collibra (Integrated)"
    },
    "azure_staging": {
        "cloud_provider": "Azure",
        "region": "eastus",
        "data_lake_bucket": "taashim-staging-data-lake-adls",
        "compute_engine": "Azure Synapse Analytics",
        "cost_optimization_strategy": "Pause/Resume Compute & Reserved Capacity",
        "security_model": "Azure Active Directory & RBAC",
        "data_governance_tool": "Azure Purview"
    }
}

def get_platform_config(env: str) -> Dict[str, Any]:
    """
    Retrieves the configuration for a specified environment.
    This function simulates a lookup from a configuration store (e.g., Consul, Vault, or a simple JSON file).
    """
    if env not in PLATFORM_CONFIG:
        raise ValueError(f"Environment '{env}' not found in configuration.")
    return PLATFORM_CONFIG[env]

def generate_terraform_vars(env: str, output_file: str = "terraform.tfvars.json"):
    """
    Generates a mock terraform variable file for the specified environment.
    """
    config = get_platform_config(env)
    
    # Select only the variables relevant for a terraform deployment
    tf_vars = {
        "cloud_provider": config["cloud_provider"],
        "region": config["region"],
        "data_lake_name": config["data_lake_bucket"],
        "compute_sku": config["compute_engine"],
        "governance_tool": config["data_governance_tool"]
    }
    
    with open(output_file, "w") as f:
        json.dump(tf_vars, f, indent=4)
    
    print(f"Successfully generated Terraform variables for {env} in {output_file}")

if __name__ == "__main__":
    # Example 1: Retrieve and print the production configuration
    prod_config = get_platform_config("aws_prod")
    print("--- AWS Production Configuration ---")
    print(json.dumps(prod_config, indent=4))
    
    # Example 2: Generate a mock Terraform variable file for the staging environment
    generate_terraform_vars("azure_staging", "azure_staging.tfvars.json")
