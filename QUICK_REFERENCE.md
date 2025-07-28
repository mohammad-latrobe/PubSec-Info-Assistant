# 🚀 PubSec Information Assistant - Quick Reference

## ⚡ Quick Deploy Commands

### Terraform Infrastructure (Recommended)
```powershell
# 1. Setup
cd infrastructure\environments\dev
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings

# 2. Deploy Infrastructure  
..\..\..\infrastructure\scripts\deploy-infrastructure.ps1 -Environment dev

# 3. Deploy Functions
.\infrastructure\scripts\deploy-functions.ps1 -Environment dev
```

### Legacy PowerShell (Simple)
```powershell
cd simplified_functions
.\deploy.ps1 -ResourceGroupName "rg-pubsec-ia" -Location "East US"
```

## 📁 Key File Locations

| Purpose | Location | Description |
|---------|----------|-------------|
| 🏗️ **Infrastructure** | `infrastructure/environments/dev/` | Terraform configurations |
| 🚀 **Functions** | `src/functions/` | Azure Functions source code |
| 📋 **Tests** | `tests/` | Test suites and scripts |
| 📚 **Docs** | `docs/` | Documentation |
| 🔧 **Scripts** | `infrastructure/scripts/` | Deployment automation |

## 🔧 Configuration Files

| File | Purpose | Required Changes |
|------|---------|-----------------|
| `terraform.tfvars` | Terraform configuration | ✅ Update with your settings |
| `local.settings.json` | Local function development | ⚠️ Create if developing locally |
| `.env` | Environment variables | ⚠️ For local development only |

## 🌐 Service Endpoints

After deployment, your services will be available at:

| Service | URL Pattern | Example |
|---------|-------------|---------|
| **Function App** | `https://{name}.azurewebsites.net` | `https://pubsec-ia-func-dev-1234.azurewebsites.net` |
| **ProcessKBArticles** | `{function-app}/api/ProcessKBArticles` | GET request to fetch and process articles |
| **IndexKBChunks** | `{function-app}/api/IndexKBChunks` | POST request to index processed chunks |
| **Search Service** | `https://{name}.search.windows.net` | `https://pubsec-ia-search-dev-1234.search.windows.net` |

## 🔐 Required Secrets

| Secret | Where to Set | Value |
|--------|--------------|-------|
| **APIM Subscription Key** | `terraform.tfvars` | `d1d001e93d6c4698bc954ec2426da2ad` |
| **Azure Subscription** | Azure CLI | `az account set --subscription {id}` |

## 🛠️ Common Operations

### Check Deployment Status
```powershell
# Terraform status
terraform output

# Azure resources
az resource list --resource-group "rg-pubsec-ia-dev" --output table
```

### View Function Logs
```powershell
# Stream logs
az webapp log tail --name {function-app-name} --resource-group {rg-name}

# Or check Application Insights in Azure Portal
```

### Test Functions
```powershell
# Test ProcessKBArticles
$url = "https://your-function-app.azurewebsites.net/api/ProcessKBArticles"
Invoke-RestMethod -Uri $url -Method GET

# Test IndexKBChunks  
$url = "https://your-function-app.azurewebsites.net/api/IndexKBChunks"
Invoke-RestMethod -Uri $url -Method POST
```

### Update Function Code
```powershell
# Redeploy functions after code changes
.\infrastructure\scripts\deploy-functions.ps1 -Environment dev
```

## 🔄 Migration Commands

### From PowerShell to Terraform
```powershell
# 1. Backup existing (optional)
az group export --name "rg-pubsec-ia-old" > backup.json

# 2. Deploy new infrastructure
cd infrastructure\environments\dev
# ... follow Terraform deployment steps

# 3. Clean up old resources (optional)
az group delete --name "rg-pubsec-ia-old"
```

## 🆘 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| **Resource name conflicts** | Update `project_prefix` in `terraform.tfvars` |
| **Terraform locked** | `terraform force-unlock {lock-id}` |
| **Function deployment fails** | Check Python 3.10 compatibility, verify app is running |
| **API authentication error** | Verify APIM subscription key in configuration |
| **Permission errors** | Check Azure CLI authentication: `az account show` |

## 📊 Cost Monitoring

### Daily Costs (Estimated)
- **Development**: $5-15/day
- **Production**: $50-200/day (depending on usage)

### Key Cost Drivers
1. **Azure AI Search** (S0 tier): ~$250/month base
2. **Azure OpenAI**: Pay-per-token usage
3. **Azure Functions**: Consumption-based
4. **Storage**: Minimal cost for typical usage

## 📚 Documentation Links

| Topic | Link |
|-------|------|
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Infrastructure Guide** | [infrastructure/README.md](infrastructure/README.md) |
| **Migration Guide** | [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) |
| **Legacy Deployment** | [simplified_functions/DEPLOYMENT_GUIDE.md](simplified_functions/DEPLOYMENT_GUIDE.md) |
| **Project Overview** | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |

## 🎯 Environment Variables Quick Reference

### Required for Functions
```bash
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-search.search.windows.net
BLOB_STORAGE_ACCOUNT_ENDPOINT=https://yourstorage.blob.core.windows.net/
KNOWLEDGE_BASE_API_URL=https://ltu-api-test-apim.azure-api.net/collection/v1/KnowledgeBase
APIM_SUBSCRIPTION_KEY=d1d001e93d6c4698bc954ec2426da2ad
```

### Runtime Configuration
```bash
PYTHON_VERSION=3.10
CHUNK_TARGET_SIZE=750
EMBEDDING_VECTOR_SIZE=1536
```

---
**💡 Tip**: Bookmark this page for quick reference during development and deployment!
