# Quick Start Guide

5-Minute Quick Start
1. Generate Your First Specification
bash
apidoc generate ./my_fastapi_app.py --output openapi.yaml
apidoc generate --interactive
2. Validate
bash
apidoc validate openapi.yaml
3. Start Mock Server
bash
apidoc mock openapi.yaml --port 8001
curl http://localhost:8001/users
4. Generate Tests
bash
apidoc testgen openapi.yaml --output ./tests --framework pytest
pytest ./tests -v
5. Publish
bash
apidoc server start
apidoc publish openapi.yaml --target server --name "My API"
