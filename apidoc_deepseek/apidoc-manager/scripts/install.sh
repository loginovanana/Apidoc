#!/bin/bash
set -e

echo "==================================="
echo "   APIDoc Manager Installer       "
echo "==================================="

check_python() {
    echo "Checking Python..."
    if command -v python3 &> /dev/null; then PYTHON="python3"
    elif command -v python &> /dev/null; then PYTHON="python"
    else echo "✗ Python not found"; exit 1; fi
    echo "✓ Python found"
}

install_apidoc() {
    echo "Installing APIDoc Manager..."
    if [[ -f "pyproject.toml" ]]; then pip install -e .; else pip install apidoc-manager; fi
    echo "✓ APIDoc Manager installed"
}

main() {
    check_python
    install_apidoc
    mkdir -p "$HOME/.apidoc/logs" "$HOME/.apidoc/cache"
    echo "==================================="
    echo "   Installation Complete!          "
    echo "==================================="
}

main "$@"
