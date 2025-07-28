#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# Local test script for LaTrobe KB Fetcher function

import sys
import os
import json
import asyncio
from unittest.mock import MagicMock

# Add functions directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions'))

# Set up environment variables for local testing
os.environ.update({
    'LOCAL_DEBUG': 'true',
    'KNOWLEDGE_BASE_API_URL': 'https://ltu-api-mgmt-prod.azure-api.net/api/v1/knowledgebase/articles',
    'APIM_SUBSCRIPTION_KEY': 'test-key-for-local-testing',
    'KB_NAME_FILTER': 'ICT',
    'KB_ACTIVE_FILTER': 'true',
    'KB_STATUS_FILTER': 'published',
    'BLOB_STORAGE_ACCOUNT_ENDPOINT': 'https://ltutrobyst3964.blob.core.windows.net/',
    'BLOB_STORAGE_ACCOUNT_OUTPUT_CONTAINER_NAME': 'content',
    'AZURE_QUEUE_STORAGE_ENDPOINT': 'https://ltutrobyst3964.queue.core.windows.net/',
    'NON_PDF_SUBMIT_QUEUE': 'non-pdf-submit-queue',
    'AZURE_OPENAI_AUTHORITY_HOST': 'AzurePublicCloud'
})

# Import the function after setting environment variables
try:
    from LatrobeKBFetcher import main as latrobe_kb_fetcher
    import azure.functions as func
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def create_mock_request(method='GET', query_params=None, body=None):
    """Create a mock HTTP request for testing"""
    mock_req = MagicMock(spec=func.HttpRequest)
    mock_req.method = method
    mock_req.params = query_params or {}
    mock_req.get_body.return_value = body or b''
    mock_req.get_json.return_value = json.loads(body) if body else {}
    return mock_req

def test_latrobe_kb_fetcher():
    """Test the LatrobeKBFetcher function locally"""
    print("🧪 Testing LatrobeKBFetcher Function Locally")
    print("=" * 60)
    
    try:
        # Test with GET request
        print("📝 Testing GET request...")
        mock_req = create_mock_request('GET')
        response = latrobe_kb_fetcher(mock_req)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Response Body Preview: {response.get_body().decode()[:200]}...")
        
        # Parse response
        response_data = json.loads(response.get_body().decode())
        
        if response.status_code == 200:
            print(f"✅ Function executed successfully!")
            print(f"   - Articles fetched: {response_data.get('articles_fetched', 0)}")
            print(f"   - Files uploaded: {response_data.get('files_uploaded', 0)}")
            print(f"   - Queue messages: {response_data.get('queue_messages_sent', 0)}")
        else:
            print(f"⚠️  Function returned status {response.status_code}")
            print(f"   - Message: {response_data.get('message', 'No message')}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error testing function: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_api_connectivity():
    """Test basic API connectivity"""
    print("\n🌐 Testing LaTrobe API Connectivity")
    print("=" * 60)
    
    import requests
    
    api_url = os.environ.get('KNOWLEDGE_BASE_API_URL')
    subscription_key = os.environ.get('APIM_SUBSCRIPTION_KEY')
    
    try:
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/json'
        }
        
        # Test API endpoint
        print(f"📡 Testing API endpoint: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 API Response Summary:")
            print(f"   - Total articles: {len(data) if isinstance(data, list) else 'Unknown'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"   - Sample article: {data[0].get('title', 'No title')[:50]}...")
        else:
            print(f"⚠️  API returned status {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
            
        return response.status_code == 200
        
    except requests.RequestException as e:
        print(f"❌ API connectivity error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 LaTrobe University - Local Function Testing")
    print("=" * 60)
    print()
    
    # Test API connectivity first
    api_test = test_api_connectivity()
    
    print()
    
    # Test the function
    function_test = test_latrobe_kb_fetcher()
    
    print()
    print("📋 Test Summary")
    print("=" * 30)
    print(f"API Connectivity: {'✅ PASS' if api_test else '❌ FAIL'}")
    print(f"Function Test:    {'✅ PASS' if function_test else '❌ FAIL'}")
    
    if api_test and function_test:
        print("\n🎉 All tests passed! Ready for Azure deployment.")
    else:
        print("\n⚠️  Some tests failed. Check the configuration.")
        if not api_test:
            print("   - Check APIM subscription key")
            print("   - Verify API endpoint URL")
        if not function_test:
            print("   - Check function code")
            print("   - Verify environment variables")
