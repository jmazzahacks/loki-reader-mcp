#!/bin/sh
# Build and publish loki-reader-mcp Docker image to GHCR
# Usage: ./build-publish.sh [--no-cache]

REGISTRY="ghcr.io/jmazzahacks/loki-reader-mcp"

NO_CACHE=""
if [ "$1" = "--no-cache" ]; then
    NO_CACHE="--no-cache"
fi

# Version management
if [ ! -f VERSION ]; then
    echo "1" > VERSION
fi

CURRENT_VERSION=$(cat VERSION)

# Validate version is numeric
case "$CURRENT_VERSION" in
    ''|*[!0-9]*)
        echo "ERROR: VERSION file contains non-numeric value: $CURRENT_VERSION"
        exit 1
        ;;
esac

NEXT_VERSION=$((CURRENT_VERSION + 1))

echo "Building ${REGISTRY}:${NEXT_VERSION}..."

docker build \
    --platform linux/amd64 \
    $NO_CACHE \
    -t "${REGISTRY}:${NEXT_VERSION}" \
    .

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed"
    exit 1
fi

# Tag as latest
docker tag "${REGISTRY}:${NEXT_VERSION}" "${REGISTRY}:latest"

# Push both tags
echo "Pushing ${REGISTRY}:${NEXT_VERSION}..."
docker push "${REGISTRY}:${NEXT_VERSION}"

if [ $? -ne 0 ]; then
    echo "ERROR: Push failed for versioned tag"
    exit 1
fi

echo "Pushing ${REGISTRY}:latest..."
docker push "${REGISTRY}:latest"

if [ $? -ne 0 ]; then
    echo "ERROR: Push failed for latest tag"
    exit 1
fi

# Update version file
echo "$NEXT_VERSION" > VERSION
echo "Published ${REGISTRY}:${NEXT_VERSION} and :latest"
