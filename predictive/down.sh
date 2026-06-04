#!/bin/sh
set -eu

STACK_NAME="predictive"

echo "=== Stopping predictive deployer compose ==="
docker compose down || true

echo "=== Removing predictive stack ==="
docker stack rm "$STACK_NAME" || true

echo "=== Waiting predictive services removal ==="
while docker service ls --format '{{.Name}}' | grep -q "^${STACK_NAME}_"; do
  echo "Waiting for services to disappear..."
  sleep 2
done

echo "=== Removing stopped predictive containers ==="
docker ps -a --filter "name=${STACK_NAME}_" --format '{{.ID}}' | xargs -r docker rm -f || true

echo "=== Removing predictive configs ==="
docker config ls --format '{{.Name}}' | grep "^${STACK_NAME}_" | xargs -r docker config rm || true

echo "Predictive stopped."