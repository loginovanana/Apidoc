# Plugin Development Guide

Parser Plugin
python
from apidoc_cli.plugins.base import BaseParser
from pathlib import Path

class MyFrameworkParser(BaseParser):
    @property
    def name(self) -> str: return "my-parser"
    
    @property
    def frameworks(self) -> list: return ["myframework"]
    
    def parse(self, source: Path, **kwargs) -> dict:
        return {"openapi": "3.0.3", "info": {"title": "My API", "version": "1.0.0"}, "paths": {}}
Publisher Plugin
python
from apidoc_cli.plugins.base import BasePublisher

class MyPublisher(BasePublisher):
    @property
    def name(self) -> str: return "my-service"
    
    async def publish(self, spec, name, version, **kwargs):
        return {"status": "published"}
Registration in pyproject.toml
toml
[project.entry-points."apidoc.plugins"]
my-parser = "my_package:MyFrameworkParser"
