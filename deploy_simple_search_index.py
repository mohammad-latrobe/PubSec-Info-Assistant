#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# Deploy simple search index for LaTrobe University Information Assistant

import json
import os
import requests
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)

# Environment variables
SEARCH_SERVICE_ENDPOINT = os.environ.get("AZURE_SEARCH_SERVICE_ENDPOINT", "https://ltu-troby-search-dev-3964.search.windows.net")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "kb-articles-index")

def create_simple_index():
    """Create a simple search index for KB articles"""
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="file_name", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="offset", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="created", type=SearchFieldDataType.DateTimeOffset, filterable=True),
        SimpleField(name="modified", type=SearchFieldDataType.DateTimeOffset, filterable=True),
        SimpleField(name="status", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="tags", type=SearchFieldDataType.String)
    ]
    
    return SearchIndex(name=INDEX_NAME, fields=fields)

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
        
        # Create simple index definition
        index_definition = create_simple_index()
        
        print(f"Deploying search index '{INDEX_NAME}' to {SEARCH_SERVICE_ENDPOINT}")
        
        # Create or update the index
        result = search_index_client.create_or_update_index(index_definition)
        
        print(f"✅ Successfully deployed search index: {result.name}")
        print(f"   - Fields: {len(result.fields)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying search index: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 LaTrobe University - Simple Search Index Deployment")
    print("=" * 60)
    
    success = deploy_index()
    
    if success:
        print("✅ Search index deployment completed successfully!")
    else:
        print("❌ Search index deployment failed!")
        exit(1)
