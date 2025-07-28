variable "search_service_name" {
  description = "Name of the Azure AI Search service"
  type        = string
  validation {
    condition     = length(var.search_service_name) >= 2 && length(var.search_service_name) <= 60 && can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.search_service_name))
    error_message = "Search service name must be between 2 and 60 characters, start and end with alphanumeric characters, and contain only lowercase letters, numbers, and hyphens."
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

variable "sku" {
  description = "SKU for the search service"
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"], var.sku)
    error_message = "SKU must be one of: free, basic, standard, standard2, standard3, storage_optimized_l1, storage_optimized_l2."
  }
}

variable "replica_count" {
  description = "Number of replicas for the search service"
  type        = number
  default     = 1
  validation {
    condition     = var.replica_count >= 1 && var.replica_count <= 12
    error_message = "Replica count must be between 1 and 12."
  }
}

variable "partition_count" {
  description = "Number of partitions for the search service"
  type        = number
  default     = 1
  validation {
    condition     = contains([1, 2, 3, 4, 6, 12], var.partition_count)
    error_message = "Partition count must be one of: 1, 2, 3, 4, 6, 12."
  }
}

variable "public_network_access_enabled" {
  description = "Whether public network access is enabled"
  type        = bool
  default     = true
}

variable "index_name" {
  description = "Name of the search index"
  type        = string
  default     = "kb-articles-index"
}

variable "embedding_dimensions" {
  description = "Dimensions for vector embeddings"
  type        = number
  default     = 1536
}

variable "tags" {
  description = "Tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
