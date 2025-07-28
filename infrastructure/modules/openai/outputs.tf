output "openai_service_id" {
  description = "ID of the Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.id
}

output "openai_service_name" {
  description = "Name of the Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.name
}

output "openai_endpoint" {
  description = "Endpoint URL of the Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_principal_id" {
  description = "Principal ID of the OpenAI service managed identity"
  value       = azurerm_cognitive_account.openai.identity[0].principal_id
}

output "embedding_deployment_name" {
  description = "Name of the text embedding deployment"
  value       = azurerm_cognitive_deployment.text_embedding.name
}

output "gpt_deployment_name" {
  description = "Name of the GPT deployment (if deployed)"
  value       = var.deploy_gpt_model ? azurerm_cognitive_deployment.gpt_model[0].name : null
}

output "primary_access_key" {
  description = "Primary access key for the OpenAI service"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}
