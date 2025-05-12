# CT-5 Platform Deployment Guide

This guide provides instructions for deploying the CT-5 platform in a production environment.

## Prerequisites

- Docker and Docker Compose installed on the server
- Git installed on the server
- A domain name (optional but recommended)
- SSL certificate (optional but recommended for production)

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/stracerxx/CT-package.git
cd CT-package
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory based on the provided `.env.example` file:

```bash
cp .env.example .env
```

Then edit the `.env` file to set your specific configuration values:

```
# Database Configuration
DB_USER=postgres
DB_PASSWORD=change_this_to_a_strong_password

# Security
# Generate a strong JWT secret with: openssl rand -hex 32
JWT_SECRET=change_this_to_a_secure_random_string_at_least_32_characters_long

# API Keys (optional)
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# URLs
FRONTEND_URL=https://your-domain.com
BASE_URL=https://your-domain.com
NEXT_PUBLIC_API_URL=https://your-domain.com/api

# Email Configuration (optional)
SMTP_SERVER=smtp.your-email-provider.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_password
EMAIL_FROM=noreply@your-domain.com
```

**Important Security Notes:**

1. Generate a strong JWT secret using the command: `openssl rand -hex 32`
2. Use strong, unique passwords for the database
3. Keep your `.env` file secure and never commit it to version control

### 3. Deploy with Docker Compose

For production deployment:

```bash
# Build and start all services in detached mode
docker-compose -f docker-compose.prod.yml up -d --build
```

This will build the Docker images and start all services in detached mode. The `--build` flag ensures that the images are rebuilt with the latest code changes.

You can monitor the deployment process with:

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Initialize the Database

The first time you deploy, you need to run the database migrations:

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5. Create an Admin User

Create an initial admin user:

```bash
docker-compose -f docker-compose.prod.yml exec backend python -m scripts.create_admin_user
```

### 6. Set Up Reverse Proxy (Optional but Recommended)

For production deployments, it's recommended to use a reverse proxy like Nginx or Traefik to handle SSL termination and routing.

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7. Monitoring and Maintenance

#### View Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View logs for a specific service
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

#### Restart Services

```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Restart a specific service
docker-compose -f docker-compose.prod.yml restart backend
```

#### Update the Application

```bash
# Pull the latest changes
git pull

# Rebuild and restart the containers
docker-compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Database Connection Issues

If the backend can't connect to the database:

1. Check if the Postgres container is running:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. Verify the database credentials in the `.env` file match those in the `docker-compose.prod.yml` file.

### Frontend Not Loading

If the frontend is not loading properly:

1. Check if the frontend container is running:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. Check the frontend logs for errors:
   ```bash
   docker-compose -f docker-compose.prod.yml logs frontend
   ```

3. Verify that the `NEXT_PUBLIC_API_URL` environment variable is set correctly.

### Backend API Not Responding

If the backend API is not responding:

1. Check if the backend container is running:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. Check the backend logs for errors:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

3. Verify that the database migrations have been applied.

### 404 NOT_FOUND Errors

If you're seeing 404 NOT_FOUND errors when accessing the application:

1. Ensure the Next.js application is properly built:
   ```bash
   docker-compose -f docker-compose.prod.yml exec frontend ls -la .next
   ```
   You should see the `.next` directory with build files.

2. Check that the environment variables are correctly set:
   ```bash
   docker-compose -f docker-compose.prod.yml exec frontend env | grep NEXT
   ```

3. Verify that the frontend container is using production mode:
   ```bash
   docker-compose -f docker-compose.prod.yml exec frontend env | grep NODE_ENV
   ```
   It should show `NODE_ENV=production`.

4. If the issue persists, try rebuilding the frontend container:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build frontend
   ```

## Security Considerations

For production deployments, ensure:

1. Strong, unique passwords for the database and JWT secret
2. SSL/TLS encryption for all traffic
3. Regular backups of the database
4. Proper firewall rules to restrict access to the server
5. Regular updates of the application and dependencies

## Backup and Restore

### Backup the Database

```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres ct5_db > backup.sql
```

### Restore the Database

```bash
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres -d ct5_db
```
