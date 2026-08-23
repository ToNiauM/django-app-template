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
    # --vcs-ref=HEAD: com uma tag de release no repositório, o Copier copiaria
    # por padrão a última tag — o teste precisa do estado atual do template.
    subprocess.run(
        [
            str(COPIER),
            "copy",
            "--defaults",
            "--vcs-ref=HEAD",
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
            self.assertTrue((destination / "apps/__init__.py").is_file())
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
            self.assertTrue((destination / "apps/__init__.py").is_file())
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

            nav_without = (without_example / "core/templates/core/_nav.html").read_bytes()
            nav_with = (with_example / "core/templates/core/_nav.html").read_bytes()

            # Critério 5: _nav.html é do núcleo, estático — byte a byte
            # idêntico nas duas variantes, independente de incluir_app_exemplo.
            self.assertEqual(
                nav_with,
                nav_without,
                "_nav.html divergiu entre as variantes — deixou de ser estático",
            )

            nav_texto = nav_without.decode("utf-8")
            self.assertIn("core:shell", nav_texto)
            self.assertIn("core/_nav_dominio.html", nav_texto)
            self.assertNotIn("exemplo:", nav_texto)
            self.assertNotIn("Dashboard", nav_texto)
            self.assertNotIn("Itens (CRUD)", nav_texto)

            dominio_without = (
                without_example / "core/templates/core/_nav_dominio.html"
            ).read_text(encoding="utf-8")
            dominio_with = (
                with_example / "core/templates/core/_nav_dominio.html"
            ).read_text(encoding="utf-8")

            # Variante false: o stub existe e não carrega nenhum item do exemplo.
            self.assertNotIn("exemplo:", dominio_without)

            # Variante true: o stub chega semeado com os dois itens do exemplo.
            self.assertIn("exemplo:dashboard", dominio_with)
            self.assertIn("exemplo:item_listar", dominio_with)
            self.assertIn("Dashboard", dominio_with)
            self.assertIn("Itens (CRUD)", dominio_with)

            readme = (with_example / "apps/exemplo/README.md").read_text(encoding="utf-8")

            self.assertIn("Sistema Núcleo", readme)
            self.assertIn("copier update --data incluir_app_exemplo=false", readme)
            self.assertIn("_nav_dominio.html", readme)
            self.assertNotRegex(readme, r"(?i)\b(?:pca|cfc\.org\.br|orcamento\.cfc\.org\.br|dominio-da-vps)\b")


if __name__ == "__main__":
    unittest.main()
