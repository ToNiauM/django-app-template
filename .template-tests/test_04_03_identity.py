"""Integrações do plano 04-03 para identidade do template Copier."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"
OPTIONAL_EXAMPLE_APP = ROOT / "apps/{% if incluir_app_exemplo %}exemplo{% endif %}"
FORBIDDEN_IDENTITY = (
    "sistema_base",
    "Sistema Base",
    "PCA",
    "CFC",
    "orcamento",
    "financeiro",
    "dividaativa",
    "orcamento.cfc.org.br",
    "cfc.org.br",
    "toniaum/pca",
    "github.com/ToNiauM/pca",
    "pca_rehearsal_",
    "pca_pgdata",
    "_retention_test",
    "dominio-da-vps",
)


def render(destination: Path, *, color: str) -> Path:
    """Gera uma cópia com respostas explícitas para testar o contrato in-place."""
    # --vcs-ref=HEAD: com uma tag de release no repositório, o Copier copiaria
    # por padrão a última tag — o teste precisa do estado atual do template.
    subprocess.run(
        [
            str(COPIER),
            "copy",
            "--defaults",
            "--vcs-ref=HEAD",
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
            ".",
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

    def test_runtime_scripts_are_neutral_and_generated_tree_has_no_identity_leaks(self) -> None:
        entrypoint = (ROOT / "entrypoint.sh").read_text(encoding="utf-8")
        seed = (OPTIONAL_EXAMPLE_APP / "management/commands/seed_exemplo.py").read_text(
            encoding="utf-8"
        )
        readme = (OPTIONAL_EXAMPLE_APP / "README.md.jinja").read_text(encoding="utf-8")
        icon_generator = (ROOT / "ops/gerar_icones_pwa.py").read_text(encoding="utf-8")

        self.assertIn("--bind 0.0.0.0:8000", entrypoint)
        self.assertNotIn("$WEB_PORT", entrypoint)
        self.assertIn("app exemplo removível", seed)
        self.assertNotIn("Sistema Base", readme)
        self.assertNotIn("CFC", readme)
        self.assertIn("def carregar_env", icon_generator)
        self.assertNotIn('else "#1e40af"', icon_generator)
        self.assertNotIn('else "SB"', icon_generator)

        with tempfile.TemporaryDirectory() as tempdir:
            destination = render(Path(tempdir) / "system", color="#0f766e")
            hits = []
            patterns = [
                (token, re.compile(rf"(?<!\w){re.escape(token)}(?!\w)", re.IGNORECASE))
                for token in FORBIDDEN_IDENTITY
            ]
            for path in destination.rglob("*"):
                if not path.is_file():
                    continue
                relative = path.relative_to(destination).as_posix()
                for token, pattern in patterns:
                    for match in pattern.finditer(relative):
                        hits.append(f"path:{relative}:1:{match.start() + 1}:{token}")
                for line_number, line in enumerate(
                    path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
                ):
                    # O Copier registra a origem local exclusivamente para
                    # suportar `copier update`; não é conteúdo do sistema.
                    if path.name == ".copier-answers.yml":
                        line = re.sub(r"(?:^|[,{]\s*)_src_path:\s*[^,}]+", "", line)
                    for token, pattern in patterns:
                        for match in pattern.finditer(line):
                            hits.append(
                                f"content:{relative}:{line_number}:{match.start() + 1}:{token}"
                            )

            excluded = (
                ".planning",
                ".template-tests",
                "copier.yml",
                ".venv-template",
                "IDEIA.md",
                "REVIEW.md",
                "CLAUDE.md",
                ".copier-answers.yml.jinja",
            )
            artifacts = [name for name in excluded if (destination / name).exists()]
            artifacts.extend(
                item.relative_to(destination).as_posix()
                for item in destination.rglob("*.jinja")
            )

        self.assertEqual(hits, [])
        self.assertEqual(artifacts, [])


if __name__ == "__main__":
    unittest.main()
