#!/bin/bash
set -e

# Configuration
IMAGE_NAME="car-part-scraper"
REGISTRY="ghcr.io/andy83-projects"  # Change to your GitHub username
VERSION="${1:-latest}"

echo "🐳 Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} .

echo "🏷️  Tagging image..."
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:latest

echo "📤 Pushing to registry..."
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker push ${REGISTRY}/${IMAGE_NAME}:latest

echo "✅ Build complete!"
echo ""
echo "Image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo ""
echo "To deploy, update the image in:"
echo "  homelab-gitops/k3s/apps/car-part-scraper/deployment.yaml"
