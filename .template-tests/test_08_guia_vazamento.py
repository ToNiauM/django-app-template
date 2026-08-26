"""Teste negativo de vazamento de domínio (PRV-03, Fase 8).

O fixture do guia (`.template-tests/fixtures/guia/apps/diarias/`) é a fonte
da verdade do exemplo completo — e NUNCA pode chegar ao template renderizado
nem à cópia gerada. Este módulo prova as duas direções:

1. Cópia recém-nascida (``copier copy`` leve, em tempdir, sem Docker) não
   contém ``apps/diarias`` — nas DUAS variantes de ``incluir_app_exemplo``.
2. Nenhum byte de arquivo do fixture aparece em nenhum arquivo da cópia.
3. A árvore do TEMPLATE (``git ls-files``) não lista o domínio fora de
   ``.template-tests/fixtures/``.

Por que as asserções são ESTRUTURAIS (diretório ausente, conjunto exato de
entradas em ``apps/``, interseção de hashes de conteúdo) e nunca grep da
palavra "diarias": na Fase 9, ``docs/guia/`` citará ``apps/diarias``
legitimamente em prosa e cercas de código — um grep textual apodreceria
naquele dia (Pitfall 8 da pesquisa). Estrutura não apodrece: o diretório e
os bytes do fixture continuam proibidos na cópia para sempre.

Por que o banco de ensaio compartilhado (o harness shell de ensaio Django
em ``.template-tests/``) fica DE FORA: a suíte de prova positiva instala o
fixture na cópia do banco de ensaio e o deixa lá por design (Pattern 4 da
pesquisa) — aquele estado é legítimo. Olhar para ele aqui condenaria uma
instalação correta. Este módulo usa renders leves próprios em
``tempfile.TemporaryDirectory()``, em segundos, sem Docker e sem importar
nem invocar o harness.
"""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"
FIXTURE = ROOT / ".template-tests/fixtures/guia"


def render(destination: Path, *, incluir_app_exemplo: bool) -> Path:
    """Renderiza uma variante real, sempre do working tree.

    --vcs-ref=HEAD: com uma tag de release no repositório (v0.2.0 publicada),
    o Copier copiaria por padrão a última tag — o teste precisa do estado
    COMMITADO atual do template. Consequência operacional: os arquivos do
    fixture (planos 08-01/08-02) precisam estar commitados antes desta suíte
    rodar, senão a interseção de bytes passaria em vácuo.
    """
    subprocess.run(
        [
            str(COPIER),
            "copy",
            "--defaults",
            "--vcs-ref=HEAD",
            "--data",
            "sistema_nome=Sistema Vazamento",
            "--data",
            "sistema_slug=vazamento",
            "--data",
            "sistema_hostname=vazamento.exemplo.gov.br",
            "--data",
            "sistema_porta=8789",
            "--data",
            "sistema_banco=vazamento",
            "--data",
            "sistema_sigla=SV",
            "--data",
            "cor_primaria=#7c2d12",
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


def hashes_de_conteudo(raiz: Path, *, ignorar_vazios: bool = False) -> set[str]:
    """sha256 SÓ do conteúdo (bytes puros) de cada arquivo sob ``raiz``.

    Diferente de ``impressao_subarvore()`` (test_07_nav_extensao.py), que
    embute o caminho relativo no hash: com o caminho embutido, árvores
    distintas nunca colidiriam e a interseção fixture×cópia passaria em vácuo
    — a pesquisa aponta essa pegadinha explicitamente. Aqui o hash é do
    conteúdo puro, para que um arquivo do fixture copiado para QUALQUER
    caminho da cópia seja flagrado.

    Ignora ``__pycache__``/``*.pyc`` (artefatos de execução, não de fonte).

    ``ignorar_vazios`` existe para o lado do FIXTURE: arquivos de 0 bytes
    (``__init__.py`` de pacote) não carregam nenhum byte de domínio, e o
    sha256 do conteúdo vazio colide com qualquer ``__init__.py`` vazio
    legítimo da cópia (``apps/__init__.py`` etc.) — seria um vermelho falso
    permanente, não uma detecção de vazamento.
    """
    digests: set[str] = set()
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file():
            continue
        if "__pycache__" in caminho.parts or caminho.suffix == ".pyc":
            continue
        conteudo = caminho.read_bytes()
        if ignorar_vazios and not conteudo:
            continue
        digests.add(hashlib.sha256(conteudo).hexdigest())
    return digests


class GuiaVazamentoTests(unittest.TestCase):
    def hashes_do_fixture(self) -> set[str]:
        """Hashes de conteúdo do fixture, com guarda contra falso verde."""
        self.assertTrue(
            (FIXTURE / "apps" / "diarias").is_dir(),
            "fixture do guia ausente — a interseção de bytes passaria em vácuo",
        )
        hashes = hashes_de_conteudo(FIXTURE, ignorar_vazios=True)
        # Guarda contra falso verde por fixture ausente/esvaziado: o app
        # completo tem mais de uma dezena de arquivos com conteúdo real.
        self.assertGreaterEqual(
            len(hashes),
            10,
            f"fixture com só {len(hashes)} arquivos não-vazios — "
            "interseção de bytes deixaria de provar qualquer coisa",
        )
        return hashes

    def exigir_nenhum_byte_do_fixture(self, copia: Path) -> None:
        hashes_fixture = self.hashes_do_fixture()
        hashes_copia = hashes_de_conteudo(copia)
        vazados = hashes_fixture & hashes_copia
        self.assertFalse(
            vazados,
            f"{len(vazados)} arquivo(s) do fixture presentes byte a byte na "
            f"cópia recém-nascida: {sorted(vazados)[:5]}",
        )

    def test_variante_com_exemplo_nasce_sem_o_dominio(self) -> None:
        """incluir_app_exemplo=True: apps/ contém EXATAMENTE o núcleo + exemplo."""
        with tempfile.TemporaryDirectory() as tmp:
            copia = render(Path(tmp) / "com-exemplo", incluir_app_exemplo=True)

            self.assertFalse(
                (copia / "apps" / "diarias").exists(),
                "apps/diarias vazou para a cópia gerada (variante com exemplo)",
            )
            nomes = sorted(p.name for p in (copia / "apps").iterdir())
            # Conjunto EXATO, não só ausência: qualquer entrada nova em apps/
            # (domínio, lixo de build, outro app) reprova aqui.
            self.assertEqual(
                nomes,
                ["__init__.py", "exemplo"],
                f"apps/ da cópia com exemplo deveria ter exatamente o núcleo: {nomes}",
            )
            self.exigir_nenhum_byte_do_fixture(copia)

    def test_variante_sem_exemplo_nasce_sem_o_dominio(self) -> None:
        """incluir_app_exemplo=False: apps/ contém EXATAMENTE __init__.py."""
        with tempfile.TemporaryDirectory() as tmp:
            copia = render(Path(tmp) / "sem-exemplo", incluir_app_exemplo=False)

            self.assertFalse(
                (copia / "apps" / "diarias").exists(),
                "apps/diarias vazou para a cópia gerada (variante sem exemplo)",
            )
            nomes = sorted(p.name for p in (copia / "apps").iterdir())
            self.assertEqual(
                nomes,
                ["__init__.py"],
                f"apps/ da cópia sem exemplo deveria ter só o __init__.py: {nomes}",
            )
            self.exigir_nenhum_byte_do_fixture(copia)

    def test_arvore_do_template_nao_lista_o_dominio_fora_do_fixture(self) -> None:
        """PRV-03, direção do template: git ls-files limpo fora do fixture."""
        saida = subprocess.run(
            ["git", "ls-files"],
            check=True,
            cwd=ROOT,
            text=True,
            capture_output=True,
        ).stdout
        caminhos = saida.splitlines()
        self.assertTrue(caminhos, "git ls-files não devolveu nada — repo inválido")

        suspeitos = [
            caminho
            for caminho in caminhos
            if not caminho.startswith(".template-tests/fixtures/")
            and (caminho.startswith("apps/diarias") or "/diarias/" in caminho)
        ]
        self.assertEqual(
            suspeitos,
            [],
            "o domínio do guia aparece na árvore do template fora de "
            f".template-tests/fixtures/: {suspeitos}",
        )

        # Guarda simétrica: o fixture ESTÁ rastreado — se sumir do git, o
        # render com --vcs-ref=HEAD nunca o veria e este módulo inteiro
        # passaria em vácuo.
        rastreados_do_fixture = [
            caminho
            for caminho in caminhos
            if caminho.startswith(".template-tests/fixtures/guia/apps/diarias/")
        ]
        self.assertGreaterEqual(
            len(rastreados_do_fixture),
            10,
            "fixture do guia não está (ou está só parcialmente) commitado",
        )


if __name__ == "__main__":
    unittest.main()
