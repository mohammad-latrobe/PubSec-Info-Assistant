# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# 
# Adapted from Microsoft PubSec-IA to integrate with LaTrobe KB API
# This function replaces FileUploadedFunc to fetch KB articles from LaTrobe API
# and processes them through the same Microsoft PubSec-IA pipeline

import logging
import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential, AzureAuthorityHosts

# Environment configuration (maintaining Microsoft PubSec-IA naming)
azure_blob_content_container = os.environ.get("BLOB_STORAGE_ACCOUNT_OUTPUT_CONTAINER_NAME", "content")
azure_blob_endpoint = os.environ.get("BLOB_STORAGE_ACCOUNT_ENDPOINT")
azure_queue_endpoint = os.environ.get("AZURE_QUEUE_STORAGE_ENDPOINT")
non_pdf_submit_queue = os.environ.get("NON_PDF_SUBMIT_QUEUE", "non-pdf-submit-queue")
local_debug = os.environ.get("LOCAL_DEBUG", "false")
azure_openai_authority_host = os.environ.get("AZURE_OPENAI_AUTHORITY_HOST", "AzurePublicCloud")

# LaTrobe API Configuration
KNOWLEDGE_BASE_API_URL = os.environ.get("KNOWLEDGE_BASE_API_URL")
APIM_SUBSCRIPTION_KEY = os.environ.get("APIM_SUBSCRIPTION_KEY")
KB_NAME_FILTER = os.environ.get("KB_NAME_FILTER", "ICT")
KB_ACTIVE_FILTER = os.environ.get("KB_ACTIVE_FILTER", "true")
KB_STATUS_FILTER = os.environ.get("KB_STATUS_FILTER", "published")

FUNCTION_NAME = "FileUploadedFunc"  # Maintaining Microsoft naming

if azure_openai_authority_host == "AzureUSGovernment":
    AUTHORITY = AzureAuthorityHosts.AZURE_GOVERNMENT
else:
    AUTHORITY = AzureAuthorityHosts.AZURE_PUBLIC_CLOUD

# Authentication (Microsoft PubSec-IA pattern)
if local_debug.lower() == "true":
    azure_credential = DefaultAzureCredential(authority=AUTHORITY)
else:
    azure_credential = ManagedIdentityCredential(authority=AUTHORITY)


def fetch_kb_articles() -> List[Dict[str, Any]]:
    """
    Fetch KB articles from LaTrobe API using the same filters
    Returns list of KB articles
    """
    try:
        headers = {
            'Ocp-Apim-Subscription-Key': APIM_SUBSCRIPTION_KEY,
            'Content-Type': 'application/json'
        }
        
        params = {
            'name': KB_NAME_FILTER,
            'active': KB_ACTIVE_FILTER,
            'status': KB_STATUS_FILTER
        }
        
        response = requests.get(KNOWLEDGE_BASE_API_URL, headers=headers, params=params)
        response.raise_for_status()
        
        kb_data = response.json()
        articles = kb_data.get('value', []) if isinstance(kb_data, dict) else kb_data
        
        logging.info(f"{FUNCTION_NAME} - Fetched {len(articles)} KB articles from LaTrobe API")
        return articles
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error fetching KB articles: {str(e)}")
        raise


def create_document_blob(article: Dict[str, Any], blob_service_client: BlobServiceClient) -> str:
    """
    Create a blob document from KB article data
    Following Microsoft PubSec-IA document structure
    """
    try:
        # Create standardized document name (following Microsoft pattern)
        article_id = article.get('id', 'unknown')
        document_name = f"kb_article_{article_id}.json"
        
        # Create document map (Microsoft PubSec-IA standard structure)
        document_map = {
            'file_name': document_name,
            'file_uri': f"{azure_blob_endpoint}/{azure_blob_content_container}/{document_name}",
            'content': article.get('content', ''),
            'title': article.get('title', ''),
            'structure': [],
            'content_type': [],
            'table_index': [],
            'metadata': {
                'source': 'latrobe_kb_api',
                'article_id': article_id,
                'created_date': article.get('created', ''),
                'modified_date': article.get('modified', ''),
                'status': article.get('status', ''),
                'category': article.get('category', ''),
                'tags': article.get('tags', [])
            }
        }
        
        # Upload to blob storage
        blob_client = blob_service_client.get_blob_client(
            container=azure_blob_content_container,
            blob=document_name
        )
        
        blob_client.upload_blob(
            json.dumps(document_map, indent=2),
            overwrite=True,
            content_settings={'content_type': 'application/json'}
        )
        
        logging.info(f"{FUNCTION_NAME} - Created document blob: {document_name}")
        return document_name
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error creating document blob: {str(e)}")
        raise


def queue_for_processing(document_name: str, article: Dict[str, Any]):
    """
    Queue document for processing through Microsoft PubSec-IA pipeline
    """
    try:
        # Create message following Microsoft PubSec-IA format
        message_json = {
            "blob_name": document_name,
            "blob_uri": f"{azure_blob_endpoint}/{azure_blob_content_container}/{document_name}",
            "submit_queued_count": 1,
            "pdf_submit_queued_count": 0,
            "file_type": "json",  # Treating as structured text
            "file_class": "text",
            "file_extension": ".json",
            "source": "latrobe_kb_api",
            "article_id": article.get('id', ''),
            "processing_datetime": datetime.utcnow().isoformat()
        }
        
        # Send to non-PDF queue (following Microsoft pattern for text processing)
        queue_client = QueueClient(
            account_url=azure_queue_endpoint,
            queue_name=non_pdf_submit_queue,
            credential=azure_credential,
            message_encode_policy=TextBase64EncodePolicy()
        )
        
        message_string = json.dumps(message_json)
        queue_client.send_message(message_string)
        
        logging.info(f"{FUNCTION_NAME} - Queued {document_name} for processing")
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error queuing document: {str(e)}")
        raise


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main function - HTTP trigger to fetch and process KB articles
    Replaces the blob trigger from Microsoft PubSec-IA FileUploadedFunc
    """
    logging.info(f"{FUNCTION_NAME} - KB Article processing started")
    
    try:
        # Initialize blob service client
        blob_service_client = BlobServiceClient(
            account_url=azure_blob_endpoint,
            credential=azure_credential
        )
        
        # Fetch KB articles from LaTrobe API
        articles = fetch_kb_articles()
        
        if not articles:
            logging.warning(f"{FUNCTION_NAME} - No KB articles found")
            return func.HttpResponse(
                json.dumps({"message": "No KB articles found", "processed": 0}),
                status_code=200,
                mimetype="application/json"
            )
        
        processed_count = 0
        errors = []
        
        # Process each article through Microsoft PubSec-IA pipeline
        for article in articles:
            try:
                # Create document blob (following Microsoft pattern)
                document_name = create_document_blob(article, blob_service_client)
                
                # Queue for processing (following Microsoft pipeline)
                queue_for_processing(document_name, article)
                
                processed_count += 1
                
            except Exception as e:
                error_msg = f"Error processing article {article.get('id', 'unknown')}: {str(e)}"
                logging.error(f"{FUNCTION_NAME} - {error_msg}")
                errors.append(error_msg)
                continue
        
        # Return status (following Microsoft pattern)
        result = {
            "message": f"KB articles processing initiated",
            "total_articles": len(articles),
            "processed": processed_count,
            "errors": len(errors),
            "error_details": errors[:5] if errors else []  # Limit error details
        }
        
        logging.info(f"{FUNCTION_NAME} - Processed {processed_count}/{len(articles)} articles")
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200 if processed_count > 0 else 500,
            mimetype="application/json"
        )
        
    except Exception as e:
        error_msg = f"Fatal error in {FUNCTION_NAME}: {str(e)}"
        logging.error(error_msg)
        
        return func.HttpResponse(
            json.dumps({"error": error_msg}),
            status_code=500,
            mimetype="application/json"
        )
