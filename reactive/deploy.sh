#!/bin/sh
set -eu

CLUSTER_NAME="reactive"
KUBECONFIG_FILE="/tmp/k3d-${CLUSTER_NAME}-kubeconfig.yaml"

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

if k3d cluster list | grep -q "$CLUSTER_NAME"; then
  echo "Deleting old reactive Kubernetes cluster..."
  k3d cluster delete "$CLUSTER_NAME"
fi

echo "Creating reactive Kubernetes cluster..."

k3d cluster create "$CLUSTER_NAME" \
  --agents 0 \
  --port "8020:30080@server:0" \
  --port "8081:30081@server:0" \
  --port "9091:30091@server:0"

echo "Preparing kubeconfig..."

k3d kubeconfig get "$CLUSTER_NAME" > "$KUBECONFIG_FILE"
export KUBECONFIG="$KUBECONFIG_FILE"

echo "Waiting for Kubernetes API..."

until kubectl get nodes >/dev/null 2>&1; do
  echo "Waiting for cluster API..."
  sleep 2
done

kubectl get nodes

echo "Building reactive images..."

docker build -t reactive-backend:local ./GlossaryKEKACHY/backend
docker build -t reactive-frontend:local ./GlossaryKEKACHY/frontend

echo "Importing images into reactive Kubernetes cluster..."

k3d image import reactive-backend:local -c "$CLUSTER_NAME"
k3d image import reactive-frontend:local -c "$CLUSTER_NAME"

echo "Applying Kubernetes manifests..."

kubectl apply -f k8s/namespace.yaml --validate=false

echo "Waiting for namespace reactive..."

until kubectl get namespace reactive >/dev/null 2>&1; do
  echo "Waiting for namespace..."
  sleep 1
done

kubectl apply -f k8s/nginx-config.yaml --validate=false
kubectl apply -f k8s/backend.yaml --validate=false
kubectl apply -f k8s/frontend.yaml --validate=false
kubectl apply -f k8s/prometheus.yaml --validate=false
kubectl apply -f k8s/hpa.yaml --validate=false
kubectl apply -f k8s/nginx.yaml --validate=false

echo "Waiting for reactive backend rollout..."

kubectl rollout status deployment/reactive-backend -n reactive --timeout=180s

echo "Waiting for reactive frontend rollout..."

kubectl rollout status deployment/reactive-frontend -n reactive --timeout=180s

echo "Waiting for reactive prometheus rollout..."

kubectl rollout status deployment/reactive-prometheus -n reactive --timeout=180s

echo "Waiting for reactive nginx rollout..."

kubectl rollout status deployment/reactive-nginx -n reactive --timeout=180s

echo "Validating required Services and Endpoints..."

kubectl get svc reactive-backend reactive-backend-headless reactive-nginx reactive-frontend reactive-prometheus -n reactive

kubectl get endpoints reactive-backend reactive-backend-headless -n reactive

echo "Checking backend through nginx inside cluster..."

kubectl run curl-check-nginx \
  -n reactive \
  --image=curlimages/curl:latest \
  --rm -i --restart=Never \
  -- curl -f http://reactive-nginx/metrics

echo "Reactive deployment status:"
kubectl get all -n reactive

echo "Reactive HPA status:"
kubectl get hpa -n reactive

echo "Done."
echo "Reactive nginx:      http://SERVER_IP:8020"
echo "Reactive frontend:   http://SERVER_IP:8081"
echo "Reactive prometheus: http://SERVER_IP:9091"