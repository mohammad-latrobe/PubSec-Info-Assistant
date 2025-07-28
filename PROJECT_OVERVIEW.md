# PubSec Information Assistant - Project Structure & Quick Start

## 🚀 Quick Start

This repository has been reorganized with a modern, scalable architecture using Terraform Infrastructure as Code. 

### 📁 New Project Structure

```
PubSec-Info-Assistant/
├── 🏗️ infrastructure/              # Terraform Infrastructure as Code
│   ├── modules/                    # Reusable Terraform modules
│   ├── environments/              # Environment-specific configurations
│   └── scripts/                   # Deployment automation scripts
├── 🚀 src/                        # Application source code
│   ├── functions/                 # Azure Functions (Python 3.10)
│   ├── api/                       # REST API endpoints (future)
│   └── shared/                    # Shared libraries and utilities
├── 📋 tests/                      # Test suites
├── 📚 docs/                       # Documentation
├── 🔧 scripts/                    # Legacy utility scripts
└── 📄 simplified_functions/       # Legacy simplified implementation
```

## 🎯 Two Deployment Options

### Option 1: Modern Terraform Infrastructure (Recommended)

**Benefits**: Environment management, state tracking, modular design, CI/CD ready

1. **Prerequisites**:
   ```powershell
   # Install Terraform
   winget install HashiCorp.Terraform
   
   # Install Azure CLI (if not already installed)
   winget install Microsoft.AzureCLI
   
   # Authenticate
   az login
   ```

2. **Deploy Infrastructure**:
   ```powershell
   # Navigate to development environment
   cd infrastructure\environments\dev
   
   # Create configuration from example
   Copy-Item terraform.tfvars.example terraform.tfvars
   
   # Edit terraform.tfvars with your values:
   # - resource_group_name = "rg-pubsec-ia-dev"
   # - location = "East US"  
   # - apim_subscription_key = "d1d001e93d6c4698bc954ec2426da2ad"
   
   # Deploy infrastructure
   ..\..\..\infrastructure\scripts\deploy-infrastructure.ps1 -Environment dev
   ```

3. **Deploy Functions**:
   ```powershell
   # Deploy function code to the created infrastructure
   .\infrastructure\scripts\deploy-functions.ps1 -Environment dev
   ```

### Option 2: Simplified PowerShell Deployment (Legacy)

**Benefits**: Quick setup, minimal prerequisites

```powershell
cd simplified_functions
.\deploy.ps1 -ResourceGroupName "rg-pubsec-ia-simple" -Location "East US"
```

## 🔧 Technology Stack

- **Infrastructure**: Terraform with Azure Provider
- **Compute**: Azure Functions (Python 3.10)
- **Search**: Azure AI Search (S0 tier with vector capabilities)
- **AI**: Azure OpenAI Service (text-embedding-ada-002)
- **Storage**: Azure Blob Storage
- **Monitoring**: Application Insights
- **Security**: Managed Identity, RBAC

## 📊 Key Features

### LTU API Integration
- Fetches Knowledge Base articles from LTU API
- Processes and chunks content for optimal search
- Stores processed data in Azure Blob Storage

### Vector Search Capabilities
- Azure AI Search with S0 tier
- Vector embeddings for semantic search
- Security filtering for access control
- Hybrid search (vector + keyword)

### Scalable Architecture
- Modular Terraform infrastructure
- Environment separation (dev/staging/prod)
- Automated deployment scripts
- CI/CD pipeline ready

## 🔐 Security & Compliance

- **Managed Identity**: No hardcoded secrets or connection strings
- **RBAC**: Fine-grained role assignments between services
- **HTTPS Only**: All communication encrypted in transit
- **Network Security**: Configurable public/private access
- **Secrets Management**: Azure Key Vault integration ready

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: High-level system design
- **[infrastructure/README.md](infrastructure/README.md)**: Terraform infrastructure guide
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**: Migration from legacy deployment
- **[simplified_functions/DEPLOYMENT_GUIDE.md](simplified_functions/DEPLOYMENT_GUIDE.md)**: Legacy deployment guide

## 🧪 Testing

After deployment, test your functions:

1. **Test LTU API Integration**:
   ```powershell
   # Get function URL from Terraform output
   terraform output process_kb_articles_url
   
   # Test the function
   Invoke-RestMethod -Uri "https://your-function-app.azurewebsites.net/api/ProcessKBArticles" -Method GET
   ```

2. **Test Search Indexing**:
   ```powershell
   # Test indexing function
   Invoke-RestMethod -Uri "https://your-function-app.azurewebsites.net/api/IndexKBChunks" -Method POST
   ```

3. **Verify in Azure Portal**:
   - Check Function App logs
   - Verify Search Index contents
   - Monitor Application Insights

## 🔄 Migration from Legacy

If you have existing resources from the simplified PowerShell deployment, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for step-by-step migration instructions.

## 💰 Cost Optimization

### Development Environment
- **Azure Functions**: Consumption plan (pay-per-execution)
- **Azure AI Search**: S0 tier (standard pricing)
- **Azure OpenAI**: Pay-per-token usage
- **Storage**: Standard LRS (lowest cost)

### Production Considerations
- Reserved instances for predictable workloads
- Premium search tier for higher SLA
- Private endpoints for enhanced security
- Multi-region deployment for disaster recovery

## 🆘 Troubleshooting

### Common Issues

1. **Terraform State Conflicts**:
   ```powershell
   terraform force-unlock <lock-id>
   ```

2. **Resource Name Conflicts**:
   - Update `project_prefix` in terraform.tfvars
   - Use different environment names

3. **Function Deployment Fails**:
   - Check Python version compatibility
   - Verify function app is running
   - Check Application Insights logs

4. **API Authentication Errors**:
   - Verify APIM subscription key
   - Check network connectivity to LTU API

### Getting Help

1. Check the relevant documentation in `/docs`
2. Review Azure Portal for resource status
3. Check Application Insights for detailed error logs
4. Create an issue in the repository with:
   - Error messages
   - Deployment environment details
   - Steps to reproduce

## 🎯 Next Steps

1. **Customize Configuration**: Update terraform.tfvars for your environment
2. **Deploy Infrastructure**: Use Terraform deployment scripts
3. **Test Functions**: Verify LTU API integration works
4. **Monitor Performance**: Set up alerts and monitoring
5. **Scale Up**: Move to production-ready configuration
6. **Extend Functionality**: Add additional knowledge base sources

## 📞 Support

For questions or issues:
- Check documentation first
- Review existing GitHub issues
- Create new issue with detailed information
- Contact the development team

---

**🔧 Built with modern DevOps practices • 🛡️ Security-first design • 📈 Production-ready scaling**
