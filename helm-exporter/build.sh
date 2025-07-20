#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ghcr.io/elmi70/azure-aks-helm-charts/helm-exporter"
TAG="${1:-latest}"
FULL_IMAGE="${IMAGE_NAME}:${TAG}"

echo -e "${YELLOW}🔨 Building Helm Exporter Docker image...${NC}"
echo "Image: ${FULL_IMAGE}"
echo ""

# Build the image
docker build -t "${FULL_IMAGE}" ./helm-exporter

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
    
    # Show image info
    echo -e "${YELLOW}📦 Image details:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    
    # Test the image
    echo -e "${YELLOW}🧪 Testing the image...${NC}"
    echo "Starting container for testing..."
    
    # Run container in background
    CONTAINER_ID=$(docker run -d -p 8080:8080 "${FULL_IMAGE}")
    
    # Wait a moment for startup
    sleep 5
    
    # Test the metrics endpoint
    if curl -s http://localhost:8080/metrics > /dev/null; then
        echo -e "${GREEN}✅ Container is running and metrics endpoint is accessible!${NC}"
        echo ""
        echo -e "${YELLOW}📊 Sample metrics:${NC}"
        curl -s http://localhost:8080/metrics | head -10
    else
        echo -e "${RED}❌ Container test failed!${NC}"
    fi
    
    # Cleanup
    docker stop "${CONTAINER_ID}" > /dev/null 2>&1
    docker rm "${CONTAINER_ID}" > /dev/null 2>&1
    
    echo ""
    echo -e "${YELLOW}🚀 To push to registry:${NC}"
    echo "docker push ${FULL_IMAGE}"
    echo ""
    echo -e "${YELLOW}📝 To use in Kubernetes:${NC}"
    echo "image: ${FULL_IMAGE}"
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
