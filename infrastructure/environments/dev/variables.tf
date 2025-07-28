# Environment Configuration Variables
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "PubSec Information Assistant"
}

variable "project_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "pubsec-ia"
  validation {
    condition     = length(var.project_prefix) <= 10 && can(regex("^[a-z0-9-]+$", var.project_prefix))
    error_message = "Project prefix must be 10 characters or less and contain only lowercase letters, numbers, and hyphens."
  }
}

# Resource Group Configuration
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for the resources"
  type        = string
  default     = "East US"
}

# Azure AI Search Configuration
variable "search_sku" {
  description = "SKU for the Azure AI Search service"
  type        = string
  default     = "standard"
}

variable "search_replica_count" {
  description = "Number of replicas for the search service"
  type        = number
  default     = 1
}

variable "search_partition_count" {
  description = "Number of partitions for the search service"
  type        = number
  default     = 1
}

variable "search_public_access" {
  description = "Whether public network access is enabled for search service"
  type        = bool
  default     = true
}

variable "search_index_name" {
  description = "Name of the search index"
  type        = string
  default     = "kb-articles-index"
}

# Azure OpenAI Configuration
variable "openai_location" {
  description = "Azure region for OpenAI service (leave empty to use same as main location)"
  type        = string
  default     = ""
}

variable "openai_sku" {
  description = "SKU for the Azure OpenAI service"
  type        = string
  default     = "S0"
}

variable "openai_public_access" {
  description = "Whether public network access is enabled for OpenAI service"
  type        = bool
  default     = true
}

variable "embedding_deployment_name" {
  description = "Name of the text embedding deployment"
  type        = string
  default     = "text-embedding-ada-002"
}

variable "embedding_model_name" {
  description = "Name of the embedding model"
  type        = string
  default     = "text-embedding-ada-002"
}

variable "embedding_model_version" {
  description = "Version of the embedding model"
  type        = string
  default     = "2"
}

variable "embedding_capacity" {
  description = "Capacity for the embedding deployment"
  type        = number
  default     = 120
}

variable "embedding_dimensions" {
  description = "Dimensions for vector embeddings"
  type        = number
  default     = 1536
}

variable "deploy_gpt_model" {
  description = "Whether to deploy a GPT model for future use"
  type        = bool
  default     = false
}

variable "gpt_deployment_name" {
  description = "Name of the GPT deployment"
  type        = string
  default     = "gpt-35-turbo"
}

variable "gpt_model_name" {
  description = "Name of the GPT model"
  type        = string
  default     = "gpt-35-turbo"
}

variable "gpt_model_version" {
  description = "Version of the GPT model"
  type        = string
  default     = "0613"
}

variable "gpt_capacity" {
  description = "Capacity for the GPT deployment"
  type        = number
  default     = 120
}

# Azure Functions Configuration
variable "function_sku" {
  description = "SKU for the Azure Functions service plan"
  type        = string
  default     = "Y1"
}

variable "python_version" {
  description = "Python version for the function app"
  type        = string
  default     = "3.11"
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

# LTU API Configuration
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

# Processing Configuration
variable "chunk_target_size" {
  description = "Target size for text chunks"
  type        = number
  default     = 750
}

# Common Tags
variable "tags" {
  description = "Tags to be applied to all resources"
  type        = map(string)
  default     = {
    Department = "IT"
    CostCenter = "12345"
    Owner      = "DevOps Team"
  }
}
