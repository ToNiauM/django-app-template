"""Integrações Copier para a stack isolada e backup containerizado."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"


def render(destination: Path) -> Path:
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
            str(ROOT),
            str(destination),
        ],
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return destination


class BackupComposeTemplateTests(unittest.TestCase):
    def test_rendered_compose_is_isolated_and_backup_is_internal(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            generated = render(Path(tempdir) / "aurora")
            shutil.copy(generated / ".env.example", generated / ".env")
            completed = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(generated / "compose.yml"),
                    "--env-file",
                    str(generated / ".env"),
                    "config",
                    "--format",
                    "json",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            compose = json.loads(completed.stdout)
            self.assertEqual(compose["name"], "aurora")
            self.assertEqual(set(compose["services"]), {"db", "web", "backup"})
            self.assertFalse(compose["volumes"]["pgdata"].get("external", False))
            self.assertNotIn("ports", compose["services"]["db"])
            backup = compose["services"]["backup"]
            self.assertNotIn("ports", backup)
            self.assertTrue(backup["init"])
            self.assertEqual(
                backup["depends_on"]["db"]["condition"], "service_healthy"
            )
            self.assertEqual(backup["environment"]["DB_HOST"], "db")
            port = compose["services"]["web"]["ports"][0]
            self.assertEqual(port["host_ip"], "127.0.0.1")
            self.assertEqual(str(port["published"]), "8123")
            self.assertEqual(port["target"], 8000)

    def test_rendered_backup_configuration_keeps_only_placeholder_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            generated = render(Path(tempdir) / "aurora")
            answers = (generated / ".copier-answers.yml").read_text(encoding="utf-8")
            self.assertNotRegex(
                answers,
                r"(?m)^(?:SECRET_KEY|POSTGRES_PASSWORD|R2_ACCESS_KEY_ID|R2_SECRET_ACCESS_KEY):",
            )
            values = dict(
                line.split("=", 1)
                for line in (generated / ".env.example").read_text(encoding="utf-8").splitlines()
                if "=" in line and not line.lstrip().startswith("#")
            )
            for key in (
                "SECRET_KEY",
                "POSTGRES_PASSWORD",
                "R2_ACCESS_KEY_ID",
                "R2_SECRET_ACCESS_KEY",
            ):
                self.assertTrue(values[key].startswith("replace-with-"), key)
            self.assertEqual(values["BACKUP_HORA"], "03")
            self.assertEqual(values["BACKUP_MINUTO"], "00")
            self.assertEqual(values["BACKUP_RETENCAO_DIARIA"], "7")
            self.assertEqual(values["BACKUP_RETENCAO_SEMANAL"], "4")
            self.assertEqual(values["BACKUP_DIA_SEMANAL"], "7")

    def test_backup_image_and_entrypoint_validate_the_operational_boundary(self) -> None:
        dockerfile = (ROOT / "ops/backup/Dockerfile").read_text(encoding="utf-8")
        entrypoint = ROOT / "ops/backup/entrypoint.sh"
        self.assertIn("FROM postgres:17-alpine", dockerfile)
        self.assertIn("PIN_RCLONE_VERSION=v1.68.2", dockerfile)
        self.assertIn("sha256sum -c", dockerfile)
        self.assertTrue(entrypoint.is_file())
        self.assertIn("crond -f", entrypoint.read_text(encoding="utf-8"))
        subprocess.run(["sh", "-n", str(entrypoint)], check=True)
        for invalid_environment in (
            {"BACKUP_HORA": "24"},
            {"BACKUP_MINUTO": "60"},
            {"BACKUP_RETENCAO_DIARIA": "0"},
            {"BACKUP_RETENCAO_SEMANAL": "abc"},
            {"BACKUP_DIA_SEMANAL": "8"},
        ):
            environment = {
                "BACKUP_HORA": "03",
                "BACKUP_MINUTO": "00",
                "BACKUP_RETENCAO_DIARIA": "7",
                "BACKUP_RETENCAO_SEMANAL": "4",
                "BACKUP_DIA_SEMANAL": "7",
                **invalid_environment,
            }
            result = subprocess.run(
                ["sh", str(entrypoint)],
                env=environment,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0, invalid_environment)

    def test_dump_retention_and_operational_test_are_confined(self) -> None:
        backup = ROOT / "ops/backup/backup.sh"
        retention = ROOT / "ops/backup/retencao.sh"
        operational_test = ROOT / "ops/backup/testar_retencao.sh"
        for script in (backup, retention, operational_test):
            self.assertTrue(script.is_file(), script)
            subprocess.run(["sh", "-n", str(script)], check=True)
            self.assertIn("set -eu", script.read_text(encoding="utf-8"))

        backup_source = backup.read_text(encoding="utf-8")
        retention_source = retention.read_text(encoding="utf-8")
        test_source = operational_test.read_text(encoding="utf-8")
        self.assertIn('pg_dump --format=custom', backup_source)
        self.assertIn('"/tmp/${SISTEMA_SLUG}_${DATA}.dump"', backup_source)
        self.assertIn('"r2:${R2_BUCKET}/daily/"', backup_source)
        self.assertIn('"r2:${R2_BUCKET}/weekly/"', backup_source)
        self.assertIn('"${BACKUP_DIA_SEMANAL}"', backup_source)
        self.assertIn('manter_ultimos "daily" "${BACKUP_RETENCAO_DIARIA}"', backup_source)
        self.assertIn('manter_ultimos "weekly" "${BACKUP_RETENCAO_SEMANAL}"', backup_source)
        self.assertEqual(retention_source.count("manter_ultimos()"), 1)
        self.assertIn("--format tp", retention_source)
        self.assertIn("sort -r", retention_source)
        self.assertIn("tail -n", retention_source)
        self.assertIn("rclone delete", retention_source)
        self.assertIn("trap limpar EXIT", test_source)
        self.assertIn("${SISTEMA_SLUG}_retencao_$$", test_source)
        self.assertIn("daily|weekly", test_source)
        self.assertIn("rclone purge", test_source)


if __name__ == "__main__":
    unittest.main()
