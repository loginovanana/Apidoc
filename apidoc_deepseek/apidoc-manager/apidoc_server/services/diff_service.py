"""Diff service for comparing specifications."""

from typing import Any, Dict, List

from deepdiff import DeepDiff


class DiffService:
    def compare(self, spec1: Dict[str, Any], spec2: Dict[str, Any], detect_breaking: bool = True) -> Dict[str, Any]:
        diff = DeepDiff(spec1, spec2, ignore_order=True, report_repetition=True, verbose_level=2, view="tree")
        
        changes = {"added": [], "removed": [], "changed": [], "type_changed": []}
        for item in diff.get("dictionary_item_added", []):
            if isinstance(item, str): changes["added"].append({"path": item})
        for item in diff.get("dictionary_item_removed", []):
            if isinstance(item, str): changes["removed"].append({"path": item})
        for path, change in diff.get("values_changed", {}).items():
            changes["changed"].append({"path": path, "old_value": change.get("old_value"), "new_value": change.get("new_value")})
        for path, change in diff.get("type_changes", {}).items():
            changes["type_changed"].append({"path": path, "old_type": change.get("old_type"), "new_type": change.get("new_type")})
        
        breaking_changes = []
        if detect_breaking:
            breaking_changes = self._detect_breaking_changes(spec1, spec2, changes)
        
        summary = {"total_changes": len(changes["added"]) + len(changes["removed"]) + len(changes["changed"]) + len(changes["type_changed"]), "breaking_changes_count": len(breaking_changes), "has_breaking_changes": len(breaking_changes) > 0}
        return {"changes": changes, "breaking_changes": breaking_changes, "summary": summary}
    
    def _detect_breaking_changes(self, spec1: Dict[str, Any], spec2: Dict[str, Any], changes: Dict[str, Any]) -> List[Dict[str, Any]]:
        breaking = []
        paths1 = spec1.get("paths", {})
        paths2 = spec2.get("paths", {})
        
        for path in paths1:
            if path not in paths2:
                breaking.append({"type": "endpoint_removed", "path": path, "severity": "high", "message": f"Endpoint {path} was removed"})
                continue
            for method in paths1[path]:
                if method not in paths2[path]:
                    breaking.append({"type": "method_removed", "path": path, "method": method.upper(), "severity": "high", "message": f"Method {method.upper()} {path} was removed"})
        
        schemas1 = spec1.get("components", {}).get("schemas", {})
        schemas2 = spec2.get("components", {}).get("schemas", {})
        for schema_name, schema in schemas1.items():
            if schema_name not in schemas2:
                breaking.append({"type": "schema_removed", "schema": schema_name, "severity": "high", "message": f"Schema '{schema_name}' was removed"})
        
        return breaking
