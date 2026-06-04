#!/bin/sh
set -eu

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " MLWebOptimizationStand: STOP ALL"
echo "========================================"

echo ""
echo "=== Stopping experiment-ui ==="
cd "$ROOT_DIR/experiment-ui"
docker compose down --remove-orphans || true

echo ""
echo "=== Stopping predictive ==="
cd "$ROOT_DIR/predictive"
if [ -f "./down.sh" ]; then
  chmod +x ./down.sh
  ./down.sh || true
else
  docker compose down --remove-orphans || true
  docker stack rm predictive || true
fi

echo ""
echo "=== Stopping reactive ==="
cd "$ROOT_DIR/reactive"
if [ -f "./down.sh" ]; then
  chmod +x ./down.sh
  ./down.sh || true
else
  docker compose down --remove-orphans || true
fi

echo ""
echo "=== Stopping baseline ==="
cd "$ROOT_DIR/baseline"
docker compose down --remove-orphans || true

echo ""
echo "=== Cleanup stopped deployer containers ==="
docker ps -a --filter "name=reactive-deployer" --format "{{.ID}}" | xargs -r docker rm -f || true
docker ps -a --filter "name=predictive-deployer" --format "{{.ID}}" | xargs -r docker rm -f || true

echo ""
echo "Stopped."