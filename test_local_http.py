#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# Test the local LatrobeKBFetcher function via HTTP

import requests
import json
from datetime import datetime

def test_local_function():
    """Test the LatrobeKBFetcher function running locally"""
    print("🧪 Testing Local LatrobeKBFetcher Function")
    print("=" * 60)
    
    function_url = "http://localhost:7071/api/LatrobeKBFetcher"
    
    try:
        print(f"📡 Testing GET request to: {function_url}")
        
        # Test GET request
        response = requests.get(function_url, timeout=30)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📊 Function Response:")
                print(f"   - Status: {result.get('status', 'unknown')}")
                print(f"   - Message: {result.get('message', 'no message')}")
                print(f"   - Articles processed: {result.get('articles_fetched', 0)}")
                print(f"   - Files uploaded: {result.get('files_uploaded', 0)}")
                print(f"   - Queue messages: {result.get('queue_messages_sent', 0)}")
                
                # Print first few lines of response for debugging
                response_text = response.text
                print(f"\n📄 Full response preview:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
                return True
                
            except json.JSONDecodeError:
                print(f"⚠️  Response is not JSON format")
                print(f"📄 Raw response: {response.text[:200]}...")
                return True  # Still consider success if function responds
                
        elif response.status_code == 500:
            print(f"⚠️  Function returned server error")
            print(f"📄 Error details: {response.text[:300]}...")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to function - is it running?")
        print(f"   Make sure 'func start' is running in the functions directory")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Function request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_with_post():
    """Test with POST request"""
    print(f"\n🧪 Testing POST request")
    print("=" * 40)
    
    function_url = "http://localhost:7071/api/LatrobeKBFetcher"
    
    try:
        # Test POST with some data
        test_data = {
            "test_mode": True,
            "max_articles": 5
        }
        
        response = requests.post(function_url, json=test_data, timeout=30)
        
        print(f"✅ POST Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"📄 POST Response: {response.text[:200]}...")
            return True
        else:
            print(f"⚠️  POST request failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ POST test error: {str(e)}")
        return False

def main():
    print("🚀 Local Function Testing")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test GET request
    get_success = test_local_function()
    
    # Test POST request
    post_success = test_with_post()
    
    print()
    print("📋 Test Summary")
    print("=" * 30)
    print(f"GET Test:  {'✅ PASS' if get_success else '❌ FAIL'}")
    print(f"POST Test: {'✅ PASS' if post_success else '❌ FAIL'}")
    
    if get_success:
        print(f"\n🎉 LatrobeKBFetcher function is responding!")
        print("   - Function is loaded and accessible")
        print("   - Ready for integration testing")
        print("   - Next step: Test with real APIM subscription key")
    else:
        print(f"\n⚠️  Function test failed")
        print("   - Check if functions are running: func start")
        print("   - Check for any error messages in function logs")

if __name__ == "__main__":
    main()
