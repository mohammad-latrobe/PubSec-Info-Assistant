# Output values for the development environment

# Resource Group
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

# Storage Account
output "storage_account_name" {
  description = "Name of the storage account"
  value       = module.storage.storage_account_name
}

output "storage_account_endpoint" {
  description = "Primary blob endpoint of the storage account"
  value       = module.storage.primary_blob_endpoint
}

output "content_container_name" {
  description = "Name of the content container"
  value       = module.storage.content_container_name
}

# Azure AI Search
output "search_service_name" {
  description = "Name of the Azure AI Search service"
  value       = module.ai_search.search_service_name
}

output "search_service_endpoint" {
  description = "Endpoint URL of the Azure AI Search service"
  value       = module.ai_search.search_service_endpoint
}

output "search_index_name" {
  description = "Name of the search index"
  value       = module.ai_search.search_index_name
}

# Azure OpenAI
output "openai_service_name" {
  description = "Name of the Azure OpenAI service"
  value       = module.openai.openai_service_name
}

output "openai_endpoint" {
  description = "Endpoint URL of the Azure OpenAI service"
  value       = module.openai.openai_endpoint
}

output "embedding_deployment_name" {
  description = "Name of the text embedding deployment"
  value       = module.openai.embedding_deployment_name
}

# Azure Functions
output "function_app_name" {
  description = "Name of the Azure Function App"
  value       = module.azure_functions.function_app_name
}

output "function_app_hostname" {
  description = "Default hostname of the function app"
  value       = module.azure_functions.function_app_hostname
}

output "function_app_url" {
  description = "URL of the function app"
  value       = "https://${module.azure_functions.function_app_hostname}"
}

# Function URLs
output "process_kb_articles_url" {
  description = "URL for the ProcessKBArticles function"
  value       = "https://${module.azure_functions.function_app_hostname}/api/ProcessKBArticles"
}

output "index_kb_chunks_url" {
  description = "URL for the IndexKBChunks function"
  value       = "https://${module.azure_functions.function_app_hostname}/api/IndexKBChunks"
}

# Resource IDs
output "storage_account_id" {
  description = "ID of the storage account"
  value       = module.storage.storage_account_id
}

output "search_service_id" {
  description = "ID of the Azure AI Search service"
  value       = module.ai_search.search_service_id
}

output "openai_service_id" {
  description = "ID of the Azure OpenAI service"
  value       = module.openai.openai_service_id
}

output "function_app_id" {
  description = "ID of the Azure Function App"
  value       = module.azure_functions.function_app_id
}

# Portal Links
output "azure_portal_resource_group_url" {
  description = "Direct link to the resource group in Azure Portal"
  value       = "https://portal.azure.com/#@/resource/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${azurerm_resource_group.main.name}"
}

output "azure_portal_function_app_url" {
  description = "Direct link to the function app in Azure Portal"
  value       = "https://portal.azure.com/#@/resource${module.azure_functions.function_app_id}"
}

output "azure_portal_search_service_url" {
  description = "Direct link to the search service in Azure Portal"
  value       = "https://portal.azure.com/#@/resource${module.ai_search.search_service_id}"
}

output "azure_portal_openai_service_url" {
  description = "Direct link to the OpenAI service in Azure Portal"
  value       = "https://portal.azure.com/#@/resource${module.openai.openai_service_id}"
}

# Deployment Summary
output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment             = var.environment
    resource_group         = azurerm_resource_group.main.name
    location              = azurerm_resource_group.main.location
    storage_account       = module.storage.storage_account_name
    search_service        = module.ai_search.search_service_name
    openai_service        = module.openai.openai_service_name
    function_app          = module.azure_functions.function_app_name
    search_index          = module.ai_search.search_index_name
    embedding_deployment  = module.openai.embedding_deployment_name
  }
}
