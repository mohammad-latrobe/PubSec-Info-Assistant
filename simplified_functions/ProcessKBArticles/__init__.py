# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any
import tiktoken
from nltk.tokenize import sent_tokenize
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# Configuration from environment variables
BLOB_STORAGE_ACCOUNT_ENDPOINT = os.environ.get("BLOB_STORAGE_ACCOUNT_ENDPOINT")
BLOB_CONTENT_CONTAINER_NAME = os.environ.get("BLOB_CONTENT_CONTAINER_NAME", "content")
CHUNK_TARGET_SIZE = int(os.environ.get("CHUNK_TARGET_SIZE", "750"))
LOCAL_DEBUG = os.environ.get("LOCAL_DEBUG", "false").lower() == "true"

# API Configuration for Knowledge Base
KNOWLEDGE_BASE_API_URL = os.environ.get("KNOWLEDGE_BASE_API_URL", "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase")
APIM_SUBSCRIPTION_KEY = os.environ.get("APIM_SUBSCRIPTION_KEY")
KB_NAME_FILTER = os.environ.get("KB_NAME_FILTER", "ICT")
KB_ACTIVE_FILTER = os.environ.get("KB_ACTIVE_FILTER", "true")
KB_STATUS_FILTER = os.environ.get("KB_STATUS_FILTER", "published")

# Authentication
if LOCAL_DEBUG:
    azure_credential = DefaultAzureCredential()
else:
    azure_credential = ManagedIdentityCredential()

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken encoding"""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception as e:
        logging.warning(f"Token counting failed: {e}. Using word count approximation.")
        return len(text.split()) * 1.3  # Rough approximation

def create_chunk_json(
    content: str,
    file_name: str,
    file_uri: str,
    chunk_number: int,
    title: str = "",
    section: str = "",
    pages: List[int] = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a standardized chunk JSON structure matching PubSec-IA format"""
    if pages is None:
        pages = [1]
    if metadata is None:
        metadata = {}
    
    token_count = count_tokens(content)
    
    chunk_data = {
        'file_name': file_name,
        'file_uri': file_uri,
        'file_class': 'knowledge_base',
        'processed_datetime': datetime.now().isoformat(),
        'title': title,
        'subtitle': '',
        'section': section,
        'pages': pages,
        'token_count': token_count,
        'content': content,
        'chunk_number': chunk_number,
        'metadata': metadata
    }
    
    return chunk_data

def chunk_text_by_sentences(text: str, target_size: int) -> List[str]:
    """Split text into chunks based on sentence boundaries, respecting token limits"""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        
        if count_tokens(test_chunk) <= target_size:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def upload_chunk_to_blob(
    blob_service_client: BlobServiceClient,
    container_name: str,
    chunk_data: Dict[str, Any],
    file_directory: str = ""
) -> str:
    """Upload chunk JSON to blob storage"""
    try:
        file_name = chunk_data['file_name']
        chunk_number = chunk_data['chunk_number']
        
        # Create blob path following PubSec-IA convention
        if file_directory:
            blob_path = f"{file_directory}/{file_name}/chunk-{chunk_number}.json"
        else:
            blob_path = f"{file_name}/chunk-{chunk_number}.json"
        
        # Convert to JSON
        json_content = json.dumps(chunk_data, indent=2, ensure_ascii=False)
        
        # Upload to blob
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_path
        )
        
        blob_client.upload_blob(json_content, overwrite=True)
        
        logging.info(f"Successfully uploaded chunk {chunk_number} to {blob_path}")
        return blob_path
        
    except Exception as e:
        logging.error(f"Failed to upload chunk {chunk_number}: {str(e)}")
        raise

def fetch_knowledge_base_articles() -> List[Dict[str, Any]]:
    """Fetch knowledge base articles from the LTU API"""
    
    if not APIM_SUBSCRIPTION_KEY:
        raise ValueError("APIM_SUBSCRIPTION_KEY environment variable is required")
    
    # Prepare API request
    url = KNOWLEDGE_BASE_API_URL
    headers = {
        'Ocp-Apim-Subscription-Key': APIM_SUBSCRIPTION_KEY,
        'Cookie': 'saplb_*=(J2EE7865220)7865251',
        'Accept': 'application/json',
        'User-Agent': 'PubSec-IA-Functions/1.0'
    }
    
    params = {
        'Name': KB_NAME_FILTER,
        'Active': KB_ACTIVE_FILTER,
        'Status_IN': KB_STATUS_FILTER
    }
    
    try:
        logging.info(f"Fetching KB articles from API: {url}")
        logging.info(f"Parameters: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        logging.info(f"API Response Status: {response.status_code}")
        logging.info(f"Raw API response type: {type(data)}")
        
        # Handle different response formats
        articles = []
        
        if isinstance(data, list):
            # Direct array of articles
            raw_articles = data
        elif isinstance(data, dict):
            # Check common wrapper patterns
            if 'data' in data:
                raw_articles = data['data']
            elif 'items' in data:
                raw_articles = data['items']
            elif 'results' in data:
                raw_articles = data['results']
            elif 'articles' in data:
                raw_articles = data['articles']
            else:
                # Assume the dict itself is an article
                raw_articles = [data]
        else:
            logging.error(f"Unexpected API response format: {type(data)}")
            raise ValueError(f"Unexpected API response format: {type(data)}")
        
        logging.info(f"Found {len(raw_articles)} raw articles from API")
        
        # Transform API response to our expected format
        for i, article in enumerate(raw_articles):
            try:
                transformed_article = transform_api_article(article, i + 1)
                if transformed_article:
                    articles.append(transformed_article)
            except Exception as e:
                logging.error(f"Error transforming article {i}: {str(e)}")
                continue
        
        logging.info(f"Successfully transformed {len(articles)} articles")
        return articles
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse API response as JSON: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error fetching KB articles: {str(e)}")
        raise

def transform_api_article(api_article: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Transform API article format to our expected format"""
    
    # Log the structure for debugging
    logging.debug(f"Transforming article {index}: {list(api_article.keys())}")
    
    # Extract content - try different possible field names
    content_fields = ['content', 'description', 'body', 'text', 'summary', 'details']
    content = ""
    
    for field in content_fields:
        if field in api_article and api_article[field]:
            content = str(api_article[field])
            break
    
    if not content:
        # If no content field found, combine all text fields
        text_fields = []
        for key, value in api_article.items():
            if isinstance(value, str) and len(value) > 10:  # Reasonable text length
                text_fields.append(f"{key}: {value}")
        content = "\n\n".join(text_fields)
    
    # Extract title - try different possible field names
    title_fields = ['title', 'name', 'subject', 'heading', 'summary']
    title = ""
    
    for field in title_fields:
        if field in api_article and api_article[field]:
            title = str(api_article[field])
            break
    
    if not title:
        title = f"Knowledge Base Article {index}"
    
    # Extract ID for filename
    id_fields = ['id', 'articleId', 'knowledgeBaseId', 'guid', 'key']
    article_id = ""
    
    for field in id_fields:
        if field in api_article and api_article[field]:
            article_id = str(api_article[field])
            break
    
    if not article_id:
        article_id = f"article-{index}"
    
    # Create filename (clean for filesystem)
    filename = f"kb-{article_id}".lower()
    filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_'))
    
    # Extract URL if available
    url_fields = ['url', 'link', 'permalink', 'href']
    url = ""
    
    for field in url_fields:
        if field in api_article and api_article[field]:
            url = str(api_article[field])
            break
    
    if not url:
        url = f"https://kb.internal/article/{article_id}"
    
    # Build metadata from remaining fields
    metadata = {
        "source_api": "LTU Knowledge Base",
        "fetched_datetime": datetime.now().isoformat(),
        "original_api_response": api_article
    }
    
    # Extract common metadata fields
    metadata_mapping = {
        'author': ['author', 'createdBy', 'owner'],
        'category': ['category', 'type', 'classification'],
        'department': ['department', 'team', 'group'],
        'created': ['created', 'createdDate', 'dateCreated'],
        'modified': ['modified', 'modifiedDate', 'lastModified', 'updated'],
        'status': ['status', 'state'],
        'version': ['version', 'revision'],
        'tags': ['tags', 'keywords', 'labels']
    }
    
    for meta_key, possible_fields in metadata_mapping.items():
        for field in possible_fields:
            if field in api_article and api_article[field]:
                metadata[meta_key] = api_article[field]
                break
    
    # Determine security classification based on content/metadata
    security_config = determine_security_from_api_article(api_article, metadata)
    metadata["security"] = security_config
    
    # Validate minimum requirements
    if len(content.strip()) < 10:
        logging.warning(f"Article {index} has insufficient content, skipping")
        return None
    
    transformed = {
        "title": title,
        "content": content,
        "url": url,
        "filename": filename,
        "metadata": metadata
    }
    
    logging.info(f"Transformed article: {title} ({len(content)} chars)")
    return transformed

def determine_security_from_api_article(api_article: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Determine security classification from API article data"""
    
    # Default security configuration
    security_config = {
        "access_level": "internal",
        "security_groups": ["employees"],
        "department": "general",
        "classification": "internal"
    }
    
    # Check for explicit security fields in API response
    if 'security' in api_article:
        security_config.update(api_article['security'])
        return security_config
    
    # Infer from other fields
    title_lower = metadata.get('original_api_response', {}).get('title', '').lower()
    content_lower = metadata.get('original_api_response', {}).get('content', '').lower()
    category_lower = str(metadata.get('category', '')).lower()
    
    # Check for public indicators
    public_indicators = ['public', 'external', 'customer', 'website']
    if any(indicator in title_lower or indicator in content_lower or indicator in category_lower 
           for indicator in public_indicators):
        security_config = {
            "access_level": "public",
            "security_groups": ["everyone"],
            "department": "general",
            "classification": "unclassified"
        }
    
    # Check for confidential indicators
    confidential_indicators = ['confidential', 'restricted', 'private', 'sensitive']
    if any(indicator in title_lower or indicator in content_lower or indicator in category_lower 
           for indicator in confidential_indicators):
        security_config = {
            "access_level": "confidential",
            "security_groups": ["management", "authorized_users"],
            "department": "restricted",
            "classification": "confidential"
        }
    
    # Check for HR-specific content
    hr_indicators = ['hr', 'human resources', 'employee handbook', 'benefits', 'payroll']
    if any(indicator in title_lower or indicator in content_lower or indicator in category_lower 
           for indicator in hr_indicators):
        security_config = {
            "access_level": "restricted",
            "security_groups": ["hr_team", "management"],
            "department": "human_resources",
            "classification": "restricted"
        }
    
    # Check for IT/technical content
    it_indicators = ['it', 'technical', 'system', 'network', 'security policy']
    if any(indicator in title_lower or indicator in content_lower or indicator in category_lower 
           for indicator in it_indicators):
        security_config["department"] = "information_technology"
    
    return security_config

def process_kb_article(
    article_content: str,
    article_title: str,
    article_url: str,
    file_name: str,
    metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """Process a knowledge base article into chunks"""
    
    logging.info(f"Processing KB article: {article_title}")
    
    # Split content into manageable chunks
    chunks_text = chunk_text_by_sentences(article_content, CHUNK_TARGET_SIZE)
    chunk_objects = []
    
    for i, chunk_text in enumerate(chunks_text):
        chunk_data = create_chunk_json(
            content=chunk_text,
            file_name=file_name,
            file_uri=article_url,
            chunk_number=i + 1,
            title=article_title,
            section=f"Section {i + 1}",
            metadata=metadata
        )
        chunk_objects.append(chunk_data)
    
    logging.info(f"Created {len(chunk_objects)} chunks for article: {article_title}")
    return chunk_objects

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to fetch KB articles from LTU API and store as JSON chunks.
    
    Optional request parameters:
    - force_refresh: Force refresh even if recent data exists (default: false)
    - kb_name: Override KB name filter (default: from env var)
    - status: Override status filter (default: from env var)
    """
    
    logging.info('Starting KB articles fetch and processing')
    
    try:
        # Parse optional request parameters
        force_refresh = req.params.get('force_refresh', 'false').lower() == 'true'
        kb_name_override = req.params.get('kb_name')
        status_override = req.params.get('status')
        
        # Override environment variables if provided
        global KB_NAME_FILTER, KB_STATUS_FILTER
        if kb_name_override:
            KB_NAME_FILTER = kb_name_override
        if status_override:
            KB_STATUS_FILTER = status_override
        
        logging.info(f"Processing with filters - Name: {KB_NAME_FILTER}, Status: {KB_STATUS_FILTER}")
        
        # Fetch articles from API
        try:
            articles = fetch_knowledge_base_articles()
            logging.info(f"Successfully fetched {len(articles)} articles from API")
        except Exception as e:
            logging.error(f"Failed to fetch articles from API: {str(e)}")
            return func.HttpResponse(
                json.dumps({
                    'status': 'error',
                    'message': f'Failed to fetch articles from API: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }),
                status_code=500,
                mimetype="application/json"
            )
        
        if not articles:
            return func.HttpResponse(
                json.dumps({
                    'status': 'completed',
                    'message': 'No articles found matching the criteria',
                    'articles_processed': 0,
                    'total_chunks_created': 0,
                    'timestamp': datetime.now().isoformat()
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Initialize blob client
        blob_service_client = BlobServiceClient(
            account_url=BLOB_STORAGE_ACCOUNT_ENDPOINT,
            credential=azure_credential
        )
        
        processed_articles = []
        total_chunks = 0
        
        # Process each article
        for article in articles:
            try:
                # Process article into chunks
                chunks = process_kb_article(
                    article_content=article['content'],
                    article_title=article['title'],
                    article_url=article['url'],
                    file_name=article['filename'],
                    metadata=article.get('metadata', {})
                )
                
                # Upload chunks to blob storage
                uploaded_chunks = []
                for chunk in chunks:
                    try:
                        blob_path = upload_chunk_to_blob(
                            blob_service_client,
                            BLOB_CONTENT_CONTAINER_NAME,
                            chunk,
                            "kb_articles"  # Directory for KB articles
                        )
                        uploaded_chunks.append(blob_path)
                    except Exception as e:
                        logging.error(f"Failed to upload chunk: {str(e)}")
                        continue
                
                processed_articles.append({
                    'title': article['title'],
                    'filename': article['filename'],
                    'source_url': article['url'],
                    'chunks_created': len(chunks),
                    'chunks_uploaded': len(uploaded_chunks),
                    'blob_paths': uploaded_chunks
                })
                
                total_chunks += len(uploaded_chunks)
                
            except Exception as e:
                logging.error(f"Error processing article '{article.get('title', 'Unknown')}': {str(e)}")
                processed_articles.append({
                    'title': article.get('title', 'Unknown'),
                    'filename': article.get('filename', 'unknown'),
                    'error': str(e),
                    'chunks_created': 0,
                    'chunks_uploaded': 0
                })
                continue
        
        # Return summary
        result = {
            'status': 'completed',
            'api_endpoint': KNOWLEDGE_BASE_API_URL,
            'filters_used': {
                'name': KB_NAME_FILTER,
                'active': KB_ACTIVE_FILTER,
                'status': KB_STATUS_FILTER
            },
            'articles_fetched': len(articles),
            'articles_processed': len([a for a in processed_articles if 'error' not in a]),
            'articles_failed': len([a for a in processed_articles if 'error' in a]),
            'total_chunks_created': total_chunks,
            'details': processed_articles,
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info(f"Processing completed: {result['articles_processed']} successful, {result['articles_failed']} failed")
        
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
