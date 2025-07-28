# PubSec Information Assistant - Step-by-Step Implementation Guide

This directory contains a simplified implementation of the Microsoft PubSec Information Assistant for step-by-step testing and learning.

## Overview

This implementation focuses on the first two critical steps:

1. **Azure Function to Process KB Articles** - Fetch and store JSONs for Knowledge Base articles in Azure Blob Storage
2. **Azure AI Search Service Setup** - Create S0 tier search service with security filtering and document indexing

## Key Features Implemented

- ✅ Document chunking using the same 750-token strategy as full PubSec-IA
- ✅ No overlapping chunks (section-based chunking maintains context)
- ✅ Azure AI Search with S0 SKU (as requested)
- ✅ Security column for access control and filtering
- ✅ Integration with unstructured.io processing patterns
- ✅ Managed Identity authentication (no hardcoded keys)
- ✅ Embedding generation using Azure OpenAI

## Architecture

```
KB Articles → ProcessKBArticles Function → Blob Storage (JSON chunks) → IndexKBChunks Function → Azure AI Search (S0)
```

### Security Model

The implementation includes a comprehensive security model with these fields:
- `security_groups`: Array of groups that can access the document
- `access_level`: public, internal, confidential, restricted
- `department`: Department classification
- `classification`: Security classification level

## Prerequisites

Before starting, ensure you have:

1. **Azure Subscription** with appropriate permissions
2. **Azure CLI** installed and logged in
3. **PowerShell** (for deployment script)
4. **Python 3.11** (for local testing)
5. **VS Code with Azure Functions extension** (optional, for development)

## Step-by-Step Implementation

### Step 1: Deploy Azure Infrastructure

1. **Clone and navigate to the simplified functions directory:**
   ```bash
   cd simplified_functions
   ```

2. **Run the deployment script:**
   ```powershell
   .\deploy.ps1 -ResourceGroupName "rg-pubsec-ia-test" -Location "East US"
   ```

   This creates:
   - Storage Account with containers (content, upload, logs)
   - Azure AI Search Service (S0 SKU)
   - Azure OpenAI Service with text-embedding-ada-002 deployment
   - Function App with managed identity
   - Proper role assignments

### Step 2: Create Search Index

1. **Set environment variables:**
   ```bash
   export AZURE_SEARCH_SERVICE_ENDPOINT="https://your-search-service.search.windows.net"
   export AZURE_SEARCH_INDEX="kb-articles-index"
   export EMBEDDING_VECTOR_SIZE="1536"
   ```

2. **Run the index creation script:**
   ```bash
   python create_search_index.py
   ```

   This creates an Azure AI Search index with:
   - Vector search capabilities
   - Security filtering fields
   - Semantic search configuration
   - Proper field mappings

### Step 3: Deploy Function Code

1. **Package and deploy the functions:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Deploy to Azure (replace with your function app name)
   func azure functionapp publish your-function-app-name --python
   ```

2. **Verify deployment:**
   - Check Azure portal for successful deployment
   - Verify environment variables are set correctly
   - Test function endpoints

### Step 4: Test the Implementation

1. **Update test configuration:**
   - Edit `test_functions.py`
   - Replace `your-function-app` with your actual function app name
   - Replace `your-function-key` with the actual function key from Azure portal

2. **Run tests:**
   ```bash
   python test_functions.py
   ```

   This will:
   - Send sample KB articles to the ProcessKBArticles function
   - Verify chunks are created and stored in blob storage
   - Index the chunks into Azure AI Search
   - Provide success/failure feedback

### Step 5: Verify Results

1. **Check Blob Storage:**
   - Navigate to your storage account in Azure portal
   - Look in the `content` container
   - Verify JSON chunk files are created

2. **Check Azure AI Search:**
   - Navigate to your search service in Azure portal
   - Use Search Explorer to query the index
   - Verify documents are indexed with proper security fields

## File Structure

```
simplified_functions/
├── ProcessKBArticles/          # Function to process KB articles
│   ├── __init__.py            # Main function code
│   └── function.json          # Function binding configuration
├── IndexKBChunks/             # Function to index chunks to search
│   ├── __init__.py            # Main function code
│   └── function.json          # Function binding configuration
├── requirements.txt           # Python dependencies
├── host.json                  # Function app configuration
├── create_search_index.py     # Script to create search index
├── deploy.ps1                 # Infrastructure deployment script
├── test_functions.py          # Test script with sample data
└── README.md                  # This file
```

## Key Implementation Details

### Chunking Strategy

Following the PubSec-IA approach:
- **Target size**: 750 tokens per chunk
- **No overlap**: Maintains semantic coherence within sections
- **Sentence boundaries**: Text is split on sentence boundaries when needed
- **Metadata preservation**: Each chunk includes title, section, and metadata

### Security Implementation

Each document chunk includes security metadata:
```json
{
  "security_groups": ["employees", "contractors"],
  "access_level": "internal",
  "department": "all_departments", 
  "classification": "internal"
}
```

### Search Index Schema

The search index includes:
- **Content fields**: content, title, section, subtitle
- **Vector field**: content_vector (1536 dimensions for Ada-002)
- **Security fields**: security_groups, access_level, department, classification
- **Metadata fields**: processed_datetime, chunk_number, token_count

## Testing with Sample Data

The test script includes three sample articles:

1. **Employee Handbook** (Internal) - General employee information
2. **IT Security Policy** (Confidential) - Security procedures and requirements
3. **Travel Policy** (Public) - Travel and expense guidelines

Each article demonstrates different security classifications and content types.

## Next Steps

After successfully completing these steps:

1. **Implement Search Function** - Create a function to search the indexed content
2. **Add User Authentication** - Implement user context for security filtering
3. **Expand Document Types** - Add support for PDF and other file types
4. **Implement RAG Pattern** - Create chat functionality with document grounding
5. **Add Monitoring** - Implement logging and monitoring capabilities

## Troubleshooting

### Common Issues:

1. **Function deployment fails:**
   - Check Python version (must be 3.11)
   - Verify Azure CLI is logged in
   - Check resource group permissions

2. **Search index creation fails:**
   - Verify search service is in S0 tier
   - Check managed identity permissions
   - Ensure endpoint URLs are correct

3. **Embedding generation fails:**
   - Verify OpenAI service deployment
   - Check model deployment name
   - Verify managed identity has OpenAI User role

4. **Test script fails:**
   - Update function URLs and keys
   - Check function app is running
   - Verify network connectivity

### Checking Logs:

```bash
# View function logs
func azure functionapp logstream your-function-app-name

# Or check in Azure portal under Function App > Logs
```

## Security Considerations

This implementation uses Azure best practices:

- ✅ Managed Identity for all Azure service authentication
- ✅ No hardcoded credentials in code
- ✅ Role-based access control (RBAC)
- ✅ Secure communication between services
- ✅ Document-level security filtering

## Cost Optimization

For testing and development:
- Search service S0 tier: ~$250/month
- Function App consumption plan: Pay per execution
- Storage account: ~$20/month for moderate usage
- OpenAI embedding calls: ~$0.0001 per 1K tokens

## Resources

- [Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Azure Functions Python Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure OpenAI Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [PubSec Information Assistant GitHub](https://github.com/microsoft/PubSec-Info-Assistant)

---

**Note**: This is a simplified implementation for learning and testing. For production use, consider implementing the full PubSec Information Assistant solution with additional features like web UI, advanced security, monitoring, and scale considerations.
