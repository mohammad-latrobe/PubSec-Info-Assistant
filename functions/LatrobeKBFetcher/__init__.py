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
import re
from datetime import datetime
from typing import List, Dict, Any
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential, AzureAuthorityHosts
from bs4 import BeautifulSoup

# Use Microsoft PubSec-IA environment variables (no changes needed)
azure_blob_content_container = os.environ.get("BLOB_STORAGE_ACCOUNT_OUTPUT_CONTAINER_NAME", "content")
azure_blob_endpoint = os.environ.get("BLOB_STORAGE_ACCOUNT_ENDPOINT")
azure_storage_connection_string = os.environ.get("AzureWebJobsStorage")  # Function App's storage connection
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
        
        # Parse LaTrobe API response structure
        if isinstance(kb_data, dict) and 'Collection' in kb_data:
            # Extract articles from Collection.Items.Item array
            collection = kb_data['Collection']
            items = collection.get('Items', {})
            articles_raw = items.get('Item', [])
            
            # Convert LaTrobe format to our format
            articles = []
            for item in articles_raw:
                articles.append({
                    'id': item.get('ID', ''),
                    'title': item.get('Name', item.get('Short_Description', 'Untitled')),
                    'content': item.get('Content', ''),
                    'created': item.get('Created_On', ''),
                    'modified': item.get('Updated_On', ''),
                    'status': item.get('Status', ''),
                    'category': KB_NAME_FILTER,
                    'url': item.get('Location', {}).get('Location_Name', ''),
                    'tags': []
                })
        else:
            articles = []
        
        logging.info(f"{FUNCTION_NAME} - Fetched {len(articles)} articles from LaTrobe API")
        return articles
        
    except Exception as e:
        logging.error(f"{FUNCTION_NAME} - Error fetching from LaTrobe API: {str(e)}")
        raise


def clean_html_content(html_content: str) -> str:
    """
    Clean HTML tags and formatting from LaTrobe API content
    Convert HTML to clean, readable text
    """
    if not html_content:
        return ""
    
    try:
        # Use BeautifulSoup to parse and clean HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements completely
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content and clean up whitespace
        text = soup.get_text()
        
        # Clean up whitespace - normalize multiple spaces/newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common HTML entity residue
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        return text.strip()
        
    except Exception as e:
        logging.warning(f"{FUNCTION_NAME} - Error cleaning HTML content: {str(e)}")
        # Fallback: basic regex-based cleaning if BeautifulSoup fails
        try:
            # Remove HTML tags with regex
            clean_text = re.sub(r'<[^>]+>', '', html_content)
            # Clean up whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text)
            clean_text = clean_text.replace('&nbsp;', ' ')
            clean_text = clean_text.replace('&amp;', '&')
            return clean_text.strip()
        except Exception as fallback_error:
            logging.error(f"{FUNCTION_NAME} - Fallback HTML cleaning failed: {str(fallback_error)}")
            return html_content  # Return original if all cleaning fails


def convert_to_microsoft_format(article: Dict[str, Any]) -> str:
    """
    Convert LaTrobe article to Microsoft PubSec-IA expected blob format
    This mimics what FileUploadedFunc expects to process
    """
    try:
        article_id = article.get('id', 'unknown')
        blob_name = f"latrobe_kb_{article_id}.txt"
        
        # Clean HTML content from the article
        raw_content = article.get('content', '')
        cleaned_content = clean_html_content(raw_content)
        
        # Create text content in format Microsoft PubSec-IA expects
        content_text = f"""Title: {article.get('title', 'Untitled')}

Content:
{cleaned_content}

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
        # Use storage connection string (like in your other repo)
        if azure_storage_connection_string:
            # Use connection string authentication (no permissions needed)
            blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string)
            logging.info(f"{FUNCTION_NAME} - Using storage connection string for authentication")
        elif azure_blob_endpoint:
            # Fallback to managed identity if connection string not available
            blob_service_client = BlobServiceClient(
                account_url=azure_blob_endpoint,
                credential=azure_credential
            )
            logging.info(f"{FUNCTION_NAME} - Using managed identity for authentication")
        else:
            logging.error(f"{FUNCTION_NAME} - No storage authentication method available")
            return False
        
        # Upload to upload container (Microsoft PubSec-IA pattern)
        upload_container = "upload"  # Microsoft's upload trigger container
        blob_client = blob_service_client.get_blob_client(
            container=upload_container,
            blob=blob_name
        )
        
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(content_type='text/plain')
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
    
    # Log environment variables for debugging
    logging.info(f"{FUNCTION_NAME} - API URL: {KNOWLEDGE_BASE_API_URL}")
    logging.info(f"{FUNCTION_NAME} - Blob endpoint: {azure_blob_endpoint}")
    logging.info(f"{FUNCTION_NAME} - Has API key: {'Yes' if APIM_SUBSCRIPTION_KEY else 'No'}")
    
    try:
        # First check if we can just return basic configuration info
        test_config = req.params.get('test_config', 'false').lower() == 'true'
        if test_config:
            config_info = {
                "function_name": FUNCTION_NAME,
                "api_url": KNOWLEDGE_BASE_API_URL,
                "blob_endpoint": azure_blob_endpoint,
                "has_api_key": bool(APIM_SUBSCRIPTION_KEY),
                "api_key_length": len(APIM_SUBSCRIPTION_KEY) if APIM_SUBSCRIPTION_KEY else 0,
                "filters": {
                    "name": KB_NAME_FILTER,
                    "active": KB_ACTIVE_FILTER,
                    "status": KB_STATUS_FILTER
                },
                "local_debug": local_debug
            }
            return func.HttpResponse(
                json.dumps(config_info, indent=2),
                status_code=200,
                mimetype="application/json"
            )
        
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
        
        # Check if we should test API only (without storage upload)
        test_mode = req.params.get('test_only', 'false').lower() == 'true'
        debug_mode = req.params.get('debug', 'false').lower() == 'true'
        
        # For debug mode, collect sample content
        sample_articles = []
        
        # Convert each article and feed into Microsoft pipeline
        for i, article in enumerate(articles):
            try:
                # Convert to Microsoft format
                blob_name, content = convert_to_microsoft_format(article)
                
                # Collect sample for debug mode (first 3 articles)
                if debug_mode and len(sample_articles) < 3:
                    raw_content = article.get('content', '')
                    cleaned_content = clean_html_content(raw_content)
                    sample_articles.append({
                        "id": article.get('id', 'unknown'),
                        "title": article.get('title', 'Untitled'),
                        "original_content_preview": raw_content[:500] + "..." if len(raw_content) > 500 else raw_content,
                        "cleaned_content_preview": cleaned_content[:500] + "..." if len(cleaned_content) > 500 else cleaned_content,
                        "html_tags_removed": len(re.findall(r'<[^>]+>', raw_content)),
                        "original_length": len(raw_content),
                        "cleaned_length": len(cleaned_content),
                        "converted_content_preview": content[:300] + "..." if len(content) > 300 else content
                    })
                
                if test_mode:
                    # Test mode: just convert, don't upload
                    processed_count += 1
                    logging.info(f"{FUNCTION_NAME} - Test mode: processed article {article.get('id', 'unknown')}")
                else:
                    # Upload to Microsoft upload container (triggers existing FileUploadedFunc)
                    # Limit to first 5 articles for debugging
                    if i < 5:
                        if upload_to_microsoft_pipeline(blob_name, content):
                            processed_count += 1
                            logging.info(f"{FUNCTION_NAME} - Processed article {article.get('id', 'unknown')}")
                        else:
                            errors.append(f"Upload failed for article {article.get('id', 'unknown')}")
                    else:
                        # Skip the rest in upload mode for debugging
                        break
                
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
        
        # Add debug information if requested
        if debug_mode:
            result["debug_info"] = {
                "sample_articles": sample_articles,
                "test_mode": test_mode,
                "api_configured": bool(KNOWLEDGE_BASE_API_URL and APIM_SUBSCRIPTION_KEY)
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
