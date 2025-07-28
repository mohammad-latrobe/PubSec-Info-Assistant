# Azure Functions Deployment Script for PubSec Information Assistant
# This script deploys the function code to an existing Function App

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [switch]$BuildOnly
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

# Function to get Terraform outputs
function Get-TerraformOutputs {
    param([string]$EnvPath)
    
    if (!(Test-Path "$EnvPath\terraform.tfstate")) {
        Write-ColoredOutput "❌ Terraform state not found. Please deploy infrastructure first." "Red"
        exit 1
    }
    
    Push-Location $EnvPath
    try {
        $outputs = @{}
        $outputs.functionAppName = terraform output -raw function_app_name
        $outputs.resourceGroupName = terraform output -raw resource_group_name
        return $outputs
    }
    catch {
        Write-ColoredOutput "❌ Failed to read Terraform outputs: $($_.Exception.Message)" "Red"
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Main deployment function
function Invoke-FunctionDeployment {
    param(
        [string]$Env,
        [string]$AppName,
        [string]$ResourceGroup,
        [bool]$BuildOnlyMode = $false
    )
    
    $projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
    $functionsPath = Join-Path $projectRoot "src\functions"
    $tempPath = Join-Path $env:TEMP "pubsec-ia-functions-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    if (!(Test-Path $functionsPath)) {
        Write-ColoredOutput "❌ Functions directory not found: $functionsPath" "Red"
        exit 1
    }
    
    try {
        Write-ColoredOutput "📦 Preparing function package..." "Yellow"
        
        # Create temporary directory
        New-Item -ItemType Directory -Path $tempPath -Force | Out-Null
        
        # Copy function files
        Copy-Item -Path "$functionsPath\*" -Destination $tempPath -Recurse -Force
        
        # Create deployment package
        $packagePath = Join-Path $env:TEMP "functions-$Env-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"
        
        Write-ColoredOutput "📋 Creating deployment package..." "Yellow"
        Compress-Archive -Path "$tempPath\*" -DestinationPath $packagePath -Force
        
        Write-ColoredOutput "✅ Package created: $packagePath" "Green"
        
        if ($BuildOnlyMode) {
            Write-ColoredOutput "🏗️  Build completed. Package ready for deployment: $packagePath" "Green"
            return
        }
        
        # Deploy to Azure Functions
        Write-ColoredOutput "🚀 Deploying to Azure Function App: $AppName" "Yellow"
        
        az functionapp deployment source config-zip `
            --resource-group $ResourceGroup `
            --name $AppName `
            --src $packagePath
            
        if ($LASTEXITCODE -ne 0) {
            throw "Function deployment failed"
        }
        
        Write-ColoredOutput "✅ Functions deployed successfully!" "Green"
        
        # Wait for deployment to complete
        Write-ColoredOutput "⏳ Waiting for deployment to complete..." "Yellow"
        Start-Sleep -Seconds 30
        
        # Test function endpoints
        Write-ColoredOutput "🔍 Testing function endpoints..." "Yellow"
        
        $hostname = az functionapp show --name $AppName --resource-group $ResourceGroup --query "defaultHostName" -o tsv
        
        if ($hostname) {
            Write-ColoredOutput "Function App URLs:" "Cyan"
            Write-ColoredOutput "  ProcessKBArticles: https://$hostname/api/ProcessKBArticles" "White"
            Write-ColoredOutput "  IndexKBChunks: https://$hostname/api/IndexKBChunks" "White"
        }
        
    }
    catch {
        Write-ColoredOutput "❌ Deployment failed: $($_.Exception.Message)" "Red"
        exit 1
    }
    finally {
        # Clean up temporary files
        if (Test-Path $tempPath) {
            Remove-Item -Path $tempPath -Recurse -Force
        }
        if (Test-Path $packagePath) {
            Remove-Item -Path $packagePath -Force
        }
    }
}

# Main script execution
Write-ColoredOutput "🚀 PubSec Information Assistant - Functions Deployment" "Green"
Write-ColoredOutput "Environment: $Environment" "Cyan"

# Get Terraform outputs if function app name not provided
if (!$FunctionAppName -or !$ResourceGroupName) {
    $envPath = Join-Path $PSScriptRoot "..\environments\$Environment"
    
    if (!(Test-Path $envPath)) {
        Write-ColoredOutput "❌ Environment directory not found: $envPath" "Red"
        exit 1
    }
    
    Write-ColoredOutput "📊 Reading deployment information from Terraform..." "Yellow"
    $terraformOutputs = Get-TerraformOutputs -EnvPath $envPath
    
    if (!$FunctionAppName) {
        $FunctionAppName = $terraformOutputs.functionAppName
    }
    
    if (!$ResourceGroupName) {
        $ResourceGroupName = $terraformOutputs.resourceGroupName
    }
}

Write-ColoredOutput "Target Function App: $FunctionAppName" "Cyan"
Write-ColoredOutput "Resource Group: $ResourceGroupName" "Cyan"

# Check if Azure CLI is authenticated
try {
    $azAccount = az account show --query "name" -o tsv 2>$null
    if (!$azAccount) {
        Write-ColoredOutput "❌ Azure CLI not authenticated. Please run 'az login'" "Red"
        exit 1
    }
    Write-ColoredOutput "✅ Azure CLI authenticated as: $azAccount" "Green"
}
catch {
    Write-ColoredOutput "❌ Azure CLI not found or not authenticated" "Red"
    exit 1
}

# Deploy functions
Invoke-FunctionDeployment -Env $Environment -AppName $FunctionAppName -ResourceGroup $ResourceGroupName -BuildOnlyMode $BuildOnly

Write-ColoredOutput "" "White"
Write-ColoredOutput "🎉 Function deployment completed successfully!" "Green"
Write-ColoredOutput "" "White"
Write-ColoredOutput "Next steps:" "Yellow"
Write-ColoredOutput "1. Test the functions using the test scripts in the tests directory" "White"
Write-ColoredOutput "2. Monitor function logs in Azure Portal" "White"
Write-ColoredOutput "3. Check Application Insights for telemetry data" "White"
