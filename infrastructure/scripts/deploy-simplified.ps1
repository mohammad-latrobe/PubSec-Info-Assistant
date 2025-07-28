# Deployment Script for PubSec Information Assistant - Steps 1 & 2
# This script creates the required Azure resources for the simplified implementation

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location,
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectPrefix = "pubsec-ia"
)

# Set subscription if provided
if ($SubscriptionId) {
    az account set --subscription $SubscriptionId
}

Write-Host "Starting deployment of PubSec Information Assistant simplified version..." -ForegroundColor Green

# Generate unique names
$timestamp = Get-Date -Format "yyyyMMddHHmm"
$uniqueSuffix = (Get-Random -Minimum 1000 -Maximum 9999)
$storageAccountName = "${ProjectPrefix}storage${uniqueSuffix}".Replace("-", "").ToLower()
$functionAppName = "${ProjectPrefix}-functions-${uniqueSuffix}"
$searchServiceName = "${ProjectPrefix}-search-${uniqueSuffix}"
$openAIServiceName = "${ProjectPrefix}-openai-${uniqueSuffix}"
$appServicePlanName = "${ProjectPrefix}-plan-${uniqueSuffix}"

Write-Host "Using resource names:" -ForegroundColor Yellow
Write-Host "  Storage Account: $storageAccountName" -ForegroundColor Cyan
Write-Host "  Function App: $functionAppName" -ForegroundColor Cyan
Write-Host "  Search Service: $searchServiceName" -ForegroundColor Cyan
Write-Host "  OpenAI Service: $openAIServiceName" -ForegroundColor Cyan

# Create Resource Group
Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create Storage Account
Write-Host "Creating storage account: $storageAccountName" -ForegroundColor Yellow
az storage account create `
    --name $storageAccountName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2

# Create containers
Write-Host "Creating storage containers..." -ForegroundColor Yellow
$storageKey = az storage account keys list --resource-group $ResourceGroupName --account-name $storageAccountName --query '[0].value' -o tsv

az storage container create --name "content" --account-name $storageAccountName --account-key $storageKey
az storage container create --name "upload" --account-name $storageAccountName --account-key $storageKey
az storage container create --name "logs" --account-name $storageAccountName --account-key $storageKey

# Create Azure AI Search Service (S0 tier as requested)
Write-Host "Creating Azure AI Search service: $searchServiceName" -ForegroundColor Yellow
az search service create `
    --name $searchServiceName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku S0 `
    --replica-count 1 `
    --partition-count 1

# Create Azure OpenAI Service
Write-Host "Creating Azure OpenAI service: $openAIServiceName" -ForegroundColor Yellow
az cognitiveservices account create `
    --name $openAIServiceName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --kind OpenAI `
    --sku S0

# Deploy text-embedding-ada-002 model
Write-Host "Deploying text-embedding-ada-002 model..." -ForegroundColor Yellow
az cognitiveservices account deployment create `
    --name $openAIServiceName `
    --resource-group $ResourceGroupName `
    --deployment-name "text-embedding-ada-002" `
    --model-name "text-embedding-ada-002" `
    --model-version "2" `
    --model-format OpenAI `
    --sku-capacity 120 `
    --sku-name "Standard"

# Create App Service Plan for Functions
Write-Host "Creating App Service Plan: $appServicePlanName" -ForegroundColor Yellow
az appservice plan create `
    --name $appServicePlanName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku S1 `
    --is-linux

# Create Function App
Write-Host "Creating Function App: $functionAppName" -ForegroundColor Yellow
az functionapp create `
    --name $functionAppName `
    --resource-group $ResourceGroupName `
    --consumption-plan-location $Location `
    --runtime python `
    --runtime-version 3.11 `
    --functions-version 4 `
    --storage-account $storageAccountName

# Enable system managed identity for Function App
Write-Host "Enabling managed identity for Function App..." -ForegroundColor Yellow
az functionapp identity assign --name $functionAppName --resource-group $ResourceGroupName

# Get Function App principal ID
$functionPrincipalId = az functionapp identity show --name $functionAppName --resource-group $ResourceGroupName --query principalId -o tsv

# Assign permissions to Function App
Write-Host "Assigning permissions to Function App..." -ForegroundColor Yellow

# Storage permissions
az role assignment create --assignee $functionPrincipalId --role "Storage Blob Data Contributor" --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$ResourceGroupName/providers/Microsoft.Storage/storageAccounts/$storageAccountName"

# Search permissions  
az role assignment create --assignee $functionPrincipalId --role "Search Index Data Contributor" --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$ResourceGroupName/providers/Microsoft.Search/searchServices/$searchServiceName"

# OpenAI permissions
az role assignment create --assignee $functionPrincipalId --role "Cognitive Services OpenAI User" --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$ResourceGroupName/providers/Microsoft.CognitiveServices/accounts/$openAIServiceName"

# Get service endpoints
$storageEndpoint = az storage account show --name $storageAccountName --resource-group $ResourceGroupName --query primaryEndpoints.blob -o tsv
$searchEndpoint = "https://$searchServiceName.search.windows.net"
$openAIEndpoint = az cognitiveservices account show --name $openAIServiceName --resource-group $ResourceGroupName --query properties.endpoint -o tsv

# Configure Function App settings
Write-Host "Configuring Function App settings..." -ForegroundColor Yellow
az functionapp config appsettings set --name $functionAppName --resource-group $ResourceGroupName --settings `
    "BLOB_STORAGE_ACCOUNT_ENDPOINT=$storageEndpoint" `
    "BLOB_STORAGE_ACCOUNT_OUTPUT_CONTAINER_NAME=content" `
    "BLOB_CONTENT_CONTAINER_NAME=content" `
    "AZURE_QUEUE_STORAGE_ENDPOINT=$storageEndpoint" `
    "NON_PDF_SUBMIT_QUEUE=non-pdf-submit-queue" `
    "AZURE_OPENAI_AUTHORITY_HOST=AzurePublicCloud" `
    "AZURE_SEARCH_SERVICE_ENDPOINT=$searchEndpoint" `
    "AZURE_SEARCH_INDEX=kb-articles-index" `
    "AZURE_OPENAI_ENDPOINT=$openAIEndpoint" `
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002" `
    "CHUNK_TARGET_SIZE=750" `
    "EMBEDDING_VECTOR_SIZE=1536" `
    "LOCAL_DEBUG=false" `
    "KNOWLEDGE_BASE_API_URL=https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase" `
    "APIM_SUBSCRIPTION_KEY=d1d001e93d6c4698bc954ec2426da2ad" `
    "KB_NAME_FILTER=ICT" `
    "KB_ACTIVE_FILTER=true" `
    "KB_STATUS_FILTER=published"

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Resource Information:" -ForegroundColor Yellow
Write-Host "  Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "  Storage Account: $storageAccountName" -ForegroundColor Cyan
Write-Host "  Storage Endpoint: $storageEndpoint" -ForegroundColor Cyan
Write-Host "  Function App: $functionAppName" -ForegroundColor Cyan
Write-Host "  Search Service: $searchServiceName (S0)" -ForegroundColor Cyan
Write-Host "  Search Endpoint: $searchEndpoint" -ForegroundColor Cyan
Write-Host "  OpenAI Service: $openAIServiceName" -ForegroundColor Cyan
Write-Host "  OpenAI Endpoint: $openAIEndpoint" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Deploy the function code to the Function App" -ForegroundColor White
Write-Host "2. Run the create_search_index.py script to create the search index" -ForegroundColor White
Write-Host "3. Test the ProcessKBArticles function with sample data" -ForegroundColor White
Write-Host "4. Test the IndexKBChunks function to index the data" -ForegroundColor White
