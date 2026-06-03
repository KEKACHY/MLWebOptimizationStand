#!/bin/sh
set -e

CLUSTER_NAME="reactive"

echo "Stopping deployer compose..."
docker compose down

echo "Deleting k3d cluster: $CLUSTER_NAME"
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  docker:27-cli sh -c "apk add --no-cache curl bash >/dev/null && curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash >/dev/null && k3d cluster delete $CLUSTER_NAME"

echo "Reactive stopped."