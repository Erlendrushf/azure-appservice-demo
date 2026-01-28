# Azure App Service Demo - FastAPI Application

A comprehensive FastAPI demo application showcasing various API endpoints with automatic Swagger documentation, ready for deployment to Azure App Service.

## 🚀 Features

### API Endpoints

1. **General**
   - `GET /` - Welcome message and API overview
   - `GET /health` - Health check endpoint for monitoring
   - `GET /api/stats` - Application statistics

2. **Quotes API**
   - `GET /api/quotes` - Get all quotes (with optional category filter)
   - `GET /api/quotes/random` - Get a random quote
   - `GET /api/quotes/{quote_id}` - Get a specific quote

3. **Weather API** (Mock Data)
   - `GET /api/weather/{city}` - Get weather data for a city

4. **Tasks API** (Full CRUD)
   - `GET /api/tasks` - Get all tasks (with optional completion filter)
   - `POST /api/tasks` - Create a new task
   - `GET /api/tasks/{task_id}` - Get a specific task
   - `PUT /api/tasks/{task_id}` - Update a task
   - `DELETE /api/tasks/{task_id}` - Delete a task

5. **Utilities**
   - `GET /api/random-user` - Generate a random user profile
   - `GET /api/uuid` - Generate UUIDs (1-100)

### 📚 Documentation

- **Swagger UI**: `/swagger` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative API documentation

## 🏃 Running Locally

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd azure-appservice-demo
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn main:app --reload
```

5. Access the application:
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/swagger
   - ReDoc: http://localhost:8000/redoc

## 🔧 Testing the APIs

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get random quote
curl http://localhost:8000/api/quotes/random

# Get weather
curl http://localhost:8000/api/weather/Oslo

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "This is a test"}'

# Generate UUIDs
curl http://localhost:8000/api/uuid?count=5
```

### Using Swagger UI

1. Navigate to http://localhost:8000/swagger
2. Try out any endpoint directly from the browser
3. View request/response schemas and examples

## ☁️ Deploying to Azure App Service

### Prerequisites

- Azure account with an active subscription
- Azure CLI installed and authenticated
- GitHub repository with this code
- Permissions to create App Registrations and assign roles

### Deployment via GitHub Actions (using Federated Credentials)

This project uses **OpenID Connect (OIDC)** with Azure AD for secure, password-less authentication. No secrets or publish profiles needed!

#### Quick Setup

See the detailed [SETUP.md](SETUP.md) file for complete step-by-step instructions.

#### Summary of Steps:

1. **Create Azure Resources** (App Service, Resource Group)
2. **Create App Registration** with federated credentials for GitHub
3. **Configure GitHub Secrets**:
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`
4. **Update workflow file** with your app name and resource group
5. **Push to main branch** - automatic deployment!

#### Why Federated Credentials?

- ✅ **No secrets to rotate** - uses short-lived OIDC tokens
- ✅ **More secure** - no passwords stored in GitHub
- ✅ **Least privilege** - scoped to specific resources
- ✅ **Auditable** - clear tracking of deployments

### Manual Deployment

Alternatively, deploy using Azure CLI:

```bash
az webapp up \
  --name <your-app-name> \
  --resource-group <your-resource-group> \
  --runtime "PYTHON:3.11"
```

## 🔒 Environment Variables

For production, consider adding these environment variables in Azure App Service Configuration:

- `ENVIRONMENT`: production
- `LOG_LEVEL`: info
- Any API keys or secrets your app needs

## 📊 Monitoring

- Use the `/health` endpoint for health checks
- Configure Application Insights in Azure for detailed monitoring
- View logs in Azure Portal or using Azure CLI:
  ```bash
  az webapp log tail --name <your-app-name> --resource-group <your-resource-group>
  ```

## 🛠️ Development

### Project Structure

```
azure-appservice-demo/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── startup.txt         # Azure startup command
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── .github/
    └── workflows/
        └── azure-deploy.yml  # GitHub Actions workflow
```

### Adding New Endpoints

1. Add your endpoint in `main.py`
2. Use Pydantic models for request/response validation
3. Add appropriate tags for organization in Swagger
4. Test locally before deploying

## 📝 License

This is a demo application for educational purposes.

## 🤝 Contributing

Feel free to fork this repository and submit pull requests with improvements!

## 📞 Support

For issues or questions, please open an issue in the GitHub repository.
