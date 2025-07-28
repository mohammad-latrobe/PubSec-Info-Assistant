#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# Deploy search index for LaTrobe University Information Assistant

import json
import os
import requests
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient

# Environment variables
SEARCH_SERVICE_ENDPOINT = os.environ.get("AZURE_SEARCH_SERVICE_ENDPOINT", "https://ltu-troby-search-dev-3964.search.windows.net")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "kb-articles-index")

def load_index_definition():
    """Create a simplified search index definition for LaTrobe KB articles"""
    
    # Create a simple index definition that works
    index_def = {
        "name": INDEX_NAME,
        "fields": [
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "retrievable": True,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "title",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": True,
                "filterable": True,
                "sortable": True,
                "facetable": False,
                "analyzer": "standard.lucene"
            },
            {
                "name": "content",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
                "analyzer": "standard.lucene"
            },
            {
                "name": "url",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "category",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": True,
                "filterable": True,
                "sortable": True,
                "facetable": True
            },
            {
                "name": "status",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": True
            },
            {
                "name": "source",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": True
            },
            {
                "name": "created_date",
                "type": "Edm.DateTimeOffset",
                "retrievable": True,
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False
            },
            {
                "name": "metadata",
                "type": "Edm.String",
                "retrievable": True,
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False
            }
        ]
    }
    
    return index_def

def deploy_index():
    """Deploy the search index to Azure Search"""
    try:
        # Get Azure credentials
        credential = DefaultAzureCredential()
        
        # Create search index client
        search_index_client = SearchIndexClient(
            endpoint=SEARCH_SERVICE_ENDPOINT,
            credential=credential
        )
        
        # Load index definition
        index_definition = load_index_definition()
        
        print(f"Deploying search index '{INDEX_NAME}' to {SEARCH_SERVICE_ENDPOINT}")
        
        # Create or update the index
        result = search_index_client.create_or_update_index(index_definition)
        
        print(f"✅ Successfully deployed search index: {result.name}")
        print(f"   - Fields: {len(result.fields)}")
        print(f"   - Vector search profiles: {len(result.vector_search.profiles) if result.vector_search else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying search index: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 LaTrobe University - Search Index Deployment")
    print("=" * 60)
    
    success = deploy_index()
    
    if success:
        print("✅ Search index deployment completed successfully!")
    else:
        print("❌ Search index deployment failed!")
        exit(1)
