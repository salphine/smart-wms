# Smart WMS Frontend - Streamlit Cloud Configuration
# This file tells Streamlit Cloud how to deploy the app

[app]
entryPoint = "frontend/app_cloud.py"

[[apps.env]]
key = "BACKEND_URL"
value = "https://your-railway-backend.railway.app"
