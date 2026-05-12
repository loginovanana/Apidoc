#!/bin/bash
set -e

echo "==================================="
echo "     APIDoc Manager Build         "
echo "==================================="

VERSION=""; BUILD_TYPE="wheel"; DOCKER_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --version) VERSION="$2"; shift 2 ;;
        --type) BUILD_TYPE="$2"; shift 2 ;;
        --docker) DOCKER_BUILD=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

clean() {
    echo "Cleaning..."
    rm -rf build/ dist/ *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    echo "✓ Cleaned"
}

build_python() {
    echo "Building Python package..."
    pip install --quiet build
    if [[ "$BUILD_TYPE" == "wheel" ]]; then python -m build --wheel; else python -m build; fi
    echo "✓ Python package built"
}

main() {
    clean
    build_python
    if [[ "$DOCKER_BUILD" == "true" ]]; then
        docker build -f docker/Dockerfile.prod -t "apidoc-manager:${VERSION:-latest}" .
    fi
    echo "==================================="
    echo "      Build Complete!              "
    echo "==================================="
}

main "$@"
