"""Validation service for OpenAPI specifications."""

import json
import re
from typing import Any, Dict

import httpx
from loguru import logger
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPISpecValidatorError
from prance import ResolvingParser


class ValidationService:
    REMOTE_VALIDATOR_URL = "https://validator.swagger.io/validator/debug"
    
    async def validate(self, spec: Dict[str, Any], strict: bool = False, use_remote: bool = False) -> Dict[str, Any]:
        results = {"valid": True, "errors": [], "warnings": [], "fixable": []}
        
        if "openapi" not in spec and "swagger" not in spec:
            results["valid"] = False
            results["errors"].append({"type": "missing_version", "message": "Missing 'openapi' or 'swagger' field"})
            return results
        
        if use_remote:
            return await self._validate_remote(spec)
        
        try:
            validate_spec(spec)
        except OpenAPISpecValidatorError as e:
            results["valid"] = False
            results["errors"].append({"type": "validation_error", "message": str(e), "location": self._extract_location(e)})
        except Exception as e:
            results["valid"] = False
            results["errors"].append({"type": "parse_error", "message": str(e)})
        
        self._check_references(spec, results)
        self._check_common_issues(spec, results)
        return results
    
    async def _validate_remote(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.REMOTE_VALIDATOR_URL, json={"spec": spec})
                response.raise_for_status()
                data = response.json()
                results = {"valid": len(data.get("schemaValidationMessages", [])) == 0, "errors": [], "warnings": [], "fixable": []}
                for msg in data.get("schemaValidationMessages", []):
                    error = {"type": "remote_validation", "message": msg.get("message", ""), "location": msg.get("path", "")}
                    if msg.get("level") == "error": results["errors"].append(error)
                    else: results["warnings"].append(error)
                return results
        except Exception as e:
            logger.error(f"Remote validation failed: {e}")
            return {"valid": False, "errors": [{"type": "remote_error", "message": str(e)}], "warnings": [], "fixable": []}
    
    def _check_references(self, spec: Dict[str, Any], results: Dict) -> None:
        try:
            parser = ResolvingParser(spec_string=json.dumps(spec))
            def collect_refs(obj, path=""):
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        if not obj["$ref"].startswith("#"):
                            results["warnings"].append({"type": "external_reference", "message": f"External reference: {obj['$ref']}", "location": path})
                    for key, value in obj.items():
                        collect_refs(value, f"{path}.{key}" if path else key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        collect_refs(item, f"{path}[{i}]")
            collect_refs(spec)
        except Exception as e:
            results["warnings"].append({"type": "reference_error", "message": f"Reference validation warning: {e}"})
    
    def _check_common_issues(self, spec: Dict[str, Any], results: Dict) -> None:
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]: continue
                if "responses" not in details:
                    results["errors"].append({"type": "missing_responses", "location": f"paths.{path}.{method}", "message": "Missing 'responses' field"})
                    results["fixable"].append({"type": "add_responses", "location": f"paths.{path}.{method}", "description": f"Add default response for {method.upper()} {path}"})
                if "operationId" not in details:
                    results["warnings"].append({"type": "missing_operation_id", "location": f"paths.{path}.{method}", "message": "Missing operationId"})
        info = spec.get("info", {})
        if "title" not in info: results["errors"].append({"type": "missing_title", "message": "Missing 'info.title'"})
        if "version" not in info: results["errors"].append({"type": "missing_version", "message": "Missing 'info.version'"})
    
    def _extract_location(self, error: Exception) -> str:
        error_str = str(error)
        for pattern in [r"in ['\"]([^'\"]+)['\"]", r"at ['\"]([^'\"]+)['\"]", r"path ['\"]([^'\"]+)['\"]"]:
            match = re.search(pattern, error_str)
            if match: return match.group(1)
        return ""
