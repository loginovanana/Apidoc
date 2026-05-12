# CLI Command Reference

Global Options
Option	Description
--config, -c	Path to config file
--debug	Enable debug mode
--json	Output in JSON format
--version	Show version
Commands
generate — Generate OpenAPI specs from source code
bash
apidoc generate SOURCE [--output PATH] [--format yaml|json] [--framework NAME] [--interactive]
validate — Validate specifications
bash
apidoc validate SPEC_FILE [--strict] [--remote] [--fix] [--json]
diff — Compare two specifications
bash
apidoc diff SPEC1 SPEC2 [--tree] [--json]
mock — Start mock server
bash
apidoc mock SPEC_FILE [--host HOST] [--port PORT] [--log-file PATH]
testgen — Generate tests
bash
apidoc testgen SPEC_FILE [--output DIR] [--framework NAME] [--language LANG]
publish — Publish specification
bash
apidoc publish SPEC_FILE [--target server,github,swaggerhub,readme] [--name NAME] [--version VER]
convert — Convert between formats
bash
apidoc convert INPUT [--output PATH] [--to json|yaml] [--version VER] [--from-url URL]
server — Manage APIDoc server
bash
apidoc server start [--host HOST] [--port PORT] [--background]
apidoc server status
apidoc server search QUERY
apidoc server versions SPEC_ID
apidoc server init
tree — Visualize API structure
bash
apidoc tree SPEC_FILE [--schemas] [--methods/--no-methods]
