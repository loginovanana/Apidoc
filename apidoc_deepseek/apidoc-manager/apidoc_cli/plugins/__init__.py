"""Plugin system for APIDoc CLI."""

import sys
from typing import Any, Dict, List, Optional, Type

# Импортируем базовые классы из base.py – так наследование будет работать
from apidoc_cli.plugins.base import BaseParser, BasePublisher, BaseTestGenerator


class PluginManager:
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._publishers: Dict[str, Type[BasePublisher]] = {}
        self._test_generators: Dict[str, Type[BaseTestGenerator]] = {}
        self._load_plugins()

    def _load_plugins(self) -> None:
        # Явная регистрация всех встроенных плагинов
        # Парсеры
        try:
            from apidoc_cli.plugins.python_parser import PythonParserPlugin
            self._register_plugin(PythonParserPlugin)
        except Exception as e:
            import logging; logging.warning(f"python_parser: {e}")

        try:
            from apidoc_cli.plugins.js_parser import JSParserPlugin
            self._register_plugin(JSParserPlugin)
        except Exception as e:
            import logging; logging.warning(f"js_parser: {e}")

        try:
            from apidoc_cli.plugins.java_parser import JavaParserPlugin
            self._register_plugin(JavaParserPlugin)
        except Exception as e:
            import logging; logging.warning(f"java_parser: {e}")

        try:
            from apidoc_cli.plugins.go_parser import GoParserPlugin
            self._register_plugin(GoParserPlugin)
        except Exception as e:
            import logging; logging.warning(f"go_parser: {e}")

        # Генераторы тестов
        try:
            from apidoc_cli.plugins.pytest_generator import PytestGeneratorPlugin
            self._register_plugin(PytestGeneratorPlugin)
        except Exception as e:
            import logging; logging.warning(f"pytest_generator: {e}")

        try:
            from apidoc_cli.plugins.jest_generator import JestGeneratorPlugin
            self._register_plugin(JestGeneratorPlugin)
        except Exception as e:
            import logging; logging.warning(f"jest_generator: {e}")

        # Паблишеры
        try:
            from apidoc_cli.plugins.publishers.swaggerhub import SwaggerHubPublisher
            self._register_plugin(SwaggerHubPublisher)
        except Exception as e:
            import logging; logging.warning(f"swaggerhub: {e}")

        try:
            from apidoc_cli.plugins.publishers.github import GitHubPublisher
            self._register_plugin(GitHubPublisher)
        except Exception as e:
            import logging; logging.warning(f"github: {e}")

        try:
            from apidoc_cli.plugins.publishers.readme import ReadMePublisher
            self._register_plugin(ReadMePublisher)
        except Exception as e:
            import logging; logging.warning(f"readme: {e}")

        try:
            from apidoc_cli.plugins.publishers.redocly import RedoclyPublisher
            self._register_plugin(RedoclyPublisher)
        except Exception as e:
            import logging; logging.warning(f"redocly: {e}")

        # Дополнительные внешние плагины через entry_points (необязательно)
        try:
            if sys.version_info >= (3, 10):
                from importlib.metadata import entry_points
                eps = entry_points(group="apidoc.plugins")
            else:
                from importlib_metadata import entry_points
                eps = entry_points().get("apidoc.plugins", [])
            for ep in eps:
                try:
                    plugin_class = ep.load()
                    self._register_plugin(plugin_class)
                except Exception as e:
                    import logging; logging.warning(f"entry point {ep.name}: {e}")
        except Exception:
            pass

    def _register_plugin(self, plugin_class):
        if issubclass(plugin_class, BaseParser):
            instance = plugin_class()
            for framework in instance.frameworks:
                self._parsers[framework.lower()] = plugin_class
        elif issubclass(plugin_class, BasePublisher):
            instance = plugin_class()
            self._publishers[instance.name.lower()] = plugin_class
        elif issubclass(plugin_class, BaseTestGenerator):
            instance = plugin_class()
            self._test_generators[instance.name.lower()] = plugin_class

    def get_parser(self, framework: str) -> Optional[BaseParser]:
        parser_class = self._parsers.get(framework.lower())
        return parser_class() if parser_class else None

    def list_parsers(self) -> List[str]:
        return list(self._parsers.keys())

    def get_publisher(self, name: str) -> Optional[BasePublisher]:
        pub_class = self._publishers.get(name.lower())
        return pub_class() if pub_class else None

    def list_publishers(self) -> List[str]:
        return list(self._publishers.keys())

    def get_test_generator(self, name: str) -> Optional[BaseTestGenerator]:
        gen_class = self._test_generators.get(name.lower())
        return gen_class() if gen_class else None

    def list_test_generators(self) -> List[str]:
        return list(self._test_generators.keys())