# Deploying CT-5 Platform to Render.com

This guide provides instructions for deploying the CT-5 platform to Render.com.

## Prerequisites

- A Render.com account
- Your GitHub repository connected to Render

## Deployment Steps

### 1. Deploy using the Blueprint (Recommended)

The easiest way to deploy is using the Render Blueprint defined in `render.yaml`:

1. Log in to your Render dashboard
2. Click on "Blueprints" in the sidebar
3. Click "New Blueprint Instance"
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file and set up the services
6. Review the configuration and click "Apply"

This will create:
- A PostgreSQL database
- A web service for the backend

### 2. Manual Deployment

If you prefer to set up services manually:

#### Create a PostgreSQL Database

1. In your Render dashboard, click "New" and select "PostgreSQL"
2. Configure your database:
   - Name: ct5-db
   - Database: ct5_db
   - User: ct5_user
   - Choose a plan (Free tier is available)
3. Click "Create Database"
4. Note the connection details provided by Render

#### Deploy the Backend Web Service

1. In your Render dashboard, click "New" and select "Web Service"
2. Connect your GitHub repository
3. Configure the web service:
   - Name: ct5-backend
   - Environment: Python
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the following environment variables:
   - `DB_HOST`: Your Render PostgreSQL host
   - `DB_PORT`: Your Render PostgreSQL port
   - `DB_NAME`: ct5_db
   - `DB_USER`: Your Render PostgreSQL user
   - `DB_PASSWORD`: Your Render PostgreSQL password
   - `JWT_SECRET`: Generate a secure random string
   - `JWT_ALGORITHM`: HS256
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
   - `API_HOST`: 0.0.0.0
   - `API_PORT`: $PORT
   - `FRONTEND_URL`: Your frontend URL (if deployed)
5. Click "Create Web Service"

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check the logs in your Render dashboard
2. Verify that the database environment variables are correctly set
3. Ensure your database is running and accessible
4. Check if your IP is allowed to connect to the database (Render databases allow connections from Render services by default)

### Application Errors

For application errors:

1. Check the logs in your Render dashboard
2. Use the "Shell" feature in Render to access your service and run diagnostic commands
3. Verify that all required environment variables are set correctly

## Frontend Deployment

For the frontend, we recommend deploying to Vercel:

1. Follow the instructions in `VERCEL_DEPLOYMENT.md`
2. Make sure to set the `NEXT_PUBLIC_API_URL` to your Render backend URL
