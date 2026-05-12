'''Jest test generator.'''

from pathlib import Path
from typing import Any, Dict, List

from apidoc_cli.plugins.base import BaseTestGenerator


class JestGeneratorPlugin(BaseTestGenerator):
    @property
    def name(self) -> str:
        return "jest"
    
    @property
    def language(self) -> str:
        return "javascript"
    
    @property
    def framework(self) -> str:
        return "jest"
    
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        tests_by_tag = self._group_by_tag(spec)
        for tag, endpoints in tests_by_tag.items():
            test_content = self._generate_test_file(tag, endpoints, spec)
            test_path = output_dir / f"{self._sanitize_name(tag)}.test.js"
            test_path.write_text(test_content)
            generated_files.append(test_path)
        return generated_files
    
    def _group_by_tag(self, spec: Dict) -> Dict[str, List]:
        groups = {"default": []}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                tags = details.get("tags", ["default"])
                for tag in tags:
                    if tag not in groups:
                        groups[tag] = []
                    groups[tag].append({"path": path, "method": method, "details": details})
        return groups
    
    def _generate_test_file(self, tag: str, endpoints: List, spec: Dict) -> str:
        servers = spec.get("servers", [{}])
        base_url = servers[0].get("url", "http://localhost:8000") if servers else "http://localhost:8000"
        content = "/**\n"
        content += " * Tests for " + tag + " endpoints\n"
        content += " */\n"
        content += "const axios = require('axios');\n"
        content += "const BASE_URL = '" + base_url + "';\n\n"
        content += "describe('" + tag + " API', () => {\n"
        content += "    let client;\n"
        content += "    beforeEach(() => {\n"
        content += "        client = axios.create({ baseURL: BASE_URL, timeout: 5000 });\n"
        content += "    });\n\n"
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"]
            details = endpoint["details"]
            success_code = 200
            for code in [200, 201, 204]:
                if str(code) in details.get("responses", {}):
                    success_code = code
                    break
            content += "    test('" + method.upper() + " " + path + "', async () => {\n"
            content += "        const response = await client." + method.lower() + "('" + path + "');\n"
            content += "        expect(response.status).toBe(" + str(success_code) + ");\n"
            content += "    });\n\n"
        content += "});\n"
        return content
    
    def _sanitize_name(self, name: str) -> str:
        import re
        return re.sub(r"[^\w\-]", "_", name.lower())
