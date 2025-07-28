import requests
import json

def test_azure_function():
    """Test the LatrobeKBFetcher function on Azure Function App"""
    
    # Azure Function App URL
    function_url = "https://ltu-troby-func-dev-3964.azurewebsites.net/api/LatrobeKBFetcher"
    
    print("🧪 Testing LatrobeKBFetcher on Azure Function App")
    print("=" * 50)
    print(f"🌐 Function URL: {function_url}")
    
    try:
        print("🔄 Making request to Azure Function...")
        response = requests.get(function_url, timeout=30)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"🎉 Function call successful!")
            print(f"📊 Response type: {type(response_data)}")
            
            if isinstance(response_data, dict):
                print(f"📚 Response keys: {list(response_data.keys())}")
                
                # Check if we have articles
                if 'articles' in response_data:
                    articles = response_data['articles']
                    print(f"📰 Number of articles: {len(articles)}")
                    
                    if articles:
                        print("\n📋 First article preview:")
                        first_article = articles[0]
                        for key, value in first_article.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"  {key}: {value[:100]}...")
                            else:
                                print(f"  {key}: {value}")
                else:
                    print("🔍 Response structure:")
                    print(json.dumps(response_data, indent=2)[:500] + "...")
            
        else:
            print(f"❌ Function call failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - function may be cold starting")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_azure_function()
