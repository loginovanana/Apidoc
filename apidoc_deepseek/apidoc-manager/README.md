# 🚀 APIDoc Manager

**Automated OpenAPI Specification Management CLI & Server**

APIDoc Manager is a comprehensive CLI tool and REST API server for automating the entire OpenAPI specification lifecycle.

## ✨ Features

- **🔧 Generate** - Create OpenAPI specs from FastAPI, Flask, Express, NestJS, Spring, and Gin
- **✅ Validate** - Validate specs locally or via official OpenAPI validator API
- **🔄 Diff** - Compare versions with breaking change detection
- **🎭 Mock** - Start mock server from specification
- **🧪 TestGen** - Generate Pytest and Jest test suites
- **📤 Publish** - Deploy to SwaggerHub, GitHub, ReadMe, Redocly
- **🔄 Convert** - Convert between OpenAPI 2.0/3.0/3.1 and JSON/YAML
- **🖥️ Server** - Centralized spec storage with versioning and search
- **🌲 Tree** - Visualize API structure as ASCII tree

## 🚀 Quick Start

```bash
pip install apidoc-manager
apidoc generate ./app.py --output openapi.yaml
apidoc validate openapi.yaml
apidoc mock openapi.yaml --port 8001
📝 License
MIT License - see LICENSE for details.
