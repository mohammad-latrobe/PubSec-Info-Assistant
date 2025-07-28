variable "openai_service_name" {
  description = "Name of the Azure OpenAI service"
  type        = string
  validation {
    condition     = length(var.openai_service_name) >= 2 && length(var.openai_service_name) <= 64 && can(regex("^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$", var.openai_service_name))
    error_message = "OpenAI service name must be between 2 and 64 characters, start and end with alphanumeric characters, and contain only letters, numbers, and hyphens."
  }
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
  description = "SKU for the OpenAI service"
  type        = string
  default     = "S0"
  validation {
    condition     = contains(["F0", "S0"], var.sku_name)
    error_message = "SKU must be either F0 (free) or S0 (standard)."
  }
}

variable "public_network_access_enabled" {
  description = "Whether public network access is enabled"
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

variable "scale_type" {
  description = "Scale type for the deployment"
  type        = string
  default     = "Standard"
  validation {
    condition     = contains(["Standard", "Provisioned"], var.scale_type)
    error_message = "Scale type must be either Standard or Provisioned."
  }
}

variable "embedding_capacity" {
  description = "Capacity for the embedding deployment"
  type        = number
  default     = 120
}

variable "deploy_gpt_model" {
  description = "Whether to deploy a GPT model"
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

variable "tags" {
  description = "Tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
