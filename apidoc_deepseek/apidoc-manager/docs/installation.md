# Installation

## Prerequisites

- Python 3.10 or higher
- pip

## Installing APIDoc CLI

```bash
pip install apidoc-manager
```

### Or from source:

```bash
git clone https://github.com/apidoc/apidoc-manager.git
cd apidoc-manager
pip install -e .
```
## Installing APIDoc Server
### Using Docker (Recommended)
```bash
docker-compose -f docker/docker-compose.yml up -d
```
### Manual
```bash
apidoc server init
apidoc server start --host 0.0.0.0 --port 8000
```

### Shell Completion
```bash
# Bash
echo 'eval "$(apidoc --show-completion bash)"' >> ~/.bashrc
```
```bash
# Zsh
echo 'eval "$(apidoc --show-completion zsh)"' >> ~/.zshrc
```
