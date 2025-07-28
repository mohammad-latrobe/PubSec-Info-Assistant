# Terraform Backend Configuration for Development Environment
# This file configures remote state storage in Azure Storage

terraform {
  backend "azurerm" {
    # These values should be configured through terraform init -backend-config
    # or through environment variables:
    # ARM_ACCESS_KEY or ARM_SAS_TOKEN for authentication
    
    # Storage account name for Terraform state
    # Set via: terraform init -backend-config="storage_account_name=<storage_account>"
    # storage_account_name = "terraformstateXXXX"
    
    # Container name for Terraform state
    # Set via: terraform init -backend-config="container_name=tfstate"
    # container_name = "tfstate"
    
    # Key for this environment's state file
    # Set via: terraform init -backend-config="key=pubsec-ia-dev.tfstate"
    # key = "pubsec-ia-dev.tfstate"
    
    # Resource group containing the storage account
    # Set via: terraform init -backend-config="resource_group_name=<rg_name>"
    # resource_group_name = "rg-terraform-state"
  }
}
