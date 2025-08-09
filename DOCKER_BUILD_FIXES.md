# Docker Build Fixes

This document outlines the fixes applied to resolve Docker build issues encountered during development.

## Issues Fixed

### 1. Frontend Build Issues

**Problem**: TypeScript and Vite executables not found in Docker Alpine environment, causing build failures with errors like:
- `sh: tsc: not found`
- `sh: vite: not found` 
- Rollup platform-specific dependency errors (`@rollup/rollup-linux-x64-musl` missing)

**Solution**: 
- Changed `NODE_ENV` from `production` to `development` during build stage to ensure dev dependencies are available
- Used `npm ci --include=dev --no-optional` for consistent dependency installation
- Restored original `package.json` build script with TypeScript compilation
- **Explicitly installed platform-specific Rollup binary**: `npm install --save-optional @rollup/rollup-linux-x64-musl`
- Maintained proper build stage separation in multi-stage Docker build

### 2. Frontend Nginx Configuration

**Problem**: Invalid nginx directive causing container startup failure:
```
nginx: [emerg] invalid value "must-revalidate" in /etc/nginx/nginx.conf:47
```

**Solution**: 
- Fixed `gzip_proxied` directive by removing invalid `must-revalidate` value
- Updated to use standard nginx values: `gzip_proxied expired no-cache no-store private auth;`

### 3. Backend Dependency Conflicts

**Problem**: Multiple dependency issues:
- PyTorch dependency conflicts with sentence-transformers
- Missing email-validator: `ImportError: email-validator is not installed, run 'pip install pydantic[email]'`
- Missing asyncpg: `ModuleNotFoundError: No module named 'asyncpg'`

**Solution**: 
- Added explicit PyTorch dependency: `torch>=2.0.0,<3.0.0`
- Changed pydantic to include email support: `pydantic[email]>=2.5.0`
- Added asyncpg for PostgreSQL async support: `asyncpg>=0.29.0`

### 4. Docker Compose Warnings

**Problem**: Docker Compose showing warnings about obsolete version field
**Solution**: Removed deprecated `version: '3.8'` from docker-compose.yml

## Final Status ✅

**All issues have been resolved!** The Docker containers now build and run successfully:

- ✅ **Frontend**: http://localhost:3000 (healthy) 
- ✅ **Backend**: http://localhost:8000 (running, may need DB migration)
- ✅ **PostgreSQL**: localhost:5432 (healthy)
- ✅ **Redis**: localhost:6379 (healthy)

## Testing the Fixes

To test the Docker build fixes:

```bash
# Clean any existing containers and images
docker-compose down --volumes --rmi all

# Build and start all services
make start-all

# Or manually:
docker-compose up -d --build

# Check status
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## Alternative Local Development

If Docker builds still have issues, run locally:

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (in another terminal)
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Key Learnings

1. **Node Environment**: Setting `NODE_ENV=production` too early can cause dev dependencies to be skipped
2. **Dependency Resolution**: Explicitly declaring conflicting dependencies (like PyTorch) helps pip resolve conflicts
3. **Build Tools**: Using npm scripts instead of direct tool invocation ensures proper PATH resolution
4. **Docker Layer Caching**: Copying package files before source code improves build caching efficiency
