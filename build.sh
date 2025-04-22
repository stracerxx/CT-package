#!/bin/bash

# This script prepares the application for deployment to Render.com

echo "Preparing CT-5 Platform for deployment to Render.com..."

# Create a requirements.txt file in the root directory
echo "Creating root requirements.txt file..."
echo "-r backend/requirements.txt" > requirements.txt

# Create Procfile for Render
echo "Creating Procfile..."
echo "web: cd backend && python init_db.py && uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Ensure render.yaml exists
if [ ! -f render.yaml ]; then
    echo "Creating render.yaml file..."
    cat > render.yaml << 'EOF'
services:
  # Backend web service
  - type: web
    name: ct5-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python init_db.py && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DB_HOST
        fromDatabase:
          name: ct5-db
          property: host
      - key: DB_PORT
        fromDatabase:
          name: ct5-db
          property: port
      - key: DB_NAME
        fromDatabase:
          name: ct5-db
          property: database
      - key: DB_USER
        fromDatabase:
          name: ct5-db
          property: user
      - key: DB_PASSWORD
        fromDatabase:
          name: ct5-db
          property: password
      - key: JWT_SECRET
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: 30
      - key: API_HOST
        value: 0.0.0.0
      - key: API_PORT
        value: $PORT
      - key: FRONTEND_URL
        value: https://ct5-frontend.vercel.app # Update this with your frontend URL

databases:
  - name: ct5-db
    databaseName: ct5_db
    user: ct5_user
    plan: free # Use the appropriate plan for your needs
EOF
fi

echo "Deployment preparation complete!"
echo ""
echo "To deploy to Render.com:"
echo "1. Commit these changes to your repository"
echo "2. Push to GitHub"
echo "3. Connect your repository to Render.com"
echo "4. Create a new Blueprint instance using the render.yaml file"
echo ""
echo "For more detailed instructions, see RENDER_DEPLOYMENT.md"
