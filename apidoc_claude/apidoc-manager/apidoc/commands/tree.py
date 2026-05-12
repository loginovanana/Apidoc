"""Tree command helpers."""
from __future__ import annotations
from typing import Any
METHOD_COLORS = {"GET":"bold green","POST":"bold blue","PUT":"bold yellow",
                 "PATCH":"bold yellow","DELETE":"bold red","OPTIONS":"dim","HEAD":"dim"}
def spec_to_tree_dict(spec: dict) -> dict[str, Any]:
    info = spec.get("info",{}); paths = spec.get("paths",{})
    result: dict[str,Any] = {"api":info.get("title","API"),"version":info.get("version","?"),"paths":{}}
    for path_str, pi in paths.items():
        ops = {m.upper():op.get("summary","") for m,op in pi.items()
               if m.upper() in METHOD_COLORS and isinstance(op,dict)}
        if ops: result["paths"][path_str] = ops
    return result
