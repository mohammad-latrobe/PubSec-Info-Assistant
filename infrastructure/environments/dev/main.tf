# PubSec Information Assistant - Development Environment
# Main Terraform configuration that orchestrates all modules

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the Azure Provider
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Data sources
data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# Generate unique suffix for resource names
resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}

# Local values
locals {
  # Common tags for all resources
  common_tags = merge(var.tags, {
    Environment   = var.environment
    Project      = var.project_name
    ManagedBy    = "Terraform"
    CreatedDate  = formatdate("YYYY-MM-DD", timestamp())
  })

  # Resource naming with unique suffix
  storage_account_name    = "${var.project_prefix}st${random_integer.suffix.result}"
  function_app_name      = "${var.project_prefix}-func-${var.environment}-${random_integer.suffix.result}"
  search_service_name    = "${var.project_prefix}-search-${var.environment}-${random_integer.suffix.result}"
  openai_service_name    = "${var.project_prefix}-openai-${var.environment}-${random_integer.suffix.result}"
  service_plan_name      = "${var.project_prefix}-plan-${var.environment}-${random_integer.suffix.result}"
}

# Storage Account Module
module "storage" {
  source = "../../modules/storage"

  storage_account_name = local.storage_account_name
  resource_group_name  = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = local.common_tags
}

# Azure AI Search Module
module "ai_search" {
  source = "../../modules/ai-search"

  search_service_name           = local.search_service_name
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  sku                          = var.search_sku
  replica_count               = var.search_replica_count
  partition_count             = var.search_partition_count
  public_network_access_enabled = var.search_public_access
  index_name                   = var.search_index_name
  embedding_dimensions         = var.embedding_dimensions
  tags                        = local.common_tags
}

# Azure OpenAI Module
module "openai" {
  source = "../../modules/openai"

  openai_service_name           = local.openai_service_name
  resource_group_name          = azurerm_resource_group.main.name
  location                     = var.openai_location != "" ? var.openai_location : azurerm_resource_group.main.location
  sku_name                     = var.openai_sku
  public_network_access_enabled = var.openai_public_access
  embedding_deployment_name    = var.embedding_deployment_name
  embedding_model_name         = var.embedding_model_name
  embedding_model_version      = var.embedding_model_version
  embedding_capacity          = var.embedding_capacity
  deploy_gpt_model            = var.deploy_gpt_model
  gpt_deployment_name         = var.gpt_deployment_name
  gpt_model_name              = var.gpt_model_name
  gpt_model_version           = var.gpt_model_version
  gpt_capacity                = var.gpt_capacity
  tags                        = local.common_tags
}

# Azure Functions Module
module "azure_functions" {
  source = "../../modules/azure-functions"

  function_app_name           = local.function_app_name
  service_plan_name          = local.service_plan_name
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  sku_name                   = var.function_sku
  python_version             = var.python_version
  storage_account_name       = module.storage.storage_account_name
  cors_allowed_origins       = var.cors_allowed_origins

  # Service endpoints
  openai_endpoint             = module.openai.openai_endpoint
  embedding_deployment_name   = module.openai.embedding_deployment_name
  search_endpoint            = module.ai_search.search_service_endpoint
  search_index_name          = module.ai_search.search_index_name
  blob_storage_endpoint      = module.storage.primary_blob_endpoint
  content_container_name     = module.storage.content_container_name

  # LTU API configuration
  apim_subscription_key      = var.apim_subscription_key
  knowledge_base_api_url     = var.knowledge_base_api_url
  kb_name_filter            = var.kb_name_filter
  kb_active_filter          = var.kb_active_filter
  kb_status_filter          = var.kb_status_filter

  # Processing settings
  chunk_target_size         = var.chunk_target_size
  embedding_vector_size     = var.embedding_dimensions

  tags = local.common_tags

  depends_on = [module.storage, module.ai_search, module.openai]
}

# Role Assignments for Function App
resource "azurerm_role_assignment" "function_storage_blob_contributor" {
  scope                = module.storage.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.azure_functions.function_app_principal_id
}

resource "azurerm_role_assignment" "function_search_contributor" {
  scope                = module.ai_search.search_service_id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = module.azure_functions.function_app_principal_id
}

resource "azurerm_role_assignment" "function_openai_user" {
  scope                = module.openai.openai_service_id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.azure_functions.function_app_principal_id
}
