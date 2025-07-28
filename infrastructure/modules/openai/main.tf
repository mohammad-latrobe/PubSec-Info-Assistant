# Azure OpenAI Module for PubSec Information Assistant
# Creates Azure OpenAI service with text embedding model deployment

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_service_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = var.sku_name

  # Network configuration
  public_network_access_enabled = var.public_network_access_enabled
  
  # Identity configuration
  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Text Embedding Model Deployment
resource "azurerm_cognitive_deployment" "text_embedding" {
  name                 = var.embedding_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = var.embedding_model_name
    version = var.embedding_model_version
  }

  sku {
    name     = var.scale_type
    capacity = var.embedding_capacity
  }
}

# Optional GPT Model Deployment (for future use)
resource "azurerm_cognitive_deployment" "gpt_model" {
  count                = var.deploy_gpt_model ? 1 : 0
  name                 = var.gpt_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = var.gpt_model_name
    version = var.gpt_model_version
  }

  sku {
    name     = var.scale_type
    capacity = var.gpt_capacity
  }
}
