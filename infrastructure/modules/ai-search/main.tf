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

# Search Index Configuration
# Note: Azure Search indexes are not directly supported by the AzureRM provider
# The index will need to be created using the Azure REST API or Azure CLI after deployment
# Index name: var.index_name (from variables)
# Search Service: azurerm_search_service.main.name
#
# The index should include fields for:
# - id (key field)
# - title (searchable text)
# - content (searchable text) 
# - chunk_id (filterable)
# - article_id (filterable, facetable)
# - security (filterable, facetable)
# - source_url (retrievable)
# - created_date (filterable, sortable)
# - embedding (vector field with dimensions from var.embedding_dimensions)
#
# Vector search and semantic search configurations should be included

# Create a local file with the index definition for later use
resource "local_file" "search_index_definition" {
  content = jsonencode({
    name = var.index_name
    fields = [
      {
        name = "id"
        type = "Edm.String"
        key = true
        searchable = false
        filterable = true
        retrievable = true
        sortable = false
        facetable = false
      },
      {
        name = "title"
        type = "Edm.String"
        searchable = true
        filterable = true
        retrievable = true
        sortable = true
        facetable = false
        analyzer = "standard.lucene"
      },
      {
        name = "content"
        type = "Edm.String"
        searchable = true
        filterable = false
        retrievable = true
        sortable = false
        facetable = false
        analyzer = "standard.lucene"
      },
      {
        name = "chunk_id"
        type = "Edm.String"
        searchable = false
        filterable = true
        retrievable = true
        sortable = false
        facetable = false
      },
      {
        name = "article_id"
        type = "Edm.String"
        searchable = false
        filterable = true
        retrievable = true
        sortable = false
        facetable = true
      },
      {
        name = "security"
        type = "Edm.String"
        searchable = false
        filterable = true
        retrievable = true
        sortable = false
        facetable = true
      },
      {
        name = "source_url"
        type = "Edm.String"
        searchable = false
        filterable = false
        retrievable = true
        sortable = false
        facetable = false
      },
      {
        name = "created_date"
        type = "Edm.DateTimeOffset"
        searchable = false
        filterable = true
        retrievable = true
        sortable = true
        facetable = false
      },
      {
        name = "embedding"
        type = "Collection(Edm.Single)"
        searchable = true
        filterable = false
        retrievable = false
        sortable = false
        facetable = false
        dimensions = var.embedding_dimensions
      }
    ]
    vectorSearch = {
      algorithms = [
        {
          name = "hnsw-algorithm"
          kind = "hnsw"
        }
      ]
      profiles = [
        {
          name = "vector-profile"
          algorithmConfigurationName = "hnsw-algorithm"
        }
      ]
    }
    semantic = {
      defaultConfiguration = "semantic-config"
      configurations = [
        {
          name = "semantic-config"
          prioritizedFields = {
            titleField = { fieldName = "title" }
            contentFields = [{ fieldName = "content" }]
          }
        }
      ]
    }
  })
  filename = "${path.module}/search_index_${var.index_name}.json"
}
