# Quick Reference - Azure App Service Demo

## ✅ Local Testing Confirmed Working

The application has been tested locally and works perfectly:
- ✅ FastAPI application starts successfully
- ✅ All endpoints respond correctly
- ✅ Gunicorn with Uvicorn workers runs properly
- ✅ Swagger documentation loads at `/swagger`

## 🔧 Key Fixes Applied

### 1. **Updated requirements.txt**
Added `gunicorn==23.0.0` which is required for Azure App Service.

### 2. **Updated startup.txt**
Changed to use `$PORT` environment variable for flexibility.

### 3. **Created startup.sh**
A more robust startup script with proper logging and timeout settings.

### 4. **Python Version**
Set to 3.11 (stable and well-supported) instead of 3.14.

## 🚀 Deploy to Fix Azure

### Quick Fix Commands

If your app is already deployed but showing errors:

```bash
# Set your variables
APP_NAME="apiopsdemoapp"
RESOURCE_GROUP="p-swe-rg-backend"

# 1. Update the startup command
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --timeout 120"

# 2. Ensure Python version is correct
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --linux-fx-version "PYTHON|3.11"

# 3. Restart the app
az webapp restart \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# 4. View logs to confirm
az webapp log tail \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### Or Redeploy via GitHub Actions

1. Commit the changes:
```bash
git add .
git commit -m "Fix Azure deployment - add gunicorn, update startup command"
git push origin main
```

2. Monitor deployment in GitHub Actions

3. Test endpoints:
```bash
curl https://apiopsdemoapp.azurewebsites.net/health
curl https://apiopsdemoapp.azurewebsites.net/swagger
```

## 📊 Testing Locally

```bash
# Start the app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8080

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/api/quotes/random
curl http://localhost:8080/api/weather/Oslo

# Open Swagger UI
open http://localhost:8080/swagger
```

## 🔍 Common Issues

### Issue: "Application Error"
**Solution:** Update startup command (see Quick Fix Commands above)

### Issue: "Container didn't respond"
**Solution:** 
- Check startup command includes `--timeout 120`
- Reduce workers from 4 to 2 if using Basic tier
- Ensure gunicorn is in requirements.txt

### Issue: "Module not found"
**Solution:** Restart app to reinstall dependencies:
```bash
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
```

## 📁 Files Modified

- ✅ `requirements.txt` - Added gunicorn
- ✅ `startup.txt` - Updated with $PORT variable
- ✅ `startup.sh` - New robust startup script
- ✅ `.github/workflows/azure-deploy.yml` - Python 3.11
- ✅ `SETUP.md` - Updated startup command
- ✅ `TROUBLESHOOTING.md` - Complete troubleshooting guide

## 🎯 Expected Results After Fix

Once deployed with these fixes:

1. **App Status:** Running ✅
2. **Health Check:** `https://apiopsdemoapp.azurewebsites.net/health` → Returns JSON
3. **Swagger UI:** `https://apiopsdemoapp.azurewebsites.net/swagger` → Interactive docs
4. **API Endpoints:** All working (quotes, weather, tasks, etc.)

## 📞 Need More Help?

See `TROUBLESHOOTING.md` for detailed diagnostics and solutions.
