# PubSec Information Assistant - Terraform Infrastructure

## 🏗️ Overview

This directory contains the Infrastructure as Code (IaC) implementation using Terraform for the PubSec Information Assistant project. The infrastructure is organized using modular design principles with environment-specific configurations.

## 📁 Directory Structure

```
infrastructure/
├── modules/                          # Reusable Terraform modules
│   ├── storage/                     # Azure Storage Account module
│   ├── ai-search/                   # Azure AI Search module
│   ├── openai/                      # Azure OpenAI module
│   └── azure-functions/             # Azure Functions module
│
├── environments/                     # Environment-specific configurations
│   ├── dev/                         # Development environment
│   │   ├── main.tf                  # Main configuration
│   │   ├── variables.tf             # Variable definitions
│   │   ├── outputs.tf               # Output values
│   │   ├── backend.tf               # Remote state configuration
│   │   └── terraform.tfvars.example # Example variable values
│   ├── staging/                     # Staging environment (future)
│   └── production/                  # Production environment (future)
│
└── scripts/                         # Deployment and utility scripts
    ├── deploy-infrastructure.ps1    # Infrastructure deployment script
    └── deploy-functions.ps1         # Function code deployment script
```

## 🚀 Quick Start

### Prerequisites

1. **Install Terraform**:
   ```powershell
   winget install HashiCorp.Terraform
   ```

2. **Install Azure CLI**:
   ```powershell
   winget install Microsoft.AzureCLI
   ```

3. **Authenticate with Azure**:
   ```powershell
   az login
   az account set --subscription "your-subscription-id"
   ```

### 1. Deploy Infrastructure

1. **Navigate to the environment directory**:
   ```powershell
   cd infrastructure\environments\dev
   ```

2. **Create configuration file**:
   ```powershell
   Copy-Item terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your specific values
   ```

3. **Deploy using the script**:
   ```powershell
   ..\..\..\infrastructure\scripts\deploy-infrastructure.ps1 -Environment dev
   ```

   Or manually:
   ```powershell
   terraform init
   terraform validate
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

### 2. Deploy Function Code

```powershell
.\infrastructure\scripts\deploy-functions.ps1 -Environment dev
```

## 🔧 Module Details

### Storage Module
- **Purpose**: Creates Azure Storage Account with containers for content, upload, and logs
- **Resources**: Storage Account, Blob Containers
- **Security**: HTTPS only, private access, versioning enabled

### AI Search Module
- **Purpose**: Creates Azure AI Search service with vector search capabilities
- **Resources**: Search Service, Search Index
- **Configuration**: S0 tier, vector search, semantic search

### OpenAI Module
- **Purpose**: Creates Azure OpenAI service with text embedding model
- **Resources**: Cognitive Services Account, Model Deployments
- **Models**: text-embedding-ada-002 (required), optional GPT models

### Azure Functions Module
- **Purpose**: Creates Azure Function App with consumption plan
- **Resources**: App Service Plan, Function App, Application Insights
- **Configuration**: Python 3.10, managed identity, CORS enabled

## 🔐 Security & Permissions

The infrastructure implements several security best practices:

### Managed Identity
- All services use system-assigned managed identities
- No hardcoded connection strings or keys
- Automatic role assignments between services

### Role Assignments
- **Function App → Storage**: Storage Blob Data Contributor
- **Function App → Search**: Search Index Data Contributor  
- **Function App → OpenAI**: Cognitive Services OpenAI User

### Network Security
- HTTPS-only communication
- Configurable public/private access
- CORS policies for web access

## 🌍 Environment Management

### Development Environment
- Lower-cost SKUs (consumption plan, basic search)
- Public access enabled for easy testing
- Shared resources where appropriate

### Production Environment (Future)
- Production-grade SKUs
- Private endpoints and network isolation
- Enhanced monitoring and alerting
- Multi-region deployment

## 📊 Monitoring & Observability

### Application Insights
- Automatic telemetry collection
- Function execution monitoring
- Performance metrics and alerts

### Azure Monitor
- Resource health monitoring
- Cost tracking and optimization
- Security monitoring

## 💰 Cost Optimization

### Resource Sizing
- **Development**: Consumption-based pricing
- **Production**: Reserved instances and committed use discounts

### Cost Monitoring
- Resource tagging for cost allocation
- Automated shutdown policies (dev/test)
- Regular cost reviews and optimization

## 🔄 CI/CD Integration

### GitHub Actions (Future)
- Automated infrastructure validation
- Environment promotion workflows
- Automated testing and deployment

### Pipeline Structure
1. **Validate**: Terraform validate + security scanning
2. **Plan**: Generate and review deployment plan
3. **Deploy**: Apply infrastructure changes
4. **Test**: Run integration tests
5. **Promote**: Deploy to next environment

## 🛠️ Development Workflow

### Making Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feature/infrastructure-update
   ```

2. **Make changes to modules or environments**

3. **Test locally**:
   ```powershell
   terraform plan
   ```

4. **Submit pull request** with plan output

5. **Review and merge** after approval

### Adding New Environments

1. **Copy dev environment**:
   ```powershell
   Copy-Item environments\dev environments\staging -Recurse
   ```

2. **Update configuration** in `terraform.tfvars`

3. **Deploy** using deployment script

## 📚 Additional Resources

### Terraform Best Practices
- [Official Terraform Style Guide](https://developer.hashicorp.com/terraform/language/style)
- [Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

### Azure Resources
- [Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Azure OpenAI Service Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)

## 🆘 Troubleshooting

### Common Issues

1. **Terraform State Locked**:
   ```powershell
   terraform force-unlock <lock-id>
   ```

2. **Resource Name Conflicts**:
   - Update `project_prefix` in `terraform.tfvars`
   - Use unique suffixes for resources

3. **Permission Errors**:
   - Verify Azure subscription permissions
   - Check service principal roles

4. **Resource Quota Limits**:
   - Check Azure quotas in target region
   - Request quota increases if needed

### Getting Help

- Check Azure Portal for resource status
- Review Terraform logs for detailed errors
- Use `terraform refresh` to sync state
- Validate configuration with `terraform validate`

## 📞 Support

For issues or questions:
1. Check this documentation first
2. Review Terraform and Azure documentation
3. Create an issue in the project repository
4. Contact the development team
