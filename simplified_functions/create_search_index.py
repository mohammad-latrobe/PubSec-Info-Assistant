# Azure AI Search Index Schema for Knowledge Base Articles
# This creates an index with security filtering capability

import json
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    ComplexField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticSearch,
    SemanticField,
    SemanticPrioritizedFields
)
from azure.identity import DefaultAzureCredential
import os

# Configuration
SEARCH_SERVICE_ENDPOINT = os.environ.get("AZURE_SEARCH_SERVICE_ENDPOINT")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "kb-articles-index")
EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_VECTOR_SIZE", "1536"))  # text-embedding-ada-002 default

def create_search_index():
    """Create Azure AI Search index with security filtering for KB articles"""
    
    # Initialize search client
    credential = DefaultAzureCredential()
    search_index_client = SearchIndexClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        credential=credential
    )
    
    # Define the search index schema
    fields = [
        # Document identification
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="file_name", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="file_uri", type=SearchFieldDataType.String),
        SimpleField(name="file_class", type=SearchFieldDataType.String, filterable=True, facetable=True),
        
        # Content fields
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SearchableField(name="section", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SearchableField(name="subtitle", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        
        # Vector field for semantic search
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSION,
            vector_search_profile_name="default-vector-profile"
        ),
        
        # Security and access control
        SimpleField(name="security_groups", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                   filterable=True, facetable=True),
        SimpleField(name="access_level", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="department", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="classification", type=SearchFieldDataType.String, filterable=True, facetable=True),
        
        # Metadata fields
        SimpleField(name="processed_datetime", type=SearchFieldDataType.DateTimeOffset, 
                   filterable=True, sortable=True),
        SimpleField(name="chunk_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SimpleField(name="token_count", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SimpleField(name="pages", type=SearchFieldDataType.Collection(SearchFieldDataType.Int32), 
                   filterable=True, facetable=True),
        
        # Additional metadata as complex field
        ComplexField(
            name="metadata",
            fields=[
                SimpleField(name="author", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SimpleField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), 
                           filterable=True, facetable=True),
                SimpleField(name="version", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="last_updated", type=SearchFieldDataType.DateTimeOffset, 
                           filterable=True, sortable=True)
            ]
        )
    ]
    
    # Configure vector search
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="default-hnsw-config",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="default-vector-profile",
                algorithm_configuration_name="default-hnsw-config"
            )
        ]
    )
    
    # Configure semantic search for better relevance
    semantic_config = SemanticConfiguration(
        name="kb-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[
                SemanticField(field_name="content"),
                SemanticField(field_name="section")
            ],
            keywords_fields=[
                SemanticField(field_name="metadata/category"),
                SemanticField(field_name="metadata/tags")
            ]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    # Create the search index
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    try:
        # Create or update the index
        result = search_index_client.create_or_update_index(index)
        print(f"Search index '{INDEX_NAME}' created successfully!")
        return result
    except Exception as e:
        print(f"Error creating search index: {str(e)}")
        raise

def create_sample_security_mapping():
    """Create sample security mapping for demonstration"""
    security_mapping = {
        "public": {
            "access_level": "public",
            "security_groups": ["everyone"],
            "department": "general",
            "classification": "unclassified"
        },
        "internal": {
            "access_level": "internal", 
            "security_groups": ["employees", "contractors"],
            "department": "all_departments",
            "classification": "internal"
        },
        "confidential": {
            "access_level": "confidential",
            "security_groups": ["management", "hr"],
            "department": "restricted",
            "classification": "confidential"
        },
        "hr_only": {
            "access_level": "restricted",
            "security_groups": ["hr_team"],
            "department": "human_resources", 
            "classification": "restricted"
        }
    }
    
    return security_mapping

if __name__ == "__main__":
    # Create the search index
    try:
        index_result = create_search_index()
        print("Index creation completed successfully!")
        
        # Display sample security mapping
        security_mapping = create_sample_security_mapping()
        print("\nSample Security Mapping:")
        print(json.dumps(security_mapping, indent=2))
        
    except Exception as e:
        print(f"Failed to create index: {str(e)}")
