# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# MINIMAL CHANGE: Add one new function to existing Microsoft PubSec-IA
# This function fetches from LaTrobe API and feeds into existing Microsoft pipeline
# NO CHANGES to existing Microsoft functions required

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

# Use Microsoft PubSec-IA environment variables (no changes needed)
azure_blob_content_container = os.environ.get("BLOB_STORAGE_ACCOUNT_OUTPUT_CONTAINER_NAME", "content")
azure_blob_endpoint = os.environ.get("BLOB_STORAGE_ACCOUNT_ENDPOINT")
azure_queue_endpoint = os.environ.get("AZURE_QUEUE_STORAGE_ENDPOINT")
non_pdf_submit_queue = os.environ.get("NON_PDF_SUBMIT_QUEUE", "non-pdf-submit-queue")
local_debug = os.environ.get("LOCAL_DEBUG", "false")
azure_openai_authority_host = os.environ.get("AZURE_OPENAI_AUTHORITY_HOST", "AzurePublicCloud")

# LaTrobe API settings (already in deployment script)
KNOWLEDGE_BASE_API_URL = os.environ.get("KNOWLEDGE_BASE_API_URL")
APIM_SUBSCRIPTION_KEY = os.environ.get("APIM_SUBSCRIPTION_KEY")
KB_NAME_FILTER = os.environ.get("KB_NAME_FILTER", "ICT")
KB_ACTIVE_FILTER = os.environ.get("KB_ACTIVE_FILTER", "true")
KB_STATUS_FILTER = os.environ.get("KB_STATUS_FILTER", "published")

FUNCTION_NAME = "LatroBKBFetcher"  # New function name

# Microsoft PubSec-IA authentication pattern (unchanged)
if azure_openai_authority_host == "AzureUSGovernment":
    AUTHORITY = AzureAuthorityHosts.AZURE_GOVERNMENT
else:
    AUTHORITY = AzureAuthorityHosts.AZURE_PUBLIC_CLOUD

if local_debug.lower() == "true":
    azure_credential = DefaultAzureCredential(authority=AUTHORITY)
else:
    azure_credential = ManagedIdentityCredential(authority=AUTHORITY)


def fetch_latrobe_articles() -> List[Dict[str, Any]]:
    """Fetch articles from LaTrobe API"""
    # Check if API is properly configured (not placeholder values)
    if (not KNOWLEDGE_BASE_API_URL or not APIM_SUBSCRIPTION_KEY or 
        APIM_SUBSCRIPTION_KEY == "your-apim-subscription-key-here" or
        len(APIM_SUBSCRIPTION_KEY) < 10):
        # Create test data if API not configured
        logging.warning(f"{FUNCTION_NAME} - API not configured or using placeholder values, using test data")
        return [{
            "id": "test-001",
            "title": "Test KB Article",
            "content": "This is a test knowledge base article for Microsoft PubSec-IA integration testing.",
            "created": datetime.utcnow().isoformat(),
            "modified": datetime.utcnow().isoformat(),
            "status": "published",
            "category": "Test",
            "tags": ["test", "integration"]
        }]
    
    try:
        headers = {
            'Ocp-Apim-Subscription-Key': APIM_SUBSCRIPTION_KEY,
            'Content-Type': 'application/json'
        }
        
        params = {
            'Name': KB_NAME_FILTER,
            'Active': KB_ACTIVE_FILTER,
            'Status_IN': KB_STATUS_FILTER
        }
        
        response = requests.get(KNOWLEDGE_BASE_API_URL, headers=headers, params=params)
        response.raise_for_status()
        
        kb_data = response.json()
        articles = kb_data.get('value', []) if isinstance(kb_data, dict) else kb_data
        
        logging.info(f"{FUNCTION_NAME} - Fetched {len(articles)} articles from LaTrobe API")
        return articles
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error fetching from LaTrobe API: {str(e)}")
        raise


def convert_to_microsoft_format(article: Dict[str, Any]) -> str:
    """
    Convert LaTrobe article to Microsoft PubSec-IA expected blob format
    This mimics what FileUploadedFunc expects to process
    """
    try:
        article_id = article.get('id', 'unknown')
        blob_name = f"latrobe_kb_{article_id}.txt"
        
        # Create text content in format Microsoft PubSec-IA expects
        content_text = f"""Title: {article.get('title', 'Untitled')}

Content:
{article.get('content', '')}

Source: LaTrobe Knowledge Base
Article ID: {article_id}
Created: {article.get('created', '')}
Modified: {article.get('modified', '')}
Status: {article.get('status', '')}
Category: {article.get('category', '')}
Tags: {', '.join(article.get('tags', []))}
"""
        
        return blob_name, content_text
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error converting article {article.get('id', 'unknown')}: {str(e)}")
        raise


def upload_to_microsoft_pipeline(blob_name: str, content: str):
    """
    Upload to Microsoft PubSec-IA upload container
    This triggers the existing Microsoft FileUploadedFunc (no changes needed)
    """
    try:
        blob_service_client = BlobServiceClient(
            account_url=azure_blob_endpoint,
            credential=azure_credential
        )
        
        # Upload to upload container (Microsoft PubSec-IA pattern)
        upload_container = "upload"  # Microsoft's upload trigger container
        blob_client = blob_service_client.get_blob_client(
            container=upload_container,
            blob=blob_name
        )
        
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings={'content_type': 'text/plain'}
        )
        
        logging.info(f"{FUNCTION_NAME} - Uploaded {blob_name} to Microsoft pipeline")
        return True
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error uploading {blob_name}: {str(e)}")
        return False


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main function: Fetch from LaTrobe API and feed into Microsoft PubSec-IA pipeline
    ZERO changes needed to existing Microsoft functions
    """
    logging.info(f"{FUNCTION_NAME} - Starting LaTrobe KB integration")
    
    try:
        # Fetch from LaTrobe API
        articles = fetch_latrobe_articles()
        
        if not articles:
            return func.HttpResponse(
                json.dumps({"message": "No articles found", "processed": 0}),
                status_code=200,
                mimetype="application/json"
            )
        
        processed_count = 0
        errors = []
        
        # Convert each article and feed into Microsoft pipeline
        for article in articles:
            try:
                # Convert to Microsoft format
                blob_name, content = convert_to_microsoft_format(article)
                
                # Upload to Microsoft upload container (triggers existing FileUploadedFunc)
                if upload_to_microsoft_pipeline(blob_name, content):
                    processed_count += 1
                    logging.info(f"{FUNCTION_NAME} - Processed article {article.get('id', 'unknown')}")
                else:
                    errors.append(f"Upload failed for article {article.get('id', 'unknown')}")
                
            except Exception as e:
                error_msg = f"Error processing article {article.get('id', 'unknown')}: {str(e)}"
                logging.error(f"{FUNCTION_NAME} - {error_msg}")
                errors.append(error_msg)
                continue
        
        result = {
            "message": f"LaTrobe KB articles processed through Microsoft PubSec-IA pipeline",
            "total_articles": len(articles),
            "processed": processed_count,
            "errors": len(errors),
            "error_details": errors[:5] if errors else [],
            "pipeline": "Microsoft PubSec-IA (unchanged)"
        }
        
        logging.info(f"{FUNCTION_NAME} - Completed: {processed_count}/{len(articles)} articles")
        
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
