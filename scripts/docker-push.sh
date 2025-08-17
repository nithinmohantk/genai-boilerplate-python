#!/bin/bash

# Docker Hub Push Script for thingxcloud account
# This script builds and pushes the GenAI Boilerplate images to Docker Hub

set -e

DOCKER_HUB_USER="thingxcloud"
PROJECT_NAME="genai-boilerplate-python"
BUILD_ONLY=false

# Parse arguments
if [ "$1" = "--build-only" ]; then
    BUILD_ONLY=true
    VERSION=${2:-latest}
else
    VERSION=${1:-latest}
fi

if [ "$BUILD_ONLY" = true ]; then
    echo "🐳 Building Docker images for $DOCKER_HUB_USER/$PROJECT_NAME:$VERSION (build-only mode)"
else
    echo "🐳 Building and pushing Docker images for $DOCKER_HUB_USER/$PROJECT_NAME:$VERSION"
    # Check if user is logged in to Docker Hub
    if ! docker info | grep -q "Username.*$DOCKER_HUB_USER"; then
        echo "❌ Not logged in to Docker Hub as $DOCKER_HUB_USER"
        echo "Please run: docker login"
        echo "And log in with the thingxcloud account credentials"
        exit 1
    fi
    echo "✅ Logged in to Docker Hub as $DOCKER_HUB_USER"
fi

# Build and tag backend image
echo "🔨 Building backend image..."
docker build -t $DOCKER_HUB_USER/$PROJECT_NAME-backend:$VERSION ./backend
docker build -t $DOCKER_HUB_USER/$PROJECT_NAME-backend:latest ./backend

# Build and tag frontend image  
echo "🔨 Building frontend image..."
docker build -t $DOCKER_HUB_USER/$PROJECT_NAME-frontend:$VERSION ./frontend
docker build -t $DOCKER_HUB_USER/$PROJECT_NAME-frontend:latest ./frontend

if [ "$BUILD_ONLY" = false ]; then
    # Push backend images
    echo "⬆️  Pushing backend image..."
    docker push $DOCKER_HUB_USER/$PROJECT_NAME-backend:$VERSION
    docker push $DOCKER_HUB_USER/$PROJECT_NAME-backend:latest

    # Push frontend images
    echo "⬆️  Pushing frontend image..."
    docker push $DOCKER_HUB_USER/$PROJECT_NAME-frontend:$VERSION  
    docker push $DOCKER_HUB_USER/$PROJECT_NAME-frontend:latest

    echo "🎉 Successfully pushed all images to Docker Hub!"
    echo ""
    echo "Images available at:"
    echo "  📦 Backend:  https://hub.docker.com/r/$DOCKER_HUB_USER/$PROJECT_NAME-backend"
    echo "  📦 Frontend: https://hub.docker.com/r/$DOCKER_HUB_USER/$PROJECT_NAME-frontend"
    echo ""
    echo "To use these images:"
    echo "  docker pull $DOCKER_HUB_USER/$PROJECT_NAME-backend:$VERSION"
    echo "  docker pull $DOCKER_HUB_USER/$PROJECT_NAME-frontend:$VERSION"
else
    echo "🎉 Successfully built all images!"
    echo ""
    echo "Local images created:"
    echo "  📦 Backend:  $DOCKER_HUB_USER/$PROJECT_NAME-backend:$VERSION"
    echo "  📦 Frontend: $DOCKER_HUB_USER/$PROJECT_NAME-frontend:$VERSION"
    echo ""
    echo "To push these images later, run:"
    echo "  ./scripts/docker-push.sh $VERSION"
fi
