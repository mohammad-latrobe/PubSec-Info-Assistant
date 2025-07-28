# Migration Guide: From PowerShell Scripts to Terraform

This guide helps you migrate from the simplified PowerShell deployment to the new Terraform-based infrastructure.

## 🔄 Migration Overview

### What's Changing
- **From**: PowerShell scripts with Azure CLI commands
- **To**: Terraform Infrastructure as Code with modular design
- **Benefits**: Better state management, reusable modules, environment consistency

### New Project Structure
```
PubSec-Info-Assistant/
├── infrastructure/           # New Terraform infrastructure
│   ├── modules/             # Reusable components
│   ├── environments/        # Environment-specific configs
│   └── scripts/            # Deployment scripts
├── src/                     # Application source code
│   └── functions/          # Moved from simplified_functions/
├── tests/                   # Test suites
└── docs/                   # Documentation
```

## 📋 Migration Steps

### Step 1: Backup Current Resources (Optional)

If you have existing resources from the PowerShell deployment:

```powershell
# List current resources
az resource list --resource-group "rg-pubsec-ia-dev" --output table

# Export resource configurations (optional)
az group export --name "rg-pubsec-ia-dev" --include-comments --include-parameter-default-value > backup-resources.json
```

### Step 2: Clean Up Old Resources (If Needed)

If you want to start fresh:

```powershell
# Warning: This will delete all resources in the resource group
az group delete --name "rg-pubsec-ia-dev" --yes --no-wait
```

### Step 3: Set Up Terraform Environment

1. **Install Prerequisites**:
   ```powershell
   # Install Terraform
   winget install HashiCorp.Terraform
   
   # Verify installation
   terraform version
   ```

2. **Navigate to new structure**:
   ```powershell
   cd infrastructure\environments\dev
   ```

3. **Create configuration**:
   ```powershell
   Copy-Item terraform.tfvars.example terraform.tfvars
   
   # Edit terraform.tfvars with your values:
   # - resource_group_name
   # - location
   # - apim_subscription_key
   ```

### Step 4: Deploy New Infrastructure

```powershell
# Using the deployment script
..\..\..\infrastructure\scripts\deploy-infrastructure.ps1 -Environment dev

# Or manually
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

### Step 5: Deploy Function Code

```powershell
# Deploy functions to new infrastructure
.\infrastructure\scripts\deploy-functions.ps1 -Environment dev
```

### Step 6: Test Migration

1. **Test function endpoints**:
   ```powershell
   # Get function URLs from Terraform output
   terraform output function_app_hostname
   
   # Test ProcessKBArticles
   $functionUrl = "https://your-function-app.azurewebsites.net/api/ProcessKBArticles"
   Invoke-RestMethod -Uri $functionUrl -Method GET
   ```

2. **Verify search index**:
   - Check Azure Portal for search service
   - Verify index schema matches requirements

## 🔄 Import Existing Resources (Alternative)

If you want to keep existing resources and manage them with Terraform:

### Step 1: Import Resources

```powershell
# Import resource group
terraform import azurerm_resource_group.main /subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP_NAME

# Import storage account
terraform import module.storage.azurerm_storage_account.main /subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP_NAME/providers/Microsoft.Storage/storageAccounts/STORAGE_ACCOUNT_NAME

# Import function app
terraform import module.azure_functions.azurerm_linux_function_app.main /subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP_NAME/providers/Microsoft.Web/sites/FUNCTION_APP_NAME

# Import search service
terraform import module.ai_search.azurerm_search_service.main /subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP_NAME/providers/Microsoft.Search/searchServices/SEARCH_SERVICE_NAME

# Import OpenAI service
terraform import module.openai.azurerm_cognitive_account.openai /subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP_NAME/providers/Microsoft.CognitiveServices/accounts/OPENAI_SERVICE_NAME
```

### Step 2: Align Configuration

Update `terraform.tfvars` to match your existing resource names and configurations.

### Step 3: Plan and Verify

```powershell
terraform plan
# Should show no changes if configuration matches existing resources
```

## 📊 Configuration Mapping

### PowerShell Script → Terraform Variables

| PowerShell Variable | Terraform Variable | Description |
|-------------------|-------------------|-------------|
| `$ResourceGroupName` | `resource_group_name` | Resource group name |
| `$Location` | `location` | Azure region |
| `$ProjectPrefix` | `project_prefix` | Resource naming prefix |
| `APIM_SUBSCRIPTION_KEY` | `apim_subscription_key` | LTU API key |
| `KNOWLEDGE_BASE_API_URL` | `knowledge_base_api_url` | API endpoint |

### Resource Name Changes

| Resource Type | PowerShell Pattern | Terraform Pattern |
|--------------|-------------------|------------------|
| Storage Account | `${ProjectPrefix}storage${uniqueSuffix}` | `${project_prefix}st${random_suffix}` |
| Function App | `${ProjectPrefix}-functions-${uniqueSuffix}` | `${project_prefix}-func-${environment}-${random_suffix}` |
| Search Service | `${ProjectPrefix}-search-${uniqueSuffix}` | `${project_prefix}-search-${environment}-${random_suffix}` |
| OpenAI Service | `${ProjectPrefix}-openai-${uniqueSuffix}` | `${project_prefix}-openai-${environment}-${random_suffix}` |

## 🔍 Verification Checklist

After migration, verify:

- [ ] All Azure resources are deployed and healthy
- [ ] Function app has correct environment variables
- [ ] Search index exists with proper schema
- [ ] OpenAI model deployment is active
- [ ] Storage containers are created
- [ ] Role assignments are in place
- [ ] Functions can access all required services
- [ ] LTU API integration works
- [ ] Test scripts run successfully

## 🐛 Troubleshooting Migration

### Common Issues

1. **Resource Name Conflicts**:
   ```
   Error: A resource with the ID already exists
   ```
   **Solution**: Update `project_prefix` or manually clean up conflicting resources

2. **Permission Errors**:
   ```
   Error: insufficient privileges to complete the operation
   ```
   **Solution**: Verify Azure subscription permissions and role assignments

3. **State File Issues**:
   ```
   Error: Resource already managed by Terraform
   ```
   **Solution**: Use `terraform import` or remove from state with `terraform state rm`

4. **Function Deployment Fails**:
   ```
   Error: Deployment package could not be deployed
   ```
   **Solution**: Check function app is running and has correct runtime version

### Recovery Steps

If migration fails:

1. **Check Terraform state**:
   ```powershell
   terraform state list
   terraform state show <resource_name>
   ```

2. **Review Azure Portal** for partial deployments

3. **Use Terraform refresh**:
   ```powershell
   terraform refresh
   ```

4. **Start over if needed**:
   ```powershell
   # Remove state file and start fresh
   Remove-Item terraform.tfstate*
   terraform init
   ```

## 📞 Getting Help

If you encounter issues during migration:

1. Check the Terraform documentation
2. Review Azure provider documentation
3. Check existing GitHub issues
4. Create a new issue with:
   - Migration step where you encountered the issue
   - Full error message
   - Your environment configuration (sanitized)
   - Steps to reproduce

## 🎯 Post-Migration Benefits

After successful migration:

- **Infrastructure as Code**: Version-controlled infrastructure
- **Environment Consistency**: Identical dev/staging/prod environments
- **Modular Design**: Reusable components for future projects
- **State Management**: Proper tracking of resource dependencies
- **Team Collaboration**: Shared infrastructure definitions
- **Automated Deployments**: CI/CD ready infrastructure
