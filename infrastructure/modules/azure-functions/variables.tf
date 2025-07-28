variable "function_app_name" {
  description = "Name of the Azure Function App"
  type        = string
  validation {
    condition     = length(var.function_app_name) >= 2 && length(var.function_app_name) <= 60 && can(regex("^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$", var.function_app_name))
    error_message = "Function app name must be between 2 and 60 characters, start and end with alphanumeric characters, and contain only letters, numbers, and hyphens."
  }
}

variable "service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for the resources"
  type        = string
}

variable "sku_name" {
  description = "SKU for the App Service Plan"
  type        = string
  default     = "Y1"
  validation {
    condition     = contains(["Y1", "EP1", "EP2", "EP3"], var.sku_name)
    error_message = "SKU must be one of: Y1 (Consumption), EP1, EP2, EP3 (Premium)."
  }
}

variable "python_version" {
  description = "Python version for the function app"
  type        = string
  default     = "3.11"
  validation {
    condition     = contains(["3.8", "3.9", "3.10", "3.11"], var.python_version)
    error_message = "Python version must be one of: 3.8, 3.9, 3.10, 3.11."
  }
}

variable "storage_account_name" {
  description = "Name of the storage account for the function app (optional, will create if not provided)"
  type        = string
  default     = null
}

variable "storage_account_access_key" {
  description = "Access key for the storage account (required if storage_account_name is provided)"
  type        = string
  default     = null
  sensitive   = true
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

# Azure service endpoints
variable "openai_endpoint" {
  description = "Azure OpenAI service endpoint"
  type        = string
}

variable "embedding_deployment_name" {
  description = "Name of the embedding deployment in Azure OpenAI"
  type        = string
  default     = "text-embedding-ada-002"
}

variable "search_endpoint" {
  description = "Azure AI Search service endpoint"
  type        = string
}

variable "search_index_name" {
  description = "Name of the search index"
  type        = string
  default     = "kb-articles-index"
}

variable "blob_storage_endpoint" {
  description = "Azure Blob Storage endpoint"
  type        = string
}

variable "content_container_name" {
  description = "Name of the content container in blob storage"
  type        = string
  default     = "content"
}

# LTU API configuration
variable "knowledge_base_api_url" {
  description = "URL of the Knowledge Base API"
  type        = string
  default     = "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase"
}

variable "apim_subscription_key" {
  description = "APIM subscription key for the Knowledge Base API"
  type        = string
  sensitive   = true
}

variable "kb_name_filter" {
  description = "Default KB name filter"
  type        = string
  default     = "ICT"
}

variable "kb_active_filter" {
  description = "Default KB active filter"
  type        = string
  default     = "true"
}

variable "kb_status_filter" {
  description = "Default KB status filter"
  type        = string
  default     = "published"
}

# Processing configuration
variable "chunk_target_size" {
  description = "Target size for text chunks"
  type        = number
  default     = 750
}

variable "embedding_vector_size" {
  description = "Size of embedding vectors"
  type        = number
  default     = 1536
}

variable "additional_app_settings" {
  description = "Additional application settings for the function app"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
