# Azure Functions Module for PubSec Information Assistant
# Creates Azure Function App with consumption plan and managed identity

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

# Service Plan for Azure Functions
resource "azurerm_service_plan" "main" {
  name                = var.service_plan_name
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = var.sku_name

  tags = var.tags
}

# Storage Account for Function App (if not provided)
# Note: We'll always use the main storage account passed as a variable
# resource "azurerm_storage_account" "function_storage" {
#   count                    = var.storage_account_name == null ? 1 : 0
#   name                     = "${var.function_app_name}st${random_integer.suffix.result}"
#   resource_group_name      = var.resource_group_name
#   location                 = var.location
#   account_tier             = "Standard"
#   account_replication_type = "LRS"
#   
#   tags = var.tags
# }

resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}

# Application Insights for monitoring
resource "azurerm_application_insights" "main" {
  name                = "${var.function_app_name}-insights"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"

  tags = var.tags

  lifecycle {
    ignore_changes = [workspace_id]
  }
}

# Azure Function App
resource "azurerm_linux_function_app" "main" {
  name                = var.function_app_name
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = azurerm_service_plan.main.id

  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_account_access_key

  # Function App configuration
  site_config {
    always_on = false

    application_stack {
      python_version = var.python_version
    }

    # CORS settings
    cors {
      allowed_origins     = var.cors_allowed_origins
      support_credentials = false
    }
  }

  # Managed Identity
  identity {
    type = "SystemAssigned"
  }

  # Application settings
  app_settings = merge(
    {
      "FUNCTIONS_WORKER_RUNTIME"       = "python"
      "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.main.instrumentation_key
      "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main.connection_string
      "WEBSITE_RUN_FROM_PACKAGE"       = "1"
      
      # Azure OpenAI settings
      "AZURE_OPENAI_ENDPOINT"          = var.openai_endpoint
      "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME" = var.embedding_deployment_name
      
      # Azure Search settings
      "AZURE_SEARCH_SERVICE_ENDPOINT"  = var.search_endpoint
      "AZURE_SEARCH_INDEX"             = var.search_index_name
      
      # Storage settings
      "BLOB_STORAGE_ACCOUNT_ENDPOINT"  = var.blob_storage_endpoint
      "BLOB_CONTENT_CONTAINER_NAME"    = var.content_container_name
      
      # LTU API settings
      "KNOWLEDGE_BASE_API_URL"         = var.knowledge_base_api_url
      "APIM_SUBSCRIPTION_KEY"          = var.apim_subscription_key
      "KB_NAME_FILTER"                 = var.kb_name_filter
      "KB_ACTIVE_FILTER"               = var.kb_active_filter
      "KB_STATUS_FILTER"               = var.kb_status_filter
      
      # Processing settings
      "CHUNK_TARGET_SIZE"              = var.chunk_target_size
      "EMBEDDING_VECTOR_SIZE"          = var.embedding_vector_size
      "LOCAL_DEBUG"                    = "false"
    },
    var.additional_app_settings
  )

  tags = var.tags
}
