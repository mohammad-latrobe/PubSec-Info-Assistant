# Azure AI Search Module for PubSec Information Assistant
# Creates Azure AI Search service with S0 tier and security configurations

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

# Azure AI Search Service
resource "azurerm_search_service" "main" {
  name                         = var.search_service_name
  resource_group_name          = var.resource_group_name
  location                     = var.location
  sku                          = var.sku
  replica_count               = var.replica_count
  partition_count             = var.partition_count
  public_network_access_enabled = var.public_network_access_enabled

  # Identity configuration for managed identity
  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# Search Index (basic structure - can be customized)
resource "azurerm_search_index" "kb_articles" {
  name               = var.index_name
  search_service_id  = azurerm_search_service.main.id

  fields {
    name                     = "id"
    type                     = "Edm.String"
    key                      = true
    searchable              = false
    filterable              = true
    retrievable             = true
    sortable                = false
    facetable               = false
    analyzer_name           = null
  }

  fields {
    name                     = "title"
    type                     = "Edm.String"
    key                      = false
    searchable              = true
    filterable              = true
    retrievable             = true
    sortable                = true
    facetable               = false
    analyzer_name           = "standard.lucene"
  }

  fields {
    name                     = "content"
    type                     = "Edm.String"
    key                      = false
    searchable              = true
    filterable              = false
    retrievable             = true
    sortable                = false
    facetable               = false
    analyzer_name           = "standard.lucene"
  }

  fields {
    name                     = "chunk_id"
    type                     = "Edm.String"
    key                      = false
    searchable              = false
    filterable              = true
    retrievable             = true
    sortable                = false
    facetable               = false
  }

  fields {
    name                     = "article_id"
    type                     = "Edm.String"
    key                      = false
    searchable              = false
    filterable              = true
    retrievable             = true
    sortable                = false
    facetable               = true
  }

  fields {
    name                     = "security"
    type                     = "Edm.String"
    key                      = false
    searchable              = false
    filterable              = true
    retrievable             = true
    sortable                = false
    facetable               = true
  }

  fields {
    name                     = "source_url"
    type                     = "Edm.String"
    key                      = false
    searchable              = false
    filterable              = false
    retrievable             = true
    sortable                = false
    facetable               = false
  }

  fields {
    name                     = "created_date"
    type                     = "Edm.DateTimeOffset"
    key                      = false
    searchable              = false
    filterable              = true
    retrievable             = true
    sortable                = true
    facetable               = false
  }

  fields {
    name                     = "embedding"
    type                     = "Collection(Edm.Single)"
    key                      = false
    searchable              = true
    filterable              = false
    retrievable             = false
    sortable                = false
    facetable               = false
    vector_search_dimensions = var.embedding_dimensions
  }

  # Vector search configuration
  vector_search {
    algorithms {
      name                     = "hnsw-algorithm"
      kind                     = "hnsw"
    }

    profiles {
      name                     = "vector-profile"
      algorithm_configuration_name = "hnsw-algorithm"
    }
  }

  # Semantic search configuration
  semantic_search {
    default_configuration_name = "semantic-config"

    configurations {
      name = "semantic-config"

      prioritized_fields {
        title_field {
          field_name = "title"
        }

        content_fields {
          field_name = "content"
        }
      }
    }
  }
}
