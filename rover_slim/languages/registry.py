import os
from typing import List, Optional, Dict
from rover_slim.languages.base import BaseLanguageAdapter
from rover_slim.languages.python_adapter import PythonLanguageAdapter
from rover_slim.languages.node_adapter import NodeLanguageAdapter
from rover_slim.languages.java_adapter import JavaLanguageAdapter
from rover_slim.languages.dotnet_adapter import DotNetLanguageAdapter

class LanguageRegistry:
    """Registry that manages and auto-detects language adapters for a given project root."""

    def __init__(self):
        self._adapters: Dict[str, BaseLanguageAdapter] = {}
        # Register default adapters
        self.register(PythonLanguageAdapter())
        self.register(NodeLanguageAdapter())
        self.register(JavaLanguageAdapter())
        self.register(DotNetLanguageAdapter())

    def register(self, adapter: BaseLanguageAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> Optional[BaseLanguageAdapter]:
        return self._adapters.get(name)

    def list_adapters(self) -> List[BaseLanguageAdapter]:
        return list(self._adapters.values())

    def detect_language(self, root_dir: str) -> BaseLanguageAdapter:
        """Detects the matching language adapter, defaulting to Python if ambiguous."""
        root = os.path.abspath(root_dir)
        for adapter in self._adapters.values():
            if adapter.detect(root):
                return adapter
        # Default fallback
        return self._adapters.get("python", PythonLanguageAdapter())
