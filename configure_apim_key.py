#!/usr/bin/env python3
"""
APIM Subscription Key Configuration Helper
Help configure the LaTrobe API APIM subscription key
"""

import os
import json

def update_local_settings(apim_key):
    """Update local.settings.json with APIM subscription key"""
    settings_file = "functions/local.settings.json"
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # Update the APIM subscription key
        settings['Values']['APIM_SUBSCRIPTION_KEY'] = apim_key
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"✅ Updated {settings_file} with APIM subscription key")
        return True
        
    except Exception as e:
        print(f"❌ Error updating local settings: {e}")
        return False

def update_azure_function_settings(apim_key):
    """Generate Azure CLI command to update function app settings"""
    function_app_name = "ltu-troby-func-dev-3964"
    resource_group = "LTU-AI-TROBY-DEV"
    
    cli_command = f'''az functionapp config appsettings set \\
  --resource-group {resource_group} \\
  --name {function_app_name} \\
  --settings "APIM_SUBSCRIPTION_KEY={apim_key}"'''
    
    return cli_command

def main():
    print("🔑 LaTrobe API - APIM Subscription Key Configuration")
    print("=" * 60)
    print()
    
    print("To configure the APIM subscription key, you need:")
    print("1. The APIM subscription key from LaTrobe University")
    print("2. Access to the LaTrobe API Management portal")
    print()
    
    print("Current configuration:")
    print(f"  API URL: https://ltu-api-mgmt-prod.azure-api.net/api/v1/knowledgebase/articles")
    print(f"  Filters: name=ICT, active=true, status=published")
    print()
    
    apim_key = input("Enter your APIM subscription key (or press Enter to skip): ").strip()
    
    if apim_key and apim_key != "your-apim-subscription-key-here":
        print()
        print("🔄 Updating configuration...")
        
        # Update local settings
        if update_local_settings(apim_key):
            print("✅ Local settings updated")
        
        # Generate Azure CLI command
        cli_command = update_azure_function_settings(apim_key)
        print()
        print("📋 To update Azure Function App settings, run:")
        print(cli_command)
        print()
        
        print("🧪 Testing steps:")
        print("1. Restart local Azure Functions: func start --port 7071")
        print("2. Test locally: python test_local_http.py")
        print("3. Update Azure settings with the CLI command above")
        print("4. Test Azure function: python test_azure_http.py")
        
    else:
        print()
        print("⏭️  Configuration skipped. Current setup:")
        print("   - Using test data mode")
        print("   - APIM key placeholder: 'your-apim-subscription-key-here'")
        print()
        print("🔍 How to get your APIM subscription key:")
        print("1. Contact LaTrobe University IT team")
        print("2. Access LaTrobe API Management portal")
        print("3. Navigate to 'Subscriptions' section")
        print("4. Copy the primary or secondary key")
        print()
        print("📖 Alternative testing:")
        print("   - Current test mode shows the integration works")
        print("   - Function processes through Microsoft PubSec-IA pipeline")
        print("   - Replace APIM key when available for real data")

if __name__ == "__main__":
    main()
