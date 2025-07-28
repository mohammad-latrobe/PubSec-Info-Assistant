# Infrastructure Deployment Script for PubSec Information Assistant
# This script deploys the Terraform infrastructure for the specified environment

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$Plan,
    
    [Parameter(Mandatory=$false)]
    [switch]$Destroy,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipValidation
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-ColoredOutput "Checking prerequisites..." "Yellow"
    
    # Check if Terraform is installed
    try {
        $terraformVersion = terraform version
        Write-ColoredOutput "✅ Terraform found: $($terraformVersion[0])" "Green"
    }
    catch {
        Write-ColoredOutput "❌ Terraform not found. Please install Terraform first." "Red"
        Write-ColoredOutput "Install using: winget install HashiCorp.Terraform" "Cyan"
        exit 1
    }
    
    # Check if Azure CLI is installed and authenticated
    try {
        $azAccount = az account show --query "name" -o tsv 2>$null
        if ($azAccount) {
            Write-ColoredOutput "✅ Azure CLI authenticated as: $azAccount" "Green"
        } else {
            Write-ColoredOutput "❌ Azure CLI not authenticated. Please run 'az login'" "Red"
            exit 1
        }
    }
    catch {
        Write-ColoredOutput "❌ Azure CLI not found or not authenticated" "Red"
        exit 1
    }
}

# Main deployment function
function Deploy-Infrastructure {
    param(
        [string]$Env,
        [bool]$PlanOnly = $false,
        [bool]$DestroyMode = $false
    )
    
    $envPath = Join-Path $PSScriptRoot "..\environments\$Env"
    
    if (!(Test-Path $envPath)) {
        Write-ColoredOutput "❌ Environment directory not found: $envPath" "Red"
        exit 1
    }
    
    # Change to environment directory
    Push-Location $envPath
    
    try {
        Write-ColoredOutput "🚀 Starting Terraform deployment for environment: $Env" "Green"
        Write-ColoredOutput "Working directory: $envPath" "Cyan"
        
        # Check if terraform.tfvars exists
        if (!(Test-Path "terraform.tfvars")) {
            Write-ColoredOutput "⚠️  terraform.tfvars not found. Creating from example..." "Yellow"
            if (Test-Path "terraform.tfvars.example") {
                Copy-Item "terraform.tfvars.example" "terraform.tfvars"
                Write-ColoredOutput "📝 Please edit terraform.tfvars with your specific values before continuing." "Yellow"
                Write-ColoredOutput "Press any key to continue once you've updated terraform.tfvars..." "Yellow"
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
        }
        
        # Initialize Terraform
        Write-ColoredOutput "📦 Initializing Terraform..." "Yellow"
        terraform init
        if ($LASTEXITCODE -ne 0) {
            throw "Terraform init failed"
        }
        
        # Validate configuration (unless skipped)
        if (!$SkipValidation) {
            Write-ColoredOutput "🔍 Validating Terraform configuration..." "Yellow"
            terraform validate
            if ($LASTEXITCODE -ne 0) {
                throw "Terraform validation failed"
            }
            Write-ColoredOutput "✅ Terraform configuration is valid" "Green"
        }
        
        if ($DestroyMode) {
            # Destroy infrastructure
            Write-ColoredOutput "💥 Destroying infrastructure..." "Red"
            terraform destroy -auto-approve
            if ($LASTEXITCODE -ne 0) {
                throw "Terraform destroy failed"
            }
            Write-ColoredOutput "✅ Infrastructure destroyed successfully" "Green"
        }
        elseif ($PlanOnly) {
            # Plan only
            Write-ColoredOutput "📋 Creating Terraform plan..." "Yellow"
            terraform plan -out="tfplan"
            if ($LASTEXITCODE -ne 0) {
                throw "Terraform plan failed"
            }
            Write-ColoredOutput "✅ Terraform plan created successfully" "Green"
            Write-ColoredOutput "💡 Run with -Plan:$false to apply the plan" "Cyan"
        }
        else {
            # Plan and apply
            Write-ColoredOutput "📋 Creating Terraform plan..." "Yellow"
            terraform plan -out="tfplan"
            if ($LASTEXITCODE -ne 0) {
                throw "Terraform plan failed"
            }
            
            Write-ColoredOutput "🚀 Applying Terraform configuration..." "Yellow"
            terraform apply -auto-approve "tfplan"
            if ($LASTEXITCODE -ne 0) {
                throw "Terraform apply failed"
            }
            
            Write-ColoredOutput "✅ Infrastructure deployed successfully!" "Green"
            
            # Show outputs
            Write-ColoredOutput "📊 Deployment outputs:" "Yellow"
            terraform output
            
            # Generate Azure Portal links
            $resourceGroupName = terraform output -raw resource_group_name
            $subscriptionId = az account show --query id -o tsv
            
            Write-ColoredOutput "" "White"
            Write-ColoredOutput "🌐 Azure Portal Links:" "Yellow"
            Write-ColoredOutput "Resource Group: https://portal.azure.com/#@/resource/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName" "Cyan"
            
            # Clean up plan file
            if (Test-Path "tfplan") {
                Remove-Item "tfplan"
            }
        }
        
    }
    catch {
        Write-ColoredOutput "❌ Deployment failed: $($_.Exception.Message)" "Red"
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Main script execution
Write-ColoredOutput "🏗️  PubSec Information Assistant - Infrastructure Deployment" "Green"
Write-ColoredOutput "Environment: $Environment" "Cyan"

# Set subscription if provided
if ($SubscriptionId) {
    Write-ColoredOutput "Setting Azure subscription: $SubscriptionId" "Yellow"
    az account set --subscription $SubscriptionId
    if ($LASTEXITCODE -ne 0) {
        Write-ColoredOutput "❌ Failed to set subscription" "Red"
        exit 1
    }
}

# Check prerequisites
Test-Prerequisites

# Deploy infrastructure
Deploy-Infrastructure -Env $Environment -PlanOnly $Plan -DestroyMode $Destroy

Write-ColoredOutput "" "White"
Write-ColoredOutput "🎉 Deployment script completed successfully!" "Green"
Write-ColoredOutput "" "White"
Write-ColoredOutput "Next steps:" "Yellow"
Write-ColoredOutput "1. Deploy the Azure Functions code using: .\deploy-functions.ps1 -Environment $Environment" "White"
Write-ColoredOutput "2. Test the functions using the test scripts" "White"
Write-ColoredOutput "3. Monitor the deployment in Azure Portal" "White"
