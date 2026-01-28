# Azure Deployment Setup Guide

This guide walks you through setting up Azure App Registration with Federated Credentials for GitHub Actions deployment.

## Prerequisites

- Azure CLI installed and authenticated
- Azure subscription with appropriate permissions
- GitHub repository created

## Step 1: Set Variables

```bash
# Set your variables
APP_NAME="<your-app-service-name>"
RESOURCE_GROUP="<your-resource-group>"
LOCATION="westeurope"  # or your preferred location
GITHUB_ORG="<your-github-username-or-org>"
GITHUB_REPO="<your-repo-name>"
APP_REGISTRATION_NAME="${APP_NAME}-github-deploy"
```

## Step 2: Create Resource Group (if needed)

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

## Step 3: Create App Service Plan

```bash
az appservice plan create \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux
```

## Step 4: Create Web App

```bash
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan "${APP_NAME}-plan" \
  --runtime "PYTHON:3.11"
```

## Step 5: Configure Web App Startup Command

```bash
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120"
```

Alternatively, you can set it in the Azure Portal:
- Go to your App Service > Configuration > General settings
- Set Startup Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120`

## Step 6: Create App Registration

```bash
# Create the app registration
APP_ID=$(az ad app create \
  --display-name $APP_REGISTRATION_NAME \
  --query appId \
  --output tsv)

echo "App Registration ID: $APP_ID"

# Create a service principal
az ad sp create --id $APP_ID
```

## Step 7: Get Your Subscription and Tenant IDs

```bash
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
TENANT_ID=$(az account show --query tenantId --output tsv)

echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Tenant ID: $TENANT_ID"
```

## Step 8: Assign Contributor Role to the App Registration

```bash
# Get the webapp resource ID
WEBAPP_ID=$(az webapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

# Assign Contributor role at the web app scope
az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope $WEBAPP_ID
```

## Step 9: Create Federated Credential for GitHub Actions

```bash
# For main branch deployments
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-deploy-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'$GITHUB_ORG'/'$GITHUB_REPO':ref:refs/heads/main",
    "description": "GitHub Actions deployment from main branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Optional: For pull request deployments (if you want to deploy PRs to staging slots)
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-deploy-pr",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'$GITHUB_ORG'/'$GITHUB_REPO':pull_request",
    "description": "GitHub Actions deployment from pull requests",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

## Step 10: Configure GitHub Secrets

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions > New repository secret):

1. **AZURE_CLIENT_ID**: `$APP_ID` (from step 6)
2. **AZURE_TENANT_ID**: `$TENANT_ID` (from step 7)
3. **AZURE_SUBSCRIPTION_ID**: `$SUBSCRIPTION_ID` (from step 7)

```bash
# Print the values you need to add to GitHub
echo "=== Add these secrets to GitHub ==="
echo "AZURE_CLIENT_ID: $APP_ID"
echo "AZURE_TENANT_ID: $TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
```

## Step 11: Update GitHub Actions Workflow

Update the `.github/workflows/azure-deploy.yml` file:

1. Replace `<YOUR_APP_NAME>` with your actual app name
2. Replace `<YOUR_RESOURCE_GROUP>` with your resource group name

## Step 12: Deploy

1. Commit and push your changes to the `main` branch
2. GitHub Actions will automatically trigger the deployment
3. Monitor the workflow in the Actions tab of your GitHub repository

## Verification

After deployment, check:

```bash
# Check app status
az webapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query state \
  --output tsv

# View logs
az webapp log tail \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# Test the endpoints
curl https://$APP_NAME.azurewebsites.net/health
curl https://$APP_NAME.azurewebsites.net/swagger
```

## Troubleshooting

### Check Role Assignments
```bash
az role assignment list \
  --assignee $APP_ID \
  --output table
```

### Verify Federated Credentials
```bash
az ad app federated-credential list \
  --id $APP_ID \
  --output table
```

### Check Web App Configuration
```bash
az webapp config show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### View Deployment Logs
```bash
az webapp log deployment show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

## Security Best Practices

1. **Least Privilege**: The service principal only has Contributor access to the specific Web App, not the entire subscription
2. **No Secrets**: No passwords or keys are stored; authentication uses OIDC tokens
3. **Scoped Credentials**: Federated credentials are scoped to specific branches/actions
4. **Automatic Rotation**: OIDC tokens are short-lived and automatically rotated

## Cleanup

To delete all resources:

```bash
# Delete the web app and app service plan
az webapp delete \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

az appservice plan delete \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --yes

# Delete the resource group (if you want to remove everything)
az group delete \
  --name $RESOURCE_GROUP \
  --yes

# Delete the app registration
az ad app delete --id $APP_ID
```

## Additional Resources

- [Azure OIDC with GitHub Actions](https://docs.microsoft.com/azure/active-directory/develop/workload-identity-federation-github)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
