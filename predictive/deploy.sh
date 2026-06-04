#!/bin/sh
set -eu

STACK_NAME="predictive"

echo "=== Checking Docker Swarm ==="

SWARM_STATE="$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo error)"
CONTROL_AVAILABLE="$(docker info --format '{{.Swarm.ControlAvailable}}' 2>/dev/null || echo false)"

echo "Swarm state: $SWARM_STATE"
echo "Control available: $CONTROL_AVAILABLE"

if [ "$SWARM_STATE" != "active" ] || [ "$CONTROL_AVAILABLE" != "true" ]; then
  echo "ERROR: Docker Swarm is not active as manager."
  echo "Run once on host:"
  echo "  docker swarm leave --force"
  echo "  docker swarm init"
  exit 1
fi

echo "=== Removing old predictive stack ==="
docker stack rm "$STACK_NAME" || true

echo "=== Waiting old predictive services removal ==="
while docker service ls --format '{{.Name}}' | grep -q "^${STACK_NAME}_"; do
  echo "Waiting for services to disappear..."
  sleep 2
done

echo "=== Removing old stopped predictive containers ==="
docker ps -a --filter "name=${STACK_NAME}_" --format '{{.ID}}' | xargs -r docker rm -f || true

echo "=== Removing old predictive configs ==="
docker config ls --format '{{.Name}}' | grep "^${STACK_NAME}_" | xargs -r docker config rm || true

echo "=== Building predictive images ==="
docker build -t mlweb/predictive-backend:local ./GlossaryKEKACHY/backend
docker build -t mlweb/predictive-frontend:local ./GlossaryKEKACHY/frontend
docker build -t mlweb/predictive-ml:local ./ml_service
docker build -t mlweb/predictive-autoscaling:local ./autoscaling

echo "=== Deploying predictive stack ==="
docker stack deploy --resolve-image never -c docker-stack.yml "$STACK_NAME"

echo "=== Waiting services startup ==="
sleep 15

echo "=== Predictive services ==="
docker stack services "$STACK_NAME"

echo "=== Predictive tasks ==="
docker service ps predictive_nginx || true
docker service ps predictive_prometheus || true
docker service ps predictive_web-backend || true

echo "=== Smoke checks ==="
curl -i http://localhost:8030/ || true
curl -i http://localhost:8030/healthz || true
curl -i http://localhost:8030/glossaries/ || true
curl -i http://localhost:9092/-/ready || true

echo "=== Prometheus replicas query ==="
curl -G "http://localhost:9092/api/v1/query" \
  --data-urlencode 'query=count(up{job="predictive-backend"} == 1)' || true

echo ""
echo "Done."
echo "Predictive nginx:      http://SERVER_IP:8030"
echo "Predictive frontend:   http://SERVER_IP:8082"
echo "Predictive prometheus: http://SERVER_IP:9092"