# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import logging
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import azure.functions as func
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import requests

# Configuration from environment variables
SEARCH_SERVICE_ENDPOINT = os.environ.get("AZURE_SEARCH_SERVICE_ENDPOINT")
SEARCH_INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "kb-articles-index")
BLOB_STORAGE_ACCOUNT_ENDPOINT = os.environ.get("BLOB_STORAGE_ACCOUNT_ENDPOINT")
BLOB_CONTENT_CONTAINER_NAME = os.environ.get("BLOB_CONTENT_CONTAINER_NAME", "content")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002")
LOCAL_DEBUG = os.environ.get("LOCAL_DEBUG", "false").lower() == "true"

# Authentication
if LOCAL_DEBUG:
    azure_credential = DefaultAzureCredential()
else:
    azure_credential = ManagedIdentityCredential()

def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding using Azure OpenAI"""
    try:
        # Get access token for Azure OpenAI
        from azure.identity import get_bearer_token_provider
        token_provider = get_bearer_token_provider(azure_credential, "https://cognitiveservices.azure.com/.default")
        access_token = token_provider()
        
        # Prepare the request
        url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_EMBEDDING_DEPLOYMENT}/embeddings?api-version=2023-05-15"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": text,
            "model": AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        if "data" in result and len(result["data"]) > 0:
            return result["data"][0]["embedding"]
        else:
            logging.error("No embedding data in response")
            return None
            
    except Exception as e:
        logging.error(f"Failed to generate embedding: {str(e)}")
        return None

def create_document_id(file_name: str, chunk_number: int) -> str:
    """Create a unique document ID for the search index"""
    id_string = f"{file_name}-chunk-{chunk_number}"
    return hashlib.md5(id_string.encode()).hexdigest()

def transform_chunk_for_search(chunk_data: Dict[str, Any], security_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Transform chunk JSON to search document format"""
    
    # Default security configuration if none provided
    if security_config is None:
        security_config = {
            "access_level": "public",
            "security_groups": ["everyone"],
            "department": "general",
            "classification": "unclassified"
        }
    
    # Generate embedding for content
    content = chunk_data.get("content", "")
    content_vector = generate_embedding(content)
    
    if content_vector is None:
        logging.warning(f"Failed to generate embedding for chunk, skipping indexing")
        return None
    
    # Create search document
    search_doc = {
        "id": create_document_id(chunk_data.get("file_name", ""), chunk_data.get("chunk_number", 0)),
        "file_name": chunk_data.get("file_name", ""),
        "file_uri": chunk_data.get("file_uri", ""),
        "file_class": chunk_data.get("file_class", "knowledge_base"),
        "content": content,
        "title": chunk_data.get("title", ""),
        "section": chunk_data.get("section", ""),
        "subtitle": chunk_data.get("subtitle", ""),
        "content_vector": content_vector,
        "processed_datetime": chunk_data.get("processed_datetime"),
        "chunk_number": chunk_data.get("chunk_number", 0),
        "token_count": chunk_data.get("token_count", 0),
        "pages": chunk_data.get("pages", [1]),
        
        # Security fields
        "security_groups": security_config.get("security_groups", ["everyone"]),
        "access_level": security_config.get("access_level", "public"),
        "department": security_config.get("department", "general"),
        "classification": security_config.get("classification", "unclassified"),
        
        # Metadata
        "metadata": chunk_data.get("metadata", {})
    }
    
    return search_doc

def index_chunk_to_search(search_client: SearchClient, chunk_data: Dict[str, Any], security_config: Dict[str, Any] = None) -> bool:
    """Index a single chunk to Azure AI Search"""
    try:
        # Transform chunk to search document
        search_doc = transform_chunk_for_search(chunk_data, security_config)
        
        if search_doc is None:
            return False
        
        # Upload to search index
        result = search_client.upload_documents([search_doc])
        
        # Check if successful
        if result and len(result) > 0 and result[0].succeeded:
            logging.info(f"Successfully indexed chunk: {search_doc['id']}")
            return True
        else:
            logging.error(f"Failed to index chunk: {search_doc['id']}")
            return False
            
    except Exception as e:
        logging.error(f"Error indexing chunk: {str(e)}")
        return False

def process_blob_chunks(blob_service_client: BlobServiceClient, search_client: SearchClient, blob_prefix: str = "kb_articles/") -> Dict[str, Any]:
    """Process all chunk JSON files from blob storage and index them"""
    
    indexed_count = 0
    failed_count = 0
    processed_files = []
    
    try:
        # Get container client
        container_client = blob_service_client.get_container_client(BLOB_CONTENT_CONTAINER_NAME)
        
        # List all JSON blobs with the prefix
        blob_list = container_client.list_blobs(name_starts_with=blob_prefix)
        
        for blob in blob_list:
            if blob.name.endswith('.json'):
                try:
                    # Download and parse JSON
                    blob_client = container_client.get_blob_client(blob.name)
                    blob_data = blob_client.download_blob().readall()
                    chunk_data = json.loads(blob_data)
                    
                    # Determine security configuration based on metadata or filename
                    security_config = determine_security_config(chunk_data)
                    
                    # Index the chunk
                    if index_chunk_to_search(search_client, chunk_data, security_config):
                        indexed_count += 1
                        processed_files.append({
                            "blob_name": blob.name,
                            "status": "indexed",
                            "file_name": chunk_data.get("file_name", ""),
                            "chunk_number": chunk_data.get("chunk_number", 0)
                        })
                    else:
                        failed_count += 1
                        processed_files.append({
                            "blob_name": blob.name,
                            "status": "failed",
                            "file_name": chunk_data.get("file_name", ""),
                            "chunk_number": chunk_data.get("chunk_number", 0)
                        })
                        
                except Exception as e:
                    logging.error(f"Error processing blob {blob.name}: {str(e)}")
                    failed_count += 1
                    processed_files.append({
                        "blob_name": blob.name,
                        "status": "error",
                        "error": str(e)
                    })
        
        return {
            "indexed_count": indexed_count,
            "failed_count": failed_count,
            "total_processed": indexed_count + failed_count,
            "processed_files": processed_files
        }
        
    except Exception as e:
        logging.error(f"Error processing blob chunks: {str(e)}")
        raise

def determine_security_config(chunk_data: Dict[str, Any]) -> Dict[str, Any]:
    """Determine security configuration based on chunk metadata"""
    
    metadata = chunk_data.get("metadata", {})
    file_name = chunk_data.get("file_name", "").lower()
    
    # Default to public access
    security_config = {
        "access_level": "public",
        "security_groups": ["everyone"],
        "department": "general",
        "classification": "unclassified"
    }
    
    # Override based on metadata or filename patterns
    if "security" in metadata:
        security_config.update(metadata["security"])
    elif "confidential" in file_name or "restricted" in file_name:
        security_config = {
            "access_level": "confidential",
            "security_groups": ["management", "authorized_users"],
            "department": "restricted",
            "classification": "confidential"
        }
    elif "internal" in file_name:
        security_config = {
            "access_level": "internal",
            "security_groups": ["employees", "contractors"],
            "department": "all_departments",
            "classification": "internal"
        }
    elif "hr" in file_name:
        security_config = {
            "access_level": "restricted",
            "security_groups": ["hr_team"],
            "department": "human_resources",
            "classification": "restricted"
        }
    
    return security_config

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to index KB article chunks from blob storage to Azure AI Search.
    
    Optional request parameters:
    - blob_prefix: Prefix to filter blobs (default: "kb_articles/")
    - security_override: Override security configuration for all chunks
    """
    
    logging.info('Starting KB articles indexing process')
    
    try:
        # Parse request parameters
        blob_prefix = req.params.get('blob_prefix', 'kb_articles/')
        security_override = None
        
        try:
            req_body = req.get_json()
            if req_body and 'security_override' in req_body:
                security_override = req_body['security_override']
        except:
            pass  # No JSON body is OK
        
        # Initialize clients
        blob_service_client = BlobServiceClient(
            account_url=BLOB_STORAGE_ACCOUNT_ENDPOINT,
            credential=azure_credential
        )
        
        search_client = SearchClient(
            endpoint=SEARCH_SERVICE_ENDPOINT,
            index_name=SEARCH_INDEX_NAME,
            credential=azure_credential
        )
        
        # Process and index chunks
        logging.info(f"Processing chunks with prefix: {blob_prefix}")
        result = process_blob_chunks(blob_service_client, search_client, blob_prefix)
        
        # Add metadata to result
        result.update({
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "blob_prefix": blob_prefix,
            "search_index": SEARCH_INDEX_NAME
        })
        
        logging.info(f"Indexing completed: {result['indexed_count']} successful, {result['failed_count']} failed")
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Function execution failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }),
            status_code=500,
            mimetype="application/json"
        )
