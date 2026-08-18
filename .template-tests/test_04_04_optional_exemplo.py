"""Integrações Copier para a opcionalidade completa de ``apps.exemplo``."""

from __future__ import annotations

import py_compile
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"


def render(destination: Path, *, incluir_app_exemplo: bool) -> Path:
    """Renderiza uma variante real, com todos os dados não-default explícitos."""
    subprocess.run(
        [
            str(COPIER),
            "copy",
            "--defaults",
            "--data",
            "sistema_nome=Sistema Núcleo",
            "--data",
            "sistema_slug=nucleo",
            "--data",
            "sistema_hostname=nucleo.exemplo.gov.br",
            "--data",
            "sistema_porta=8123",
            "--data",
            "sistema_banco=nucleo",
            "--data",
            "sistema_sigla=SN",
            "--data",
            "cor_primaria=#0f766e",
            "--data",
            f"incluir_app_exemplo={str(incluir_app_exemplo).lower()}",
            ".",
            str(destination),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return destination


class OptionalExampleAppTemplateTests(unittest.TestCase):
    def test_true_renders_app_settings_and_route(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            destination = render(Path(tempdir) / "com-exemplo", incluir_app_exemplo=True)
            settings = (destination / "config/settings/base.py").read_text(encoding="utf-8")
            urls = (destination / "config/urls.py").read_text(encoding="utf-8")

            self.assertTrue((destination / "apps/exemplo").is_dir())
            self.assertIn('"apps.exemplo.apps.ExemploConfig",', settings)
            self.assertIn('path("exemplo/", include("apps.exemplo.urls"))', urls)
            py_compile.compile(destination / "config/settings/base.py", doraise=True)
            py_compile.compile(destination / "config/urls.py", doraise=True)

    def test_false_omits_only_the_example_app_integrations(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            destination = render(Path(tempdir) / "sem-exemplo", incluir_app_exemplo=False)
            settings_path = destination / "config/settings/base.py"
            urls_path = destination / "config/urls.py"
            settings = settings_path.read_text(encoding="utf-8")
            urls = urls_path.read_text(encoding="utf-8")

            self.assertFalse((destination / "apps/exemplo").exists())
            self.assertNotIn("apps.exemplo", settings)
            self.assertNotIn("apps.exemplo", urls)
            self.assertIn('path("admin/", admin.site.urls)', urls)
            self.assertIn('path("healthz", healthz, name="healthz")', urls)
            self.assertIn('path("", include("core.urls"))', urls)
            self.assertIn("SESSION_COOKIE_SECURE = True", settings)
            self.assertIn("CSRF_COOKIE_SECURE = True", settings)
            py_compile.compile(settings_path, doraise=True)
            py_compile.compile(urls_path, doraise=True)

    def test_navigation_and_readme_follow_the_same_boolean_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            without_example = render(root / "sem-exemplo", incluir_app_exemplo=False)
            with_example = render(root / "com-exemplo", incluir_app_exemplo=True)

            nav_without = (without_example / "core/templates/core/_nav.html").read_text(
                encoding="utf-8"
            )
            nav_with = (with_example / "core/templates/core/_nav.html").read_text(
                encoding="utf-8"
            )
            readme = (with_example / "apps/exemplo/README.md").read_text(encoding="utf-8")

            self.assertIn("core:shell", nav_without)
            self.assertNotIn("exemplo:", nav_without)
            self.assertNotIn("Dashboard", nav_without)
            self.assertNotIn("Itens (CRUD)", nav_without)
            self.assertIn("exemplo:dashboard", nav_with)
            self.assertIn("exemplo:item_listar", nav_with)
            self.assertIn("Dashboard", nav_with)
            self.assertIn("Itens (CRUD)", nav_with)
            self.assertIn("Sistema Núcleo", readme)
            self.assertIn("copier update --data incluir_app_exemplo=false", readme)
            self.assertNotRegex(readme, r"(?i)\b(?:pca|cfc\.org\.br|orcamento\.cfc\.org\.br|dominio-da-vps)\b")


if __name__ == "__main__":
    unittest.main()
