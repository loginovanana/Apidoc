"""Pytest test generator."""

from pathlib import Path
from typing import Any, Dict, List

from apidoc_cli.plugins.base import BaseTestGenerator


class PytestGeneratorPlugin(BaseTestGenerator):
    @property
    def name(self) -> str:
        return "pytest"

    @property
    def language(self) -> str:
        return "python"

    @property
    def framework(self) -> str:
        return "pytest"

    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        conftest = self._build_conftest(spec)
        p = output_dir / "conftest.py"
        p.write_text(conftest, encoding="utf-8")
        generated.append(p)

        for tag, endpoints in self._group_by_tag(spec).items():
            content = self._build_test_file(tag, endpoints)
            name = f"test_{self._safe_name(tag)}.py"
            p = output_dir / name
            p.write_text(content, encoding="utf-8")
            generated.append(p)

        return generated

    def _build_conftest(self, spec: Dict) -> str:
        servers = spec.get("servers", [{}])
        base_url = servers[0].get("url", "http://localhost:8000") if servers else "http://localhost:8000"
        lines = [
            '"""Pytest configuration."""',
            "",
            "import pytest",
            "import httpx",
            "",
            "",
            "@pytest.fixture",
            "def base_url():",
            f'    return "{base_url}"',
            "",
            "",
            "@pytest.fixture",
            "async def client():",
            "    async with httpx.AsyncClient() as client:",
            "        yield client",
        ]
        return "\n".join(lines)

    def _group_by_tag(self, spec: Dict) -> Dict[str, List]:
        groups = {"default": []}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ("get", "post", "put", "delete", "patch"):
                    continue
                for tag in details.get("tags", ["default"]):
                    groups.setdefault(tag, []).append(
                        {"path": path, "method": method, "details": details}
                    )
        return groups

    def _build_test_file(self, tag: str, endpoints: list) -> str:
        class_name = self._safe_name(tag).title()
        lines = [
            f'"""Tests for {tag} endpoints."""',
            "",
            "import pytest",
            "from httpx import AsyncClient",
            "",
            "",
            f"class Test{class_name}API:",
            f'    """Test cases for {tag} endpoints."""',
            "    ",
        ]
        for ep in endpoints:
            lines.append(self._build_test_method(ep))
        return "\n".join(lines)

    def _build_test_method(self, endpoint: dict) -> str:
        path = endpoint["path"]
        method = endpoint["method"]
        details = endpoint["details"]
        op_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
        success = "200"
        for code in ("200", "201", "204"):
            if code in details.get("responses", {}):
                success = code
                break
        return (
            "\n"
            + "    @pytest.mark.asyncio\n"
            + f"    async def test_{op_id}(self, client: AsyncClient, base_url: str):\n"
            + f'        """Test {method.upper()} {path}"""\n'
            + f"        response = await client.{method.lower()}(f\"{{base_url}}{path}\")\n"
            + f"        assert response.status_code == {success}\n"
        )

    def _safe_name(self, name: str) -> str:
        import re
        s = re.sub(r"[^\w]", "_", name.lower())
        if s and s[0].isdigit():
            s = "_" + s
        return s