"""Integrações do plano 04-03 para identidade do template Copier."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"


def render(destination: Path, *, color: str) -> Path:
    """Gera uma cópia com respostas explícitas para testar o contrato in-place."""
    subprocess.run(
        [
            str(COPIER),
            "copy",
            "--defaults",
            "--data",
            "sistema_nome=Sistema Aurora",
            "--data",
            "sistema_slug=aurora",
            "--data",
            "sistema_hostname=aurora.exemplo.gov.br",
            "--data",
            "sistema_porta=8123",
            "--data",
            "sistema_banco=aurora",
            "--data",
            "sistema_sigla=SA",
            "--data",
            f"cor_primaria={color}",
            str(ROOT),
            str(destination),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return destination


class RuntimeIdentityTemplateTests(unittest.TestCase):
    def test_tailwind_color_is_the_only_build_interpolation(self) -> None:
        self.assertTrue((ROOT / "tailwind.config.js.jinja").is_file())

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            teal = render(root / "teal", color="#0f766e")
            amber = render(root / "amber", color="#d97706")

            teal_tailwind = (teal / "tailwind.config.js").read_text(encoding="utf-8")
            amber_tailwind = (amber / "tailwind.config.js").read_text(encoding="utf-8")
            self.assertIn('const COR_PRIMARIA = "#0f766e";', teal_tailwind)
            self.assertIn('const COR_PRIMARIA = "#d97706";', amber_tailwind)
            self.assertNotEqual(teal_tailwind, amber_tailwind)
            self.assertEqual(
                (teal / "config/settings/base.py").read_text(encoding="utf-8"),
                (amber / "config/settings/base.py").read_text(encoding="utf-8"),
            )

    def test_rendered_settings_require_env_identity_and_dashboard_has_no_fallback(self) -> None:
        self.assertTrue((ROOT / "config/settings/base.py.jinja").is_file())

        with tempfile.TemporaryDirectory() as tempdir:
            destination = render(Path(tempdir) / "system", color="#0f766e")
            settings = (destination / "config/settings/base.py").read_text(encoding="utf-8")
            dashboard = (destination / "apps/exemplo/templates/exemplo/dashboard.html").read_text(
                encoding="utf-8"
            )

        for key in ("SISTEMA_NOME", "SISTEMA_SIGLA", "COR_PRIMARIA"):
            self.assertIn(f'{key} = env("{key}")', settings)
        self.assertIn('re.fullmatch(r"#[0-9a-fA-F]{6}", COR_PRIMARIA)', settings)
        self.assertIn('const corBrand = "{{ cor_primaria }}";', dashboard)
        self.assertNotIn("default:", dashboard)


if __name__ == "__main__":
    unittest.main()
