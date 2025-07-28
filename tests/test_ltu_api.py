# Test script for PubSec Information Assistant Functions with LTU API
# This script tests the KB article processing and indexing functions

import json
import requests
import time
from datetime import datetime

# Configuration - Update these with your actual function URLs
PROCESS_KB_FUNCTION_URL = "https://your-function-app.azurewebsites.net/api/ProcessKBArticles"
INDEX_KB_FUNCTION_URL = "https://your-function-app.azurewebsites.net/api/IndexKBChunks"
FUNCTION_KEY = "your-function-key"  # Get from Azure portal

# LTU API Configuration for direct testing (optional)
LTU_API_URL = "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase"
LTU_API_KEY = "d1d001e93d6c4698bc954ec2426da2ad"

def test_ltu_api_direct():
    """Test direct connection to LTU API"""
    print("=" * 60)
    print("Testing Direct LTU API Connection")
    print("=" * 60)
    
    headers = {
        'Ocp-Apim-Subscription-Key': LTU_API_KEY,
        'Cookie': 'saplb_*=(J2EE7865220)7865251',
        'Accept': 'application/json',
        'User-Agent': 'PubSec-IA-Test/1.0'
    }
    
    params = {
        'Name': 'ICT',
        'Active': 'true',
        'Status_IN': 'published'
    }
    
    try:
        print(f"Connecting to: {LTU_API_URL}")
        print(f"Parameters: {params}")
        
        response = requests.get(LTU_API_URL, headers=headers, params=params, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LTU API connection successful!")
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Found {len(data)} articles")
                if len(data) > 0:
                    print("Sample article keys:", list(data[0].keys()) if data[0] else "Empty article")
            elif isinstance(data, dict):
                print("Response keys:", list(data.keys()))
                if 'data' in data:
                    print(f"Articles in data: {len(data['data']) if isinstance(data['data'], list) else 'Not a list'}")
                elif 'items' in data:
                    print(f"Articles in items: {len(data['items']) if isinstance(data['items'], list) else 'Not a list'}")
            
            return True
        else:
            print(f"❌ LTU API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LTU API: {str(e)}")
        return False

def test_process_kb_articles():
    """Test the ProcessKBArticles function (now fetches from API)"""
    print("\n" + "=" * 60)
    print("Testing ProcessKBArticles Function (LTU API Fetch)")
    print("=" * 60)
    
    headers = {
        "x-functions-key": FUNCTION_KEY
    }
    
    # Test with default parameters
    try:
        print("Triggering KB articles fetch and processing...")
        response = requests.get(PROCESS_KB_FUNCTION_URL, headers=headers, timeout=300)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ProcessKBArticles succeeded!")
            print(f"API endpoint used: {result.get('api_endpoint', 'Unknown')}")
            print(f"Filters used: {result.get('filters_used', {})}")
            print(f"Articles fetched from API: {result.get('articles_fetched', 0)}")
            print(f"Articles processed: {result.get('articles_processed', 0)}")
            print(f"Articles failed: {result.get('articles_failed', 0)}")
            print(f"Total chunks created: {result.get('total_chunks_created', 0)}")
            
            # Show details for each article
            details = result.get('details', [])
            if details:
                print("\nProcessed articles:")
                for detail in details[:5]:  # Show first 5
                    if 'error' in detail:
                        print(f"  ❌ {detail['title']}: {detail['error']}")
                    else:
                        print(f"  ✅ {detail['title']}: {detail['chunks_created']} chunks, {detail['chunks_uploaded']} uploaded")
                
                if len(details) > 5:
                    print(f"  ... and {len(details) - 5} more articles")
            
            return True
        else:
            print(f"❌ ProcessKBArticles failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ProcessKBArticles: {str(e)}")
        return False

def test_process_kb_articles_with_params():
    """Test the ProcessKBArticles function with custom parameters"""
    print("\n" + "=" * 60)
    print("Testing ProcessKBArticles with Custom Parameters")
    print("=" * 60)
    
    headers = {
        "x-functions-key": FUNCTION_KEY
    }
    
    # Test with custom parameters
    params = {
        'kb_name': 'ICT',
        'status': 'published',
        'force_refresh': 'true'
    }
    
    try:
        print(f"Testing with parameters: {params}")
        response = requests.get(PROCESS_KB_FUNCTION_URL, headers=headers, params=params, timeout=300)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ProcessKBArticles with params succeeded!")
            print(f"Articles fetched: {result.get('articles_fetched', 0)}")
            print(f"Articles processed: {result.get('articles_processed', 0)}")
            print(f"Total chunks: {result.get('total_chunks_created', 0)}")
            return True
        else:
            print(f"❌ ProcessKBArticles with params failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ProcessKBArticles with params: {str(e)}")
        return False

def test_index_kb_chunks():
    """Test the IndexKBChunks function"""
    print("\n" + "=" * 60)
    print("Testing IndexKBChunks Function")
    print("=" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "x-functions-key": FUNCTION_KEY
    }
    
    # Test with default parameters
    try:
        print("Indexing KB article chunks...")
        response = requests.post(INDEX_KB_FUNCTION_URL, headers=headers, timeout=180)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ IndexKBChunks succeeded!")
            print(f"Total processed: {result.get('total_processed', 0)}")
            print(f"Successfully indexed: {result.get('indexed_count', 0)}")
            print(f"Failed: {result.get('failed_count', 0)}")
            
            # Show details for each processed file
            processed_files = result.get('processed_files', [])
            if processed_files:
                print("\nProcessed files:")
                for file_info in processed_files[:10]:  # Show first 10
                    status = file_info.get('status', 'unknown')
                    blob_name = file_info.get('blob_name', 'unknown')
                    print(f"  - {blob_name}: {status}")
                
                if len(processed_files) > 10:
                    print(f"  ... and {len(processed_files) - 10} more files")
            
            return True
        else:
            print(f"❌ IndexKBChunks failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing IndexKBChunks: {str(e)}")
        return False

def test_end_to_end_workflow():
    """Test the complete workflow: API fetch -> Process -> Index"""
    print("\n" + "=" * 60)
    print("Testing End-to-End Workflow")
    print("=" * 60)
    
    # Step 1: Test direct API connection
    print("Step 1: Testing direct LTU API connection...")
    api_success = test_ltu_api_direct()
    
    if not api_success:
        print("❌ Direct API test failed. Check API credentials and network connectivity.")
        return False
    
    # Step 2: Process articles from API
    print("\nStep 2: Processing articles via Azure Function...")
    process_success = test_process_kb_articles()
    
    if not process_success:
        print("❌ Article processing failed. Check function logs.")
        return False
    
    # Wait for blob processing
    print("\n⏳ Waiting 15 seconds for blob processing...")
    time.sleep(15)
    
    # Step 3: Index the processed chunks
    print("\nStep 3: Indexing processed chunks...")
    index_success = test_index_kb_chunks()
    
    if not index_success:
        print("❌ Indexing failed. Check function logs and search service.")
        return False
    
    print("\n🎉 End-to-end workflow completed successfully!")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting PubSec Information Assistant Function Tests with LTU API")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Update URLs with actual function app name
    print(f"\nFunction URLs:")
    print(f"  ProcessKBArticles: {PROCESS_KB_FUNCTION_URL}")
    print(f"  IndexKBChunks: {INDEX_KB_FUNCTION_URL}")
    print(f"\nLTU API Configuration:")
    print(f"  API URL: {LTU_API_URL}")
    print(f"  API Key: {LTU_API_KEY[:8]}..." if LTU_API_KEY else "  API Key: Not configured")
    
    if "your-function-app" in PROCESS_KB_FUNCTION_URL:
        print("\n⚠️  WARNING: Please update the function URLs and keys in this script!")
        print("⚠️  Replace 'your-function-app' with your actual function app name")
        print("⚠️  Replace 'your-function-key' with your actual function key")
        return
    
    # Run individual tests
    print("\n" + "="*60)
    print("INDIVIDUAL TESTS")
    print("="*60)
    
    # Test 1: Direct API connection
    test_ltu_api_direct()
    
    # Test 2: Process KB Articles (default)
    test_process_kb_articles()
    
    # Test 3: Process KB Articles (with params)
    test_process_kb_articles_with_params()
    
    # Test 4: Index chunks
    time.sleep(5)  # Brief pause
    test_index_kb_chunks()
    
    # Test 5: End-to-end workflow
    print("\n" + "="*60)
    print("END-TO-END WORKFLOW TEST")
    print("="*60)
    
    e2e_success = test_end_to_end_workflow()
    
    if e2e_success:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Check Azure AI Search index for the indexed documents")
        print("2. Test search queries in Azure portal")
        print("3. Monitor function logs for any issues")
        print("4. Set up scheduled execution if needed")
    else:
        print("\n❌ Some tests failed. Check function logs and API connectivity.")

if __name__ == "__main__":
    main()
