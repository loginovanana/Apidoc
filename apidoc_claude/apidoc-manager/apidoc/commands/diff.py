"""Diff command helpers."""
from __future__ import annotations
from typing import Any
from rich.tree import Tree
from apidoc.utils.output import console

def _collect_ops(spec: dict) -> dict[str, dict]:
    HTTP = {"GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"}
    ops: dict[str,dict] = {}
    for path, pi in spec.get("paths",{}).items():
        for m, op in pi.items():
            if m.upper() in HTTP: ops[f"{m.upper()} {path}"] = op if isinstance(op,dict) else {}
    return ops

def _req_body_fields(op: dict) -> set[str]:
    try:
        return set(op.get("requestBody",{}).get("content",{})
                     .get("application/json",{}).get("schema",{}).get("required",[]))
    except Exception: return set()

def _compare_specs(old: dict, new: dict) -> dict[str, Any]:
    old_ops, new_ops = _collect_ops(old), _collect_ops(new)
    breaking, non_breaking = [], []
    for k in set(old_ops) - set(new_ops):
        breaking.append({"type":"endpoint_removed","endpoint":k,"description":f"Endpoint removed: {k}"})
    for k in set(new_ops) - set(old_ops):
        non_breaking.append({"type":"endpoint_added","endpoint":k,"description":f"New endpoint: {k}"})
    for k in set(old_ops) & set(new_ops):
        old_op, new_op = old_ops[k], new_ops[k]
        for f in _req_body_fields(new_op) - _req_body_fields(old_op):
            breaking.append({"type":"required_body_field_added","endpoint":k,"field":f,
                              "description":f"{k}: new required field '{f}'"})
        for f in _req_body_fields(old_op) - _req_body_fields(new_op):
            non_breaking.append({"type":"required_body_field_removed","endpoint":k,"field":f,
                                  "description":f"{k}: field '{f}' now optional"})
        old_sc = {c for c in old_op.get("responses",{}) if str(c).startswith("2")}
        new_sc = {c for c in new_op.get("responses",{}) if str(c).startswith("2")}
        for c in old_sc - new_sc:
            breaking.append({"type":"response_code_changed","endpoint":k,"code":c,
                              "description":f"{k}: success code {c} removed"})
        if old_op.get("summary") != new_op.get("summary"):
            non_breaking.append({"type":"summary_changed","endpoint":k,"description":f"{k}: summary updated"})
    return {"breaking_changes": breaking, "non_breaking_changes": non_breaking,
            "summary":{"total":len(breaking)+len(non_breaking),
                        "breaking":len(breaking),"non_breaking":len(non_breaking)}}

def _render_diff(diff: dict, breaking_only: bool = False) -> None:
    s = diff["summary"]
    console.print(f"\n[bold]Diff summary:[/] [red]{s['breaking']} breaking[/] / "
                  f"[yellow]{s['non_breaking']} non-breaking[/] / [dim]{s['total']} total[/]\n")
    tree = Tree("[bold]Changes[/]")
    if diff["breaking_changes"]:
        b = tree.add("[bold red]⚠  Breaking Changes[/]")
        for c in diff["breaking_changes"]: b.add(f"[red]✗ {c['description']}[/]")
    if not breaking_only and diff["non_breaking_changes"]:
        nb = tree.add("[bold yellow]  Non-Breaking Changes[/]")
        for c in diff["non_breaking_changes"]: nb.add(f"[green]+ {c['description']}[/]")
    if not diff["breaking_changes"] and not (not breaking_only and diff["non_breaking_changes"]):
        tree.add("[green]✓ No changes detected[/]")
    console.print(tree)
