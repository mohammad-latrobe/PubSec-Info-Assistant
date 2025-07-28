#!/usr/bin/env python3
"""
Test LaTrobe API directly with the provided credentials
"""

import requests
import json
from datetime import datetime

def test_latrobe_api():
    """Test the LaTrobe API with real credentials"""
    
    url = "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase"
    headers = {
        'Ocp-Apim-Subscription-Key': 'd1d001e93d6c4698bc954ec2426da2ad',
        'Cookie': 'saplb_*=(J2EE7865220)7865251'
    }
    params = {
        'Name': 'ICT',
        'Active': 'true',
        'Status_IN': 'published'
    }
    
    print("🚀 LaTrobe API Direct Test")
    print("=" * 40)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"📡 URL: {url}")
    print(f"📋 Parameters: {params}")
    print(f"🔑 Using APIM subscription key: {headers['Ocp-Apim-Subscription-Key'][:10]}...")
    print()
    
    try:
        print("🔄 Making API request...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("🎉 API call successful!")
            try:
                json_data = response.json()
                print(f"📊 Response type: {type(json_data)}")
                
                if isinstance(json_data, list):
                    print(f"📚 Number of articles: {len(json_data)}")
                    if json_data:
                        print("📄 First article sample:")
                        print(json.dumps(json_data[0], indent=2))
                elif isinstance(json_data, dict):
                    print(f"📚 Response keys: {list(json_data.keys())}")
                    if 'value' in json_data:
                        articles = json_data['value']
                        print(f"📚 Number of articles in 'value': {len(articles)}")
                        if articles:
                            print("📄 First article sample:")
                            print(json.dumps(articles[0], indent=2))
                    else:
                        print("📄 Full response:")
                        print(json.dumps(json_data, indent=2))
                else:
                    print(f"📄 Response: {json_data}")
                    
            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON")
                print(f"📄 Raw response: {response.text[:500]}...")
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print()
    print("📋 Test Summary")
    print("=" * 30)
    if 'response' in locals() and response.status_code == 200:
        print("✅ LaTrobe API is accessible and working!")
        print("✅ Ready to integrate with Azure Functions")
    else:
        print("❌ LaTrobe API test failed")
        print("🔍 Check API credentials and endpoint")

if __name__ == "__main__":
    test_latrobe_api()
