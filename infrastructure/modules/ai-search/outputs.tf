output "search_service_id" {
  description = "ID of the Azure AI Search service"
  value       = azurerm_search_service.main.id
}

output "search_service_name" {
  description = "Name of the Azure AI Search service"
  value       = azurerm_search_service.main.name
}

output "search_service_endpoint" {
  description = "Endpoint URL of the Azure AI Search service"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "search_service_principal_id" {
  description = "Principal ID of the search service managed identity"
  value       = azurerm_search_service.main.identity[0].principal_id
}

output "search_index_name" {
  description = "Name of the search index"
  value       = azurerm_search_index.kb_articles.name
}

output "primary_key" {
  description = "Primary admin key for the search service"
  value       = azurerm_search_service.main.primary_key
  sensitive   = true
}

output "query_keys" {
  description = "Query keys for the search service"
  value       = azurerm_search_service.main.query_keys
  sensitive   = true
}
