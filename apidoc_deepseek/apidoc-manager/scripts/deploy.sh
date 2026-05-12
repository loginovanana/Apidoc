#!/bin/bash
set -e

echo "==================================="
echo "   APIDoc Manager Deploy          "
echo "==================================="

ENVIRONMENT="production"; DEPLOY_TYPE="docker"

while [[ $# -gt 0 ]]; do
    case $1 in
        --env) ENVIRONMENT="$2"; shift 2 ;;
        --type) DEPLOY_TYPE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

deploy_docker() {
    echo "Deploying with Docker Compose..."
    COMPOSE_FILE="docker/docker-compose.yml"
    if [[ "$ENVIRONMENT" == "production" ]]; then COMPOSE_FILE="docker/docker-compose.prod.yml"; fi
    docker-compose -f "$COMPOSE_FILE" up -d
    echo "✓ Docker deployment complete"
}

deploy_kubernetes() {
    echo "Deploying to Kubernetes..."
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml -n apidoc
    kubectl apply -f k8s/secrets.yaml -n apidoc
    kubectl apply -f k8s/deployment.yaml -n apidoc
    kubectl apply -f k8s/service.yaml -n apidoc
    kubectl apply -f k8s/hpa.yaml -n apidoc
    echo "✓ Kubernetes deployment complete"
}

main() {
    case "$DEPLOY_TYPE" in
        "docker") deploy_docker ;;
        "kubernetes") deploy_kubernetes ;;
        *) echo "Unknown deploy type: $DEPLOY_TYPE"; exit 1 ;;
    esac
    echo "==================================="
    echo "     Deployment Successful!        "
    echo "==================================="
}

main "$@"
