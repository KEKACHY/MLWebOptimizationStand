#!/bin/sh
set -eu

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " MLWebOptimizationStand: START ALL"
echo "========================================"

echo ""
echo "=== Checking Docker ==="
docker version >/dev/null

echo ""
echo "=== Checking Docker Swarm for predictive ==="

SWARM_STATE="$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo error)"
CONTROL_AVAILABLE="$(docker info --format '{{.Swarm.ControlAvailable}}' 2>/dev/null || echo false)"

echo "Swarm state: $SWARM_STATE"
echo "Control available: $CONTROL_AVAILABLE"

if [ "$SWARM_STATE" != "active" ] || [ "$CONTROL_AVAILABLE" != "true" ]; then
  echo "Docker Swarm is not active as manager."
  echo "Resetting local Swarm state for single-server stand..."

  docker swarm leave --force >/dev/null 2>&1 || true

  SERVER_IP="$(hostname -I | awk '{print $1}')"

  if [ -n "$SERVER_IP" ]; then
    docker swarm init --advertise-addr "$SERVER_IP" || docker swarm init
  else
    docker swarm init
  fi
fi

echo ""
echo "=== Starting baseline ==="
cd "$ROOT_DIR/baseline"
docker compose up -d --build

echo ""
echo "=== Starting reactive ==="
cd "$ROOT_DIR/reactive"
docker compose rm -f -s reactive-deployer >/dev/null 2>&1 || true
docker compose up --force-recreate --remove-orphans reactive-deployer

echo ""
echo "=== Starting predictive ==="
cd "$ROOT_DIR/predictive"
docker compose rm -f -s predictive-deployer >/dev/null 2>&1 || true
docker compose up --force-recreate --remove-orphans predictive-deployer

echo ""
echo "=== Starting experiment-ui ==="
cd "$ROOT_DIR/experiment-ui"
docker compose up -d --build

echo ""
echo "=== Final status ==="

echo ""
echo "--- baseline containers ---"
docker ps --filter "name=baseline-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

echo ""
echo "--- reactive k3d containers ---"
docker ps --filter "name=k3d-reactive" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

echo ""
echo "--- predictive services ---"
docker stack services predictive || true

echo ""
echo "--- experiment-ui containers ---"
docker ps --filter "name=experiment-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true

echo ""
echo "========================================"
echo " ALL SERVICES STARTED"
echo "========================================"
echo ""
echo "Baseline nginx:        http://SERVER_IP:80"
echo "Baseline frontend:     http://SERVER_IP:8080"
echo "Baseline prometheus:   http://SERVER_IP:9090"
echo ""
echo "Reactive nginx:        http://SERVER_IP:8020"
echo "Reactive frontend:     http://SERVER_IP:8081"
echo "Reactive prometheus:   http://SERVER_IP:9091"
echo ""
echo "Predictive nginx:      http://SERVER_IP:8030"
echo "Predictive frontend:   http://SERVER_IP:8082"
echo "Predictive prometheus: http://SERVER_IP:9092"
echo ""
echo "Experiment UI:         http://SERVER_IP:3000"
echo "Controller API:        http://SERVER_IP:7000"
echo ""