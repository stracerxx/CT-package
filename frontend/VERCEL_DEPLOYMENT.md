# Deploying CT-5 Frontend to Vercel

This guide provides instructions for deploying the CT-5 frontend to Vercel.

## Prerequisites

- A Vercel account (sign up at https://vercel.com)
- Your backend API deployed and accessible via a public URL
- Git repository with your CT-5 code

## Deployment Steps

### 1. Update the Vercel Configuration

Edit the `vercel.json` file in the frontend directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-api-url.com/api/:path*"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend-api-url.com"
  }
}
```

Replace `https://your-backend-api-url.com` with the actual URL of your deployed backend API.

### 2. Deploy to Vercel

#### Option 1: Deploy via Vercel Dashboard

1. Go to https://vercel.com and log in
2. Click "Add New..." and select "Project"
3. Import your Git repository
4. Configure the project:
   - Set the Framework Preset to "Next.js"
   - Set the Root Directory to "frontend"
   - Add environment variables:
     - `NEXT_PUBLIC_API_URL`: Your backend API URL
5. Click "Deploy"

#### Option 2: Deploy via Vercel CLI

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Log in to Vercel:
   ```bash
   vercel login
   ```

4. Deploy to Vercel:
   ```bash
   vercel
   ```

5. Follow the prompts to configure your project

### 3. Configure Environment Variables

In the Vercel dashboard:

1. Go to your project
2. Click on "Settings"
3. Go to "Environment Variables"
4. Add the following variables:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL

### 4. Verify the Deployment

1. Once deployed, Vercel will provide you with a URL for your application
2. Visit the URL to ensure your frontend is working correctly
3. Test the connection to your backend API

## Troubleshooting

### CORS Issues

If you encounter CORS issues, make sure your backend API allows requests from your Vercel domain:

```python
# In your FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Issues

If your frontend can't connect to your backend API:

1. Check that the `NEXT_PUBLIC_API_URL` environment variable is set correctly
2. Ensure your backend API is accessible from the internet
3. Verify that the API endpoints are working correctly

### Build Errors

If you encounter build errors:

1. Check the build logs in the Vercel dashboard
2. Ensure all dependencies are correctly specified in `package.json`
3. Verify that your Next.js configuration is compatible with Vercel

## Important Notes

- Vercel deployments are primarily for the frontend. You'll need to deploy your backend separately.
- Consider using a service like Heroku, AWS, or Digital Ocean for your backend API.
- Make sure your backend API is secured properly when exposed to the internet.
- Set up proper authentication and authorization for your API endpoints.
