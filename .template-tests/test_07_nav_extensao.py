"""Contratos executáveis dos critérios 5, 6 e 7 da Fase 7 (Plano 03): o
ponto de extensão da navegação (`_nav.html` estático + `_nav_dominio.html`
protegido por `_skip_if_exists` + `{% item_nav %}`).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPIER = ROOT / ".venv-template" / "bin" / "copier"


def render(destination: Path, *, incluir_app_exemplo: bool) -> Path:
    """Renderiza uma variante real, sempre do working tree.

    --vcs-ref=HEAD: com uma tag de release no repositório, o Copier copiaria
    por padrão a última tag — o teste precisa do estado atual do template.
    """
    subprocess.run(
        [
            str(COPIER),
            "copy",
            "--defaults",
            "--vcs-ref=HEAD",
            "--data",
            "sistema_nome=Sistema Extensao",
            "--data",
            "sistema_slug=extensao",
            "--data",
            "sistema_hostname=extensao.exemplo.gov.br",
            "--data",
            "sistema_porta=8321",
            "--data",
            "sistema_banco=extensao",
            "--data",
            "sistema_sigla=SEX",
            "--data",
            "cor_primaria=#1e40af",
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


def impressao_subarvore(raiz: Path) -> dict[str, str]:
    """sha256 de caminho-relativo + conteúdo de cada arquivo sob `raiz`.

    Ignora `__pycache__` e `*.pyc` — artefatos de execução, não de fonte.
    """
    digests: dict[str, str] = {}
    for caminho in sorted(raiz.rglob("*")):
        if not caminho.is_file():
            continue
        if "__pycache__" in caminho.parts or caminho.suffix == ".pyc":
            continue
        relativo = caminho.relative_to(raiz).as_posix()
        hasher = hashlib.sha256()
        hasher.update(relativo.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(caminho.read_bytes())
        digests[relativo] = hasher.hexdigest()
    return digests


class ExtensaoDeNavegacaoTests(unittest.TestCase):
    def test_nav_do_nucleo_e_identico_nas_duas_variantes(self) -> None:
        """Critério 5: `_nav.html` é do núcleo e estático — nada nele depende
        de `incluir_app_exemplo`, e por isso o derivado nunca precisa editá-lo.

        A comparação é ENTRE as duas variantes geradas, não de um arquivo
        consigo mesmo. A versão anterior deste teste lia os bytes de
        `_nav.html`, escrevia em OUTRO arquivo (`_nav_dominio.html`) e depois
        assere que `_nav.html` não mudou — nenhum código tocava `_nav.html`
        entre as duas leituras, então a asserção não podia falhar nem se o
        ponto de extensão inteiro fosse removido (WR-07). Esta pode: devolver
        um `{% if incluir_app_exemplo %}` para dentro do `_nav.html` a quebra.
        """
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            sem_exemplo = render(raiz / "sem-exemplo", incluir_app_exemplo=False)
            com_exemplo = render(raiz / "com-exemplo", incluir_app_exemplo=True)

            nav_sem = (sem_exemplo / "core/templates/core/_nav.html").read_bytes()
            nav_com = (com_exemplo / "core/templates/core/_nav.html").read_bytes()

            self.assertEqual(
                nav_com,
                nav_sem,
                "_nav.html divergiu entre as variantes — deixou de ser do "
                "núcleo e passou a depender de incluir_app_exemplo",
            )

            # _nav.html não referencia nenhuma rota fora de core: — não há
            # necessidade de editá-lo para acomodar um domínio.
            texto = nav_sem.decode("utf-8")
            rotas = re.findall(r'item_nav\s+"([a-z0-9_]+):', texto)
            self.assertTrue(rotas, "_nav.html não chamou item_nav nenhuma vez")
            self.assertTrue(
                all(app == "core" for app in rotas),
                f"_nav.html referencia rota fora de core: {rotas}",
            )
            self.assertNotIn("exemplo:", texto)

            # WR-10: a inserção do arquivo do derivado é tolerante. Um
            # {% include %} literal levantaria TemplateDoesNotExist e daria 500
            # em toda página autenticada quando o mantenedor apagasse o arquivo
            # que é dele.
            self.assertIn("{% nav_dominio %}", texto)
            self.assertNotIn("{% include", texto)

    def test_stub_semeado_declara_a_excecao_que_evita_dois_itens_ativos(self) -> None:
        """G-01: sem a exceção, `/exemplo/dashboard/` acende DOIS itens — o
        Dashboard por correspondência exata e o Itens (CRUD) pelo prefixo
        `/exemplo/`. Este gate impede que um `copier update` futuro reintroduza
        a colisão pela porta do stub que o próprio núcleo semeia."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = render(Path(tmp) / "sis", incluir_app_exemplo=True)
            conteudo = (
                destino / "core/templates/core/_nav_dominio.html"
            ).read_text(encoding="utf-8")

            linhas = [
                linha
                for linha in conteudo.splitlines()
                if 'item_nav "exemplo:item_listar"' in linha
            ]
            self.assertEqual(
                len(linhas), 1, f"esperava um item_listar no stub, achei {linhas}"
            )
            self.assertIn(
                '"/exemplo/"',
                linhas[0],
                "o prefixo sumiu do stub — rota-filha sem item próprio deixaria "
                "de acender nenhum item",
            )
            self.assertIn(
                '"/exemplo/dashboard/"',
                linhas[0],
                "o item do prefixo não excetua /exemplo/dashboard/: dois itens "
                "acendem juntos no dashboard",
            )

            # O contrato do topo é o que ensina o parâmetro a todo mantenedor
            # de derivado que for criar um item — é por onde o conserto se
            # propaga para os sistemas gerados.
            self.assertIn("excecoes", conteudo)

    def test_remover_itens_do_exemplo_nao_toca_nenhum_arquivo_do_nucleo(self) -> None:
        """Critério 6, prova literal: apagar os dois itens do exemplo de
        _nav_dominio.html deixa a subárvore core/ byte a byte idêntica."""
        with tempfile.TemporaryDirectory() as tmp:
            destino = render(Path(tmp) / "sis", incluir_app_exemplo=True)
            core_dir = destino / "core"

            antes = impressao_subarvore(core_dir)

            dominio = destino / "core/templates/core/_nav_dominio.html"
            conteudo = dominio.read_text(encoding="utf-8")
            self.assertIn("exemplo:dashboard", conteudo)
            self.assertIn("exemplo:item_listar", conteudo)

            linhas_restantes = [
                linha
                for linha in conteudo.splitlines(keepends=True)
                if 'item_nav "exemplo:dashboard"' not in linha
                and 'item_nav "exemplo:item_listar"' not in linha
            ]
            dominio.write_text("".join(linhas_restantes), encoding="utf-8")

            depois = impressao_subarvore(core_dir)

            divergentes = sorted(
                caminho
                for caminho in set(antes) | set(depois)
                if antes.get(caminho) != depois.get(caminho)
            )
            # Só o próprio _nav_dominio.html pode ter mudado — é o arquivo do
            # derivado; nenhum outro arquivo de core/ pode divergir.
            self.assertEqual(
                divergentes,
                ["templates/core/_nav_dominio.html"],
                f"caminhos divergentes além do esperado: {divergentes}",
            )

            self.assertTrue(dominio.exists())
            self.assertNotIn("exemplo:", dominio.read_text(encoding="utf-8"))

    def test_copier_yml_protege_os_arquivos_do_derivado(self) -> None:
        conteudo = (ROOT / "copier.yml").read_text(encoding="utf-8")
        self.assertIn("_skip_if_exists:", conteudo)
        self.assertIn("core/templates/core/_nav_dominio.html", conteudo)
        self.assertIn("core/static/src/dominio.css", conteudo)


if __name__ == "__main__":
    unittest.main()
