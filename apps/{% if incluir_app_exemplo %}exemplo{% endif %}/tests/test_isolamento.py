"""Testes de arquitetura para validar o desacoplamento estrito e isolamento do app exemplo (EX-04 / D-33)."""

import ast
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class IsolamentoAppExemploTest(SimpleTestCase):
    def test_core_nao_importa_apps_exemplo(self):
        """Varre todos os arquivos Python do app core e garante zero imports de apps.exemplo."""
        core_dir = Path(settings.BASE_DIR) / "core"
        arquivos_violadores = []

        for arquivo_py in core_dir.rglob("*.py"):
            try:
                conteudo = arquivo_py.read_text(encoding="utf-8")
                arvore = ast.parse(conteudo, filename=str(arquivo_py))

                for no in ast.walk(arvore):
                    if isinstance(no, ast.Import):
                        for alias in no.names:
                            if "apps.exemplo" in alias.name or "exemplo" in alias.name:
                                arquivos_violadores.append((str(arquivo_py), alias.name))
                    elif isinstance(no, ast.ImportFrom):
                        if no.module and ("apps.exemplo" in no.module or no.module.startswith("exemplo")):
                            arquivos_violadores.append((str(arquivo_py), no.module))
            except Exception as e:
                self.fail(f"Falha ao analisar arquivo {arquivo_py}: {e}")

        self.assertEqual(
            len(arquivos_violadores),
            0,
            f"O core/ possui dependências reversas proibidas para apps.exemplo: {arquivos_violadores}",
        )

    def test_config_possui_apenas_pontos_de_integracao_documentados(self):
        """Valida que apenas config/settings/base.py e config/urls.py referenciam apps.exemplo."""
        config_dir = Path(settings.BASE_DIR) / "config"
        arquivos_com_referencia = []

        for arquivo_py in config_dir.rglob("*.py"):
            conteudo = arquivo_py.read_text(encoding="utf-8")
            if "apps.exemplo" in conteudo:
                arquivos_com_referencia.append(arquivo_py.name)

        # Apenas base.py e urls.py devem conter menções a apps.exemplo
        self.assertCountEqual(
            arquivos_com_referencia,
            ["base.py", "urls.py"],
            f"Arquivos inesperados em config/ referenciando apps.exemplo: {arquivos_com_referencia}",
        )
