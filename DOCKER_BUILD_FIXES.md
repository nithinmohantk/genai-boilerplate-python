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
- Maintained proper build stage separation in multi-stage Docker build

### 2. Backend Dependency Conflicts

**Problem**: PyTorch dependency conflicts causing installation failures:
```
ERROR: Cannot install -r requirements.txt (line 11) because these package versions have conflicting dependencies.
The conflict is caused by:
    sentence-transformers X.X.X depends on torch>=1.11.0
```

**Solution**: 
- Added explicit PyTorch dependency at the top of requirements.txt: `torch>=2.0.0,<3.0.0`
- This ensures PyTorch is resolved first, preventing downstream conflicts with sentence-transformers

### 3. Docker Compose Warnings

**Problem**: Docker Compose showing warnings about obsolete version field
**Solution**: Removed deprecated `version: '3.8'` from docker-compose.yml

## Testing the Fixes

To test the Docker build fixes:

```bash
# Clean any existing containers and images
docker-compose down --volumes --rmi all

# Build and start all services
make start-all

# Or manually:
docker-compose up -d --build
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
