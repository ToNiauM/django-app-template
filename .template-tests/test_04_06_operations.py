"""Integração Copier para restore, Nginx e runbook portáveis."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"


class PortableOperationsTemplateTests(unittest.TestCase):
    def render(self, destination: Path) -> Path:
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
                ".",
                str(destination),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return destination

    def test_rendered_vhost_terminates_tls_at_loopback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = self.render(Path(directory) / "aurora")
            vhost = (generated / "ops" / "nginx" / "aurora.conf").read_text(
                encoding="utf-8"
            )

        self.assertIn("server_name aurora.exemplo.gov.br", vhost)
        self.assertIn("listen 443 ssl", vhost)
        self.assertIn("http://127.0.0.1:8123", vhost)
        self.assertIn("return 301 https://$host$request_uri", vhost)
        for header in (
            "proxy_set_header Host $host",
            "proxy_set_header X-Real-IP $remote_addr",
            "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for",
            "proxy_set_header X-Forwarded-Proto $scheme",
        ):
            self.assertIn(header, vhost)

    def test_rendered_runbook_uses_containerized_portable_steps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = self.render(Path(directory) / "aurora")
            runbook = (generated / "ops" / "MIGRACAO.md").read_text(encoding="utf-8")
            readme = (generated / "README.md").read_text(encoding="utf-8")

        for token in (
            "cp .env.example .env",
            "pg_restore --clean --if-exists --no-owner",
            "docker compose up -d",
            "docker compose exec -T web python manage.py migrate --noinput",
            "/healthz",
            "nginx -t",
            "certbot",
            "DNS",
            "ensaio_restore_local.sh",
        ):
            self.assertIn(token, runbook)
        self.assertIn("ops/MIGRACAO.md", readme)
        self.assertNotIn("external: true", runbook)
        self.assertNotIn("pca", runbook.lower())


if __name__ == "__main__":
    unittest.main()
