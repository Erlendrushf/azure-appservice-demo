# Azure App Service Troubleshooting Guide

## Common Issues and Solutions

### 1. Application Error / Container Didn't Respond

**Symptoms:**
- "Application Error" message in browser
- Container crash or timeout errors in logs

**Solutions:**

#### A. Check Startup Command
The most common issue is an incorrect startup command. Ensure it's set correctly:

```bash
# Via Azure CLI
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120"
```

Or in Azure Portal:
- Configuration > General Settings > Startup Command
- Enter: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120`

#### B. Verify Requirements.txt
Make sure `gunicorn` is in your `requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-multipart==0.0.6
gunicorn==23.0.0
```

#### C. Check Python Version
Ensure your Azure App Service Python version matches your requirements:
```bash
az webapp config show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query linuxFxVersion
```

Should return: `PYTHON|3.11`

If not, update it:
```bash
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --linux-fx-version "PYTHON|3.11"
```

#### D. Enable Application Logs
```bash
# Enable application logging
az webapp log config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging filesystem \
  --level information

# Stream logs
az webapp log tail \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

#### E. Check for Import Errors
View the deployment and container logs:
```bash
# Deployment logs
az webapp log deployment show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# Download all logs
az webapp log download \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --log-file app-logs.zip
```

### 2. Module Not Found Errors

**Cause:** Dependencies not installed correctly - Azure Oryx build system not enabled

**Solution:**
```bash
# THIS IS THE MOST IMPORTANT FIX!
# Enable Oryx build system to install dependencies
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Restart the app to trigger reinstallation
az webapp restart \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# Or redeploy via GitHub Actions (now includes this setting)
```

**Explanation:** Azure App Service uses Oryx to build Python apps and install dependencies from requirements.txt. If `SCM_DO_BUILD_DURING_DEPLOYMENT` is not set to `true`, Azure won't run `pip install -r requirements.txt`, causing "ModuleNotFoundError" for uvicorn and other packages.

### 3. Container Timeout Issues

**Symptoms:**
- Container startup timeout
- "Didn't respond in time" errors

**Solutions:**

#### Increase Timeout
```bash
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 300"
```

#### Reduce Workers
If your plan has limited resources, reduce workers:
```bash
# Use 2 workers instead of 4 for Basic tier
--startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120"
```

### 4. Port Binding Issues

**Cause:** App not listening on the correct port

**Verification:**
Azure App Service expects your app on port **8000** by default for Python apps.

Ensure your startup command has `--bind 0.0.0.0:8000`

### 5. Deployment Successful but App Not Working

**Steps to diagnose:**

1. **Check app state:**
```bash
az webapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query state
```

2. **View recent logs:**
```bash
az webapp log tail \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

3. **Test locally with Azure's setup:**
```bash
# Activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test with gunicorn (same as Azure)
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

4. **Check for file permissions:**
```bash
# Ensure main.py is readable
ls -la main.py
```

### 6. CORS Issues

If your frontend can't access the API:

The app already includes CORS middleware in `main.py`, but you can customize it:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7. Environment Variables Not Loading

Set environment variables in Azure:

```bash
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings KEY=VALUE
```

Or in Portal: Configuration > Application settings

### 8. GitHub Actions Deployment Failing

**Check these:**

1. **Verify GitHub Secrets are set:**
   - AZURE_CLIENT_ID
   - AZURE_TENANT_ID
   - AZURE_SUBSCRIPTION_ID

2. **Check service principal permissions:**
```bash
az role assignment list \
  --assignee $APP_ID \
  --output table
```

3. **Verify federated credentials:**
```bash
az ad app federated-credential list \
  --id $APP_ID \
  --output table
```

4. **Check workflow syntax:**
```bash
# In your repo root
cat .github/workflows/azure-deploy.yml
```

### 9. SSL/HTTPS Issues

Azure App Service provides free SSL by default. Ensure you're accessing via HTTPS:

```bash
# Get your app URL
az webapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query defaultHostName \
  --output tsv
```

Access: `https://<your-app-name>.azurewebsites.net`

### 10. Performance Issues

**Solutions:**

1. **Scale up (better hardware):**
```bash
az appservice plan update \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --sku S1
```

2. **Scale out (more instances):**
```bash
az appservice plan update \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --number-of-workers 2
```

3. **Enable Application Insights:**
```bash
az monitor app-insights component create \
  --app "${APP_NAME}-insights" \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP
```

## Quick Diagnostic Commands

```bash
# Get everything in one go
echo "=== App State ==="
az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query state

echo "=== Python Version ==="
az webapp config show --name $APP_NAME --resource-group $RESOURCE_GROUP --query linuxFxVersion

echo "=== Startup Command ==="
az webapp config show --name $APP_NAME --resource-group $RESOURCE_GROUP --query appCommandLine

echo "=== Recent Logs ==="
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --timeout 30
```

## Testing Endpoints After Fix

```bash
APP_URL="https://${APP_NAME}.azurewebsites.net"

# Health check
curl $APP_URL/health

# Swagger docs
curl $APP_URL/swagger

# Root endpoint
curl $APP_URL/

# Test API endpoint
curl $APP_URL/api/quotes/random
```

## Still Having Issues?

1. Download complete logs:
```bash
az webapp log download \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --log-file debug-logs.zip
```

2. Enable more verbose logging:
```bash
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings LOG_LEVEL=DEBUG
```

3. Use Azure Portal:
   - Go to your App Service
   - Navigate to "Diagnose and solve problems"
   - Check "Availability and Performance"

4. Check Azure Service Health:
   - Ensure there are no Azure region outages

## Useful Links

- [Azure App Service Linux Python docs](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
