# PubSec Information Assistant - Deployment and Testing Guide

## Overview
This guide covers deploying and testing the simplified PubSec Information Assistant implementation with LTU API integration.

## Prerequisites

Before deployment, ensure you have:

1. **Azure CLI** installed and authenticated
2. **PowerShell** with Azure PowerShell module
3. **Azure subscription** with appropriate permissions
4. **LTU API access** with subscription key: `d1d001e93d6c4698bc954ec2426da2ad`

## Step 1: Deploy Infrastructure

1. Navigate to the project directory:
   ```powershell
   cd "c:\local_codes\PubSec-Info-Assistant\simplified_functions"
   ```

2. Run the deployment script:
   ```powershell
   .\deploy.ps1
   ```

3. When prompted, provide:
   - Resource group name (e.g., `rg-pubsec-ia-dev`)
   - Location (e.g., `eastus`)
   - Unique prefix for resources (e.g., `pubsecia123`)

4. The script will create:
   - Azure Function App
   - Azure AI Search service (S0 tier)
   - Azure OpenAI service
   - Azure Storage account
   - All necessary permissions and configurations

## Step 2: Deploy Function Code

After infrastructure deployment:

1. **Get the Function App name** from the deployment output
2. **Deploy the function code**:
   ```powershell
   # Navigate to function directory
   cd "c:\local_codes\PubSec-Info-Assistant\simplified_functions"
   
   # Create deployment package
   Compress-Archive -Path "ProcessKBArticles", "IndexKBChunks", "host.json", "requirements.txt" -DestinationPath "functions.zip" -Force
   
   # Deploy using Azure CLI
   az functionapp deployment source config-zip --resource-group "rg-pubsec-ia-dev" --name "func-your-app-name" --src "functions.zip"
   ```

3. **Wait for deployment** (usually 2-3 minutes)

## Step 3: Configure Environment Variables

The deployment script sets most variables, but verify these are configured:

```powershell
# Get your Function App name
$functionAppName = "func-pubsec-ia-123"  # Replace with actual name
$resourceGroupName = "rg-pubsec-ia-dev"  # Replace with actual name

# Check LTU API configuration
az functionapp config appsettings list --name $functionAppName --resource-group $resourceGroupName --query "[?name=='KNOWLEDGE_BASE_API_URL']"
az functionapp config appsettings list --name $functionAppName --resource-group $resourceGroupName --query "[?name=='APIM_SUBSCRIPTION_KEY']"
```

## Step 4: Test the Functions

### Option A: Use Azure Portal

1. Go to **Azure Portal** → **Function Apps** → **Your Function App**
2. Navigate to **Functions** → **ProcessKBArticles**
3. Click **Code + Test** → **Test/Run**
4. Use HTTP GET method (no body needed)
5. Click **Run** and check the output

### Option B: Use PowerShell Testing

1. **Get the function URL and key**:
   ```powershell
   # Get function key
   $functionKey = az functionapp keys list --name $functionAppName --resource-group $resourceGroupName --query "functionKeys.default" -o tsv
   
   # Get function URL
   $functionUrl = "https://$functionAppName.azurewebsites.net/api/ProcessKBArticles"
   
   # Test the function
   $headers = @{"x-functions-key" = $functionKey}
   $response = Invoke-RestMethod -Uri $functionUrl -Method GET -Headers $headers
   $response | ConvertTo-Json -Depth 10
   ```

### Option C: Use Python Test Script

1. **Install Python dependencies**:
   ```powershell
   pip install requests
   ```

2. **Update the test script**:
   ```python
   # Edit test_ltu_api.py
   PROCESS_KB_FUNCTION_URL = "https://your-actual-function-app.azurewebsites.net/api/ProcessKBArticles"
   INDEX_KB_FUNCTION_URL = "https://your-actual-function-app.azurewebsites.net/api/IndexKBChunks"
   FUNCTION_KEY = "your-actual-function-key"
   ```

3. **Run the tests**:
   ```powershell
   python test_ltu_api.py
   ```

## Step 5: Monitor and Verify

### Check Function Logs

1. **In Azure Portal**:
   - Go to Function App → Monitor → Application Insights
   - Check real-time logs and metrics

2. **Using Azure CLI**:
   ```powershell
   # Stream logs
   az webapp log tail --name $functionAppName --resource-group $resourceGroupName
   ```

### Verify Blob Storage

1. **Check content container**:
   ```powershell
   # List blobs in content container
   az storage blob list --account-name "st$uniquePrefix" --container-name "content" --output table
   ```

### Verify Search Index

1. **Check search index**:
   ```powershell
   # Get search service info
   $searchServiceName = "search-$uniquePrefix"
   
   # Check if index exists
   az search index list --service-name $searchServiceName --resource-group $resourceGroupName
   ```

## Troubleshooting

### Common Issues

1. **API Authentication Errors**
   - Verify APIM subscription key is correct
   - Check if API endpoint is accessible

2. **Function Timeout**
   - Increase function timeout in host.json
   - Process fewer articles per batch

3. **Search Service Errors**
   - Verify search service is running
   - Check search service key configuration

4. **Blob Storage Errors**
   - Verify storage account permissions
   - Check managed identity assignments

### Debug Steps

1. **Check Function App Configuration**:
   ```powershell
   az functionapp config appsettings list --name $functionAppName --resource-group $resourceGroupName
   ```

2. **Test LTU API Direct**:
   ```powershell
   # Test API connectivity
   $headers = @{
       "Ocp-Apim-Subscription-Key" = "d1d001e93d6c4698bc954ec2426da2ad"
       "Cookie" = "saplb_*=(J2EE7865220)7865251"
   }
   
   $apiUrl = "https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase?Name=ICT&Active=true&Status_IN=published"
   
   try {
       $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers -Method GET
       Write-Host "✅ API connection successful: $($response.Count) articles found"
   }
   catch {
       Write-Host "❌ API connection failed: $($_.Exception.Message)"
   }
   ```

3. **Check Managed Identity**:
   ```powershell
   # Verify managed identity has correct permissions
   az role assignment list --assignee $(az functionapp identity show --name $functionAppName --resource-group $resourceGroupName --query principalId -o tsv)
   ```

## Expected Results

After successful deployment and testing:

1. **ProcessKBArticles Function**:
   - Fetches articles from LTU API
   - Creates chunked JSON files in blob storage
   - Returns processing summary
   - Runs on Python 3.10 runtime

2. **IndexKBChunks Function**:
   - Reads chunks from blob storage
   - Generates embeddings using Azure OpenAI
   - Indexes content in Azure AI Search
   - Runs on Python 3.10 runtime

3. **Search Index**:
   - Contains searchable KB articles
   - Includes security filtering capabilities
   - Supports vector and keyword search

## Next Steps

1. **Set up Monitoring**: Configure alerts for function failures
2. **Implement Scheduling**: Use Azure Logic Apps or Timer triggers for automatic updates
3. **Add Frontend**: Create search interface using the indexed content
4. **Scale Resources**: Adjust pricing tiers based on usage
5. **Security Review**: Implement additional security measures as needed

## Support

For issues or questions:
1. Check Azure Function App logs
2. Review Application Insights telemetry
3. Validate API connectivity and permissions
4. Test with smaller data sets first
