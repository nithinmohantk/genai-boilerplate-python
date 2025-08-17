# Docker Deployment Guide

This guide provides comprehensive instructions for deploying the GenAI Chatbot application using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **System Resources**: 
  - Minimum: 4GB RAM, 2 CPU cores, 20GB disk space
  - Recommended: 8GB RAM, 4 CPU cores, 50GB disk space

### Installing Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS
```bash
brew install docker docker-compose
```

#### Windows
Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nithinmohantk/genai-boilerplate-python.git
   cd genai-boilerplate-python
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**:
   ```bash
   # Development
   docker-compose up -d
   
   # Production
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_DB=genai_chatbot
POSTGRES_USER=genai_user
POSTGRES_PASSWORD=your_secure_database_password

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password

# Application Secrets
SECRET_KEY=your_super_secret_key_here
JWT_SECRET=your_jwt_secret_here

# AI API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Application URLs
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Optional Monitoring
GRAFANA_PASSWORD=admin123

# Production specific
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
HTTP_PORT=80
HTTPS_PORT=443
```

### Environment-specific Files

- **Development**: `.env` or `docker-compose.yml`
- **Production**: `.env.prod` with `docker-compose.prod.yml`
- **Testing**: `.env.test`

## Development Deployment

### Standard Development Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

### Development with Live Reload

The development setup includes volume mounts for live code reloading:

```yaml
volumes:
  - ./backend:/app      # Backend live reload
  - ./frontend:/app     # Frontend live reload
  - /app/node_modules   # Prevent node_modules override
```

### Development Commands

```bash
# View service status
docker-compose ps

# Execute commands in containers
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm install new-package

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

## Production Deployment

### Production Configuration

```bash
# Create production environment
cp .env.example .env.prod
# Configure production values

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Or with specific environment file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Production Features

- **Multi-stage Docker builds** for optimized images
- **Non-root users** for security
- **Resource limits** and constraints
- **Health checks** and monitoring
- **Automated restarts** and recovery
- **Logging** configuration
- **Nginx reverse proxy** with SSL
- **Prometheus/Grafana** monitoring

### SSL/TLS Configuration

1. **Generate SSL certificates**:
   ```bash
   mkdir -p deployments/nginx/ssl
   
   # Self-signed for development
   openssl req -x509 -newkey rsa:4096 -keyout deployments/nginx/ssl/tls.key \
     -out deployments/nginx/ssl/tls.crt -days 365 -nodes
   
   # Or use Let's Encrypt with Certbot
   certbot certonly --standalone -d your-domain.com
   cp /etc/letsencrypt/live/your-domain.com/* deployments/nginx/ssl/
   ```

2. **Update nginx configuration** in `docker-compose.prod.yml`

### Scaling Services

```bash
# Scale backend horizontally
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale specific services
docker-compose -f docker-compose.prod.yml up -d \
  --scale backend=3 \
  --scale frontend=2
```

## Monitoring and Logging

### Access Monitoring Dashboards

- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service with timestamps
docker-compose logs -f -t backend

# Filter logs
docker-compose logs backend | grep ERROR

# Export logs
docker-compose logs --no-color > application.log
```

### Log Management

Production deployment includes:
- **JSON structured logging**
- **Log rotation** (10MB max, 5 files)
- **Centralized log collection**
- **Log analysis** with Grafana

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :8000
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U genai_user

# Reset database
docker-compose down -v  # WARNING: Deletes data
docker-compose up -d
```

#### 3. Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER data/
sudo chmod -R 755 data/
```

#### 4. Container Health Check Failures
```bash
# Check container health
docker-compose ps
docker inspect <container_name> | grep Health -A 20

# Manual health check
docker-compose exec backend curl -f http://localhost:8000/health
```

### Debugging

```bash
# Enter container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Run commands in container
docker-compose exec backend python -c "import sys; print(sys.path)"

# Debug with container logs
docker-compose logs backend --tail=100 -f
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Check container processes
docker-compose exec backend top

# Database performance
docker-compose exec postgres psql -U genai_user -d genai_chatbot -c "
  SELECT query, state, query_start 
  FROM pg_stat_activity 
  WHERE state != 'idle';"
```

## Security Considerations

### Container Security

1. **Non-root users**: All containers run as non-privileged users
2. **Read-only filesystems**: Where possible
3. **Capability dropping**: Remove unnecessary Linux capabilities
4. **Security scanning**: Automated vulnerability scans in CI/CD
5. **Resource limits**: Prevent resource exhaustion attacks

### Network Security

```yaml
networks:
  backend-network:
    driver: bridge
    internal: true  # Backend services isolated
  frontend-network:
    driver: bridge  # Frontend accessible via reverse proxy
```

### Secrets Management

```bash
# Use Docker secrets for production
echo "super_secret_password" | docker secret create postgres_password -

# Or use external secret management
export POSTGRES_PASSWORD=$(vault kv get -field=password secret/postgres)
```

### Security Best Practices

1. **Regular updates**: Keep base images updated
2. **Minimal images**: Use alpine or distroless images
3. **Secret rotation**: Regularly rotate passwords and keys
4. **Access control**: Limit container privileges
5. **Monitoring**: Log security events and anomalies

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U genai_user genai_chatbot > backup.sql

# Automated daily backup
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"
docker-compose exec -T postgres pg_dump -U genai_user genai_chatbot > "$BACKUP_DIR/database.sql"
docker-compose exec -T redis redis-cli --rdb "$BACKUP_DIR/dump.rdb"
EOF

chmod +x backup.sh
# Add to cron: 0 2 * * * /path/to/backup.sh
```

### Data Recovery

```bash
# Stop services
docker-compose down

# Restore database
docker-compose up -d postgres
docker-compose exec -T postgres psql -U genai_user genai_chatbot < backup.sql

# Restore Redis
docker-compose up -d redis
docker cp dump.rdb $(docker-compose ps -q redis):/data/

# Start all services
docker-compose up -d
```

### Volume Backup

```bash
# Backup all volumes
docker run --rm -v genai-boilerplate-python_postgres_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .

# Restore volume
docker run --rm -v genai-boilerplate-python_postgres_data:/data \
  -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
```

## Maintenance

### Regular Maintenance Tasks

```bash
# Update images
docker-compose pull
docker-compose up -d

# Clean unused resources
docker system prune -f
docker volume prune -f

# Update containers
docker-compose down
docker-compose pull
docker-compose up -d --force-recreate
```

### Health Monitoring

Set up automated health checks and alerting:

```bash
# Health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
for service in backend frontend postgres redis; do
  if ! docker-compose ps $service | grep -q "healthy\|Up"; then
    echo "Service $service is unhealthy"
    # Send alert (email, Slack, etc.)
  fi
done
EOF
```

### Performance Tuning

1. **Database**: Adjust PostgreSQL configuration for your workload
2. **Redis**: Configure memory limits and eviction policies  
3. **Application**: Tune worker processes and connection pools
4. **Nginx**: Optimize caching and compression settings

---

For more information, see:
- [Kubernetes Deployment Guide](./KUBERNETES_DEPLOYMENT.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Security Guide](./SECURITY.md)
