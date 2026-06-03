#!/bin/sh
set -e

CLUSTER_NAME="vkr-reactive"

echo "Installing tools inside deployer container..."

apk add --no-cache curl bash

if ! command -v k3d >/dev/null 2>&1; then
  curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
fi

if ! command -v kubectl >/dev/null 2>&1; then
  curl -LO "https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl"
  chmod +x kubectl
  mv kubectl /usr/local/bin/kubectl
fi

echo "Checking reactive Kubernetes cluster..."

if ! k3d cluster list | grep -q "$CLUSTER_NAME"; then
  echo "Creating reactive Kubernetes cluster..."

  k3d cluster create "$CLUSTER_NAME" \
    --agents 0 \
    --port "8020:80@loadbalancer" \
    --port "8081:8080@loadbalancer" \
    --port "9091:9090@loadbalancer"
else
  echo "Reactive cluster already exists."
fi

echo "Building reactive images..."

docker build -t reactive-backend:local ./GlossaryKEKACHY/backend
docker build -t reactive-frontend:local ./GlossaryKEKACHY/frontend

echo "Importing images into reactive Kubernetes cluster..."

k3d image import reactive-backend:local -c "$CLUSTER_NAME"
k3d image import reactive-frontend:local -c "$CLUSTER_NAME"

echo "Applying Kubernetes manifests..."

kubectl apply -f ./k8s/

echo "Reactive deployment status:"
kubectl get all -n reactive

echo "Reactive HPA status:"
kubectl get hpa -n reactive

echo "Done."
echo "Reactive nginx:      http://SERVER_IP:8020"
echo "Reactive frontend:   http://SERVER_IP:8081"
echo "Reactive prometheus: http://SERVER_IP:9091"