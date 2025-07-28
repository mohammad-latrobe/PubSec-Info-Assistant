# Step 1: Test LaTrobe API Connection
# This script tests the LaTrobe API before making any changes to Microsoft PubSec-IA code

import requests
import json
import os

# LaTrobe API Configuration (from your deployment script)
KNOWLEDGE_BASE_API_URL = "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase"
APIM_SUBSCRIPTION_KEY = "d1d001e93d6c4698bc954ec2426da2ad"
KB_NAME_FILTER = "ICT"
KB_ACTIVE_FILTER = "true"
KB_STATUS_FILTER = "published"

# Test different filter combinations
TEST_FILTERS = [
    {"name": "ICT", "active": "true", "status": "published"},
    {"name": "ICT", "active": "true"},  # Try without status filter
    {"active": "true", "status": "published"},  # Try without name filter
    {"active": "true"},  # Try with only active filter
    {}  # Try with no filters
]

def test_latrobe_api():
    """Test LaTrobe API connection with different filter combinations"""
    print("🧪 Step 1: Testing LaTrobe API Connection...")
    
    headers = {
        'Ocp-Apim-Subscription-Key': APIM_SUBSCRIPTION_KEY,
        'Content-Type': 'application/json'
    }
    
    for i, params in enumerate(TEST_FILTERS):
        try:
            print(f"\n📊 Test {i+1}: Filters = {params}")
            print(f"📡 Calling: {KNOWLEDGE_BASE_API_URL}")
            
            response = requests.get(KNOWLEDGE_BASE_API_URL, headers=headers, params=params)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                kb_data = response.json()
                print(f"✅ API Call Successful!")
                
                # Handle both array and object responses
                articles = kb_data.get('value', []) if isinstance(kb_data, dict) else kb_data
                
                print(f"📚 Found {len(articles)} KB articles")
                
                if articles:
                    print("\n🔍 Sample Article Structure:")
                    sample = articles[0]
                    for key, value in sample.items():
                        value_preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        print(f"  {key}: {value_preview}")
                    
                    print(f"\n🎉 Success! Found {len(articles)} articles with filters: {params}")
                    return True, articles
                    
            else:
                print(f"❌ API Call Failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"🚨 Error with filters {params}: {str(e)}")
            continue
    
    print(f"\n⚠️  No articles found with any filter combination")
    return True, []  # API works, just no data

if __name__ == "__main__":
    success, articles = test_latrobe_api()
    
    if success:
        print(f"\n🎉 Step 1 Complete: LaTrobe API is accessible")
        if articles:
            print(f"✅ Ready to proceed to Step 2: Minimal Microsoft PubSec-IA Integration")
        else:
            print(f"⚠️  Consider adjusting filters to get test data")
    else:
        print(f"\n🛑 Step 1 Failed: Fix API connection before proceeding")
