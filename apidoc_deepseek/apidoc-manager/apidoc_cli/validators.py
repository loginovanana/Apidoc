"""OpenAPI specification validator."""

import json
from pathlib import Path
from typing import Any, Dict

import httpx
import yaml
from loguru import logger
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPISpecValidatorError
from prance import ResolvingParser


class OpenAPIValidator:
    
    REMOTE_VALIDATOR_URL = "https://validator.swagger.io/validator/debug"
    
    def __init__(self, use_remote: bool = False):
        self.use_remote = use_remote
    
    def validate(self, spec_file: Path, strict: bool = False) -> Dict[str, Any]:
        spec = self._load_spec(spec_file)
        results = {"valid": True, "errors": [], "warnings": [], "fixable": []}
        
        if self.use_remote:
            return self._validate_remote(spec)
        
        try:
            validate_spec(spec)
            self._check_references(spec, results)
            self._check_common_issues(spec, results)
        except OpenAPISpecValidatorError as e:
            results["valid"] = False
            results["errors"].append({"type": "validation_error", "message": str(e), "location": self._extract_location(e)})
        except Exception as e:
            results["valid"] = False
            results["errors"].append({"type": "parse_error", "message": str(e)})
        
        return results
    
    def _validate_remote(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.REMOTE_VALIDATOR_URL, json={"spec": spec})
                response.raise_for_status()
                data = response.json()
                results = {"valid": len(data.get("schemaValidationMessages", [])) == 0, "errors": [], "warnings": [], "fixable": []}
                for msg in data.get("schemaValidationMessages", []):
                    error = {"type": "remote_validation", "message": msg.get("message", ""), "location": msg.get("path", "")}
                    if msg.get("level") == "error":
                        results["errors"].append(error)
                    else:
                        results["warnings"].append(error)
                return results
        except Exception as e:
            logger.error(f"Remote validation failed: {e}")
            return {"valid": False, "errors": [{"type": "remote_error", "message": str(e)}], "warnings": [], "fixable": []}
    
    def _load_spec(self, spec_file: Path) -> Dict[str, Any]:
        content = spec_file.read_text(encoding="utf-8")
        if spec_file.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(content)
        elif spec_file.suffix == ".json":
            return json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {spec_file.suffix}")
    
    def _check_references(self, spec: Dict[str, Any], results: Dict) -> None:
        try:
            parser = ResolvingParser(spec_string=json.dumps(spec))
            def collect_refs(obj, path=""):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref = obj["$ref"]
                        if not ref.startswith("#"):
                            results["warnings"].append(f"External reference: {ref} at {path}")
                    for key, value in obj.items():
                        collect_refs(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        collect_refs(item, f"{path}[{i}]")
            collect_refs(spec)
        except Exception as e:
            results["warnings"].append(f"Reference validation warning: {e}")
    
    def _check_common_issues(self, spec: Dict[str, Any], results: Dict) -> None:
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    continue
                if "responses" not in details:
                    results["errors"].append({"type": "missing_responses", "location": f"paths.{path}.{method}", "message": f"Missing 'responses' field for {method.upper()} {path}"})
                    results["fixable"].append({"type": "add_responses", "location": f"paths.{path}.{method}", "description": f"Add default 200 response for {method.upper()} {path}"})
                if "operationId" not in details:
                    results["warnings"].append(f"Missing operationId for {method.upper()} {path}")
    
    def _extract_location(self, error: Exception) -> str:
        error_str = str(error)
        if "in " in error_str:
            parts = error_str.split("in ")
            if len(parts) > 1:
                return parts[-1].split()[0].strip("'\"")
        return ""
    
    def apply_fix(self, spec_file: Path, issue: Dict[str, Any]) -> bool:
        spec = self._load_spec(spec_file)
        if issue["type"] == "add_responses":
            location = issue["location"]
            parts = location.split(".")
            if len(parts) >= 3:
                path = parts[1]
                method = parts[2]
                if path in spec["paths"] and method in spec["paths"][path]:
                    spec["paths"][path][method]["responses"] = {"200": {"description": "Successful response", "content": {"application/json": {"schema": {"type": "object"}}}}}
                    self._save_spec(spec_file, spec)
                    return True
        return False
    
    def _save_spec(self, spec_file: Path, spec: Dict[str, Any]) -> None:
        if spec_file.suffix in [".yaml", ".yml"]:
            content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        else:
            content = json.dumps(spec, indent=2, ensure_ascii=False)
        spec_file.write_text(content, encoding="utf-8")
