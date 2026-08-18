"""Contrato de build do Dockerfile para settings obrigatórios no collectstatic."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CollectstaticBuildEnvironmentTests(unittest.TestCase):
    def test_collectstatic_recebe_todas_as_settings_obrigatorias_e_seguras(self) -> None:
        settings = (ROOT / "config/settings/base.py.jinja").read_text(encoding="utf-8")
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

        required = set(re.findall(r'env\("([A-Z_]+)"\)', settings))
        required.add("DATABASE_URL")
        self.assertEqual(
            required,
            {"SECRET_KEY", "DATABASE_URL", "SISTEMA_NOME", "SISTEMA_SIGLA", "COR_PRIMARIA"},
        )

        collectstatic = re.search(
            r"RUN (?P<environment>.*?)\\\n    python manage.py collectstatic --noinput",
            dockerfile,
            re.DOTALL,
        )
        self.assertIsNotNone(collectstatic)
        block = collectstatic.group("environment") if collectstatic else ""

        expected_safe_values = {
            "SECRET_KEY": "build",
            "DATABASE_URL": "sqlite:///tmp/build.db",
            "DJANGO_SETTINGS_MODULE": "config.settings.prod",
            "SISTEMA_NOME": "build",
            "SISTEMA_SIGLA": "BLD",
            "COR_PRIMARIA": "#000000",
        }
        for key, value in expected_safe_values.items():
            self.assertIn(f"{key}={value}", block)


if __name__ == "__main__":
    unittest.main()
