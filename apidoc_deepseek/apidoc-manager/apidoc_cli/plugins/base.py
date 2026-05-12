"""Base classes for plugins."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseParser(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def frameworks(self) -> List[str]:
        pass
    
    @abstractmethod
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        pass
    
    def detect(self, source: Path) -> bool:
        return False


class BasePublisher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    @abstractmethod
    async def publish(self, spec: Dict[str, Any], name: str, version: str, **kwargs) -> Dict[str, Any]:
        pass
    
    async def validate_credentials(self, **kwargs) -> bool:
        return True


class BaseTestGenerator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def language(self) -> str:
        pass
    
    @property
    @abstractmethod
    def framework(self) -> str:
        pass
    
    @abstractmethod
    def generate(self, spec: Dict[str, Any], output_dir: Path, **kwargs) -> List[Path]:
        pass
