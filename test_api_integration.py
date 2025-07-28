#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# Simple local test for LaTrobe API integration logic

import os
import json
import requests
from datetime import datetime

# Set up environment variables for local testing
os.environ.update({
    'LOCAL_DEBUG': 'true',
    'KNOWLEDGE_BASE_API_URL': 'https://ltu-api-mgmt-prod.azure-api.net/api/v1/knowledgebase/articles',
    'APIM_SUBSCRIPTION_KEY': 'test-key-for-local-testing',  # You'll need to provide the real key
    'KB_NAME_FILTER': 'ICT',
    'KB_ACTIVE_FILTER': 'true',
    'KB_STATUS_FILTER': 'published'
})

def test_latrobe_api_directly():
    """Test the LaTrobe API directly without Azure Functions wrapper"""
    print("🧪 Testing LaTrobe API Integration Logic")
    print("=" * 60)
    
    # Get environment variables
    api_url = os.environ.get('KNOWLEDGE_BASE_API_URL')
    subscription_key = os.environ.get('APIM_SUBSCRIPTION_KEY')
    kb_name_filter = os.environ.get('KB_NAME_FILTER', 'ICT')
    kb_active_filter = os.environ.get('KB_ACTIVE_FILTER', 'true')
    kb_status_filter = os.environ.get('KB_STATUS_FILTER', 'published')
    
    print(f"📡 API URL: {api_url}")
    print(f"🔍 Filters: name={kb_name_filter}, active={kb_active_filter}, status={kb_status_filter}")
    print()
    
    try:
        # Set up headers
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/json',
            'User-Agent': 'LaTrobe-University-Information-Assistant/1.0'
        }
        
        # Set up query parameters
        params = {
            'name': kb_name_filter,
            'active': kb_active_filter,
            'status': kb_status_filter
        }
        
        print("📡 Making API request...")
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                articles = response.json()
                print(f"\n📊 API Response Analysis:")
                print(f"   - Articles count: {len(articles) if isinstance(articles, list) else 'Not a list'}")
                
                if isinstance(articles, list):
                    if len(articles) > 0:
                        sample_article = articles[0]
                        print(f"   - Sample article keys: {list(sample_article.keys()) if isinstance(sample_article, dict) else 'Not a dict'}")
                        
                        if isinstance(sample_article, dict):
                            print(f"   - Sample title: {sample_article.get('title', 'No title')[:100]}...")
                            print(f"   - Sample content length: {len(str(sample_article.get('content', '')))}")
                            
                        # Show a few more samples
                        print(f"\n📚 First 3 article titles:")
                        for i, article in enumerate(articles[:3]):
                            if isinstance(article, dict):
                                title = article.get('title', f'Article {i+1}')
                                print(f"   {i+1}. {title[:80]}...")
                    else:
                        print("   - No articles found with current filters")
                        
                return True, articles if isinstance(articles, list) else []
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📄 Raw response (first 500 chars): {response.text[:500]}...")
                return False, []
                
        elif response.status_code == 401:
            print("❌ Authentication failed - check APIM subscription key")
            return False, []
        elif response.status_code == 404:
            print("❌ API endpoint not found - check URL")
            return False, []
        else:
            print(f"❌ API returned error status {response.status_code}")
            print(f"📄 Response body: {response.text[:500]}...")
            return False, []
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - API took too long to respond")
        return False, []
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check network connectivity")
        return False, []
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        return False, []

def simulate_article_processing(articles):
    """Simulate how articles would be processed by the Microsoft pipeline"""
    print("\n🔄 Simulating Article Processing Pipeline")
    print("=" * 60)
    
    if not articles:
        print("❌ No articles to process")
        return False
    
    processed_count = 0
    
    for article in articles[:5]:  # Process first 5 articles as example
        if not isinstance(article, dict):
            continue
            
        # Simulate creating a file for the Microsoft pipeline
        title = article.get('title', 'Untitled')
        content = article.get('content', '')
        article_id = article.get('id', f'article_{processed_count + 1}')
        
        # Create a filename that would work with the Microsoft pipeline
        safe_filename = f"latrobe_kb_{article_id}_{title[:30].replace(' ', '_').replace('/', '_')}.txt"
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '._-')
        
        print(f"📄 Processing: {safe_filename}")
        print(f"   - Title: {title[:60]}...")
        print(f"   - Content length: {len(content)} characters")
        
        # This is where we would upload to blob storage and send to queue
        # For now, just simulate the process
        processed_count += 1
    
    print(f"\n✅ Simulated processing of {processed_count} articles")
    print("   - Files would be uploaded to 'content' container")
    print("   - Queue messages would be sent to 'non-pdf-submit-queue'")
    
    return True

def main():
    print("🚀 LaTrobe University - API Integration Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API connectivity and data retrieval
    api_success, articles = test_latrobe_api_directly()
    
    if api_success:
        # Test article processing simulation
        processing_success = simulate_article_processing(articles)
        
        print(f"\n📋 Test Summary")
        print("=" * 30)
        print(f"API Test:        {'✅ PASS' if api_success else '❌ FAIL'}")
        print(f"Processing Test: {'✅ PASS' if processing_success else '❌ FAIL'}")
        
        if api_success and processing_success:
            print(f"\n🎉 All tests passed!")
            print("   - LaTrobe API is accessible")
            print("   - Articles can be retrieved and processed")
            print("   - Integration logic is working correctly")
            print(f"   - Ready to test with Azure Functions")
        else:
            print(f"\n⚠️  Some tests failed")
            
    else:
        print(f"\n❌ API test failed - cannot proceed with processing test")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check APIM subscription key in test script")
        print("   2. Verify API endpoint URL")
        print("   3. Test network connectivity")
        print("   4. Check API management service status")

if __name__ == "__main__":
    main()
