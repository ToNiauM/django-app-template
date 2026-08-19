"""Contrato de persistência do plano 06-01: bind mount e .gitignore gerado.

O critério que estes testes protegem: `docker compose down -v` num sistema
gerado nunca pode destruir o banco (D-73), e o sistema recém-gerado nasce com
`.gitignore` que impede `git add .` de commitar `.env` e `/dados/` (D-74).
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"


def render(destination: Path) -> Path:
    """Gera uma cópia real com respostas neutras (mesmo molde do test_04_03).

    --vcs-ref=HEAD é obrigatório: como o template é um repositório git com tag
    de release, o Copier copiaria por padrão a última tag (estado antigo) — o
    teste precisa validar o estado ATUAL da árvore de trabalho.
    """
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
            str(ROOT),
            str(destination),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return destination


class ContratoFonteTests(unittest.TestCase):
    """Asserções diretas sobre os arquivos-fonte do template."""

    def test_compose_usa_bind_mount_sem_named_volume(self) -> None:
        compose = (ROOT / "compose.yml.jinja").read_text(encoding="utf-8")
        # O bind mount com default relativo é a proteção estrutural contra
        # `down -v` (D-73); qualquer resquício de `pgdata` reintroduz o risco.
        self.assertIn(
            "${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data", compose
        )
        self.assertNotIn("pgdata", compose)

    def test_env_example_documenta_pgdata_dir(self) -> None:
        env_example = (ROOT / ".env.example.jinja").read_text(encoding="utf-8")
        self.assertIn("PGDATA_DIR", env_example)

    def test_copier_nao_exclui_gitignore(self) -> None:
        # O _exclude aplica ao caminho de DESTINO: manter `.gitignore` ali
        # bloquearia o `.gitignore.jinja` renderizado (Pitfall 3).
        copier_yml = (ROOT / "copier.yml").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^\s*- \.gitignore$", copier_yml))

    def test_gitignore_do_template_ignora_dados(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/dados/", gitignore.splitlines())

    def test_gitignore_jinja_protege_env_e_dados(self) -> None:
        linhas = (ROOT / ".gitignore.jinja").read_text(encoding="utf-8").splitlines()
        self.assertIn(".env", linhas)
        self.assertIn("/dados/", linhas)


class GitignoreGeradoTests(unittest.TestCase):
    """Valida a Assumption A4 com uma cópia real do Copier."""

    def test_sistema_gerado_nasce_com_gitignore_renderizado(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            generated = render(Path(tempdir) / "aurora")
            gitignore = generated / ".gitignore"
            self.assertTrue(gitignore.is_file())
            linhas = gitignore.read_text(encoding="utf-8").splitlines()
            self.assertIn(".env", linhas)
            self.assertIn("/dados/", linhas)
            # O Copier renderiza e remove o sufixo .jinja — o arquivo com
            # sufixo não pode vazar para o destino.
            self.assertFalse((generated / ".gitignore.jinja").exists())


if __name__ == "__main__":
    unittest.main()
