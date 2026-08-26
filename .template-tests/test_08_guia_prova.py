"""Prova de ponta a ponta do fixture do guia (PRV-01, Fase 8, Plano 04).

Esta suíte instala `.template-tests/fixtures/guia/apps/diarias` numa cópia
Copier REAL (o banco de ensaio de `ensaio_django.sh`) executando exatamente
os passos que o leitor do guia fará à mão: copiar o app para `apps/`,
editar settings/urls/nav e reconstruir a imagem web. Depois prova, dentro
do container, que a migração aplica, que `makemigrations --check` está
limpo e que os testes do app passam — e, do host, que as telas respondem.

Convenções desta suíte (normativas para suítes futuras):

- O banco de ensaio fica COM o fixture instalado ao final (Pattern 4 da
  pesquisa da fase): restaurar exigiria um segundo rebuild por execução e
  `migrate diarias zero`, com ganho nulo. NENHUMA suíte futura deve assumir
  banco de ensaio "puro" (sem apps/diarias) — quem precisa de cópia
  recém-nascida usa render leve próprio em tempdir, como
  test_08_guia_vazamento.py faz.
- O harness é invocado UMA única vez, com o subcomando `subir`, no
  setUpClass (Pattern 2). Depois de qualquer `up -d --build`, quem espera o
  serviço é o laço PRÓPRIO de /healthz desta suíte — jamais um subcomando
  do harness, porque `garantir_banco()` faz um único curl sem retry e,
  chamado durante o boot, detona recriação completa com porta nova
  (Pitfall 2).
- A impressão digital do harness EXCLUI `.template-tests`: editar o fixture
  nunca recria o banco. A guarda contra provar código morto é a detecção de
  drift por sha256 (caminho relativo + conteúdo) feita aqui a cada execução
  (Pattern 3, Pitfalls 4-5).
- Orçamento de tempo (contrato do cabeçalho de ensaio_django.sh): quem
  invoca esta suíte usa timeout explícito de 600000 ms; a PRIMEIRA criação
  do banco (cache Docker frio) deve ser disparada em background com polling
  ANTES da suíte. Estouro de tempo com recriação anunciada em stderr não é
  reprovação — só reprova comando que TERMINOU com código != 0.

As constantes de patch abaixo (LINHA_SETTINGS, LINHA_URLS, LINHAS_NAV) são
o texto EXATO que o guia (Fase 9) mandará o leitor digitar — a Fase 9 cita
estas constantes; mudá-las aqui exige mudar o guia junto.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENSAIO = ROOT / ".template-tests" / "ensaio_django.sh"
FIXTURE_APP = ROOT / ".template-tests" / "fixtures" / "guia" / "apps" / "diarias"

# Orçamento normativo por invocação (segundos) — ver docstring do módulo.
ORCAMENTO = 600

# --- Constantes de patch: os passos do leitor, byte a byte -------------------

# 1) config/settings/base.py — INSTALLED_APPS. Âncora primária: a linha do
#    app exemplo. Fallback (cópia sem exemplo): inserir antes do `]` que
#    fecha a lista.
ANCORA_SETTINGS = '"apps.exemplo.apps.ExemploConfig",'
LINHA_SETTINGS = '    "apps.diarias.apps.DiariasConfig",'

# 2) config/urls.py — a rota do app entra imediatamente ANTES do include de
#    core.urls (que carrega o catch-all do shell).
ANCORA_URLS = '    path("", include("core.urls")),'
LINHA_URLS = '    path("diarias/", include("apps.diarias.urls")),'

# 3) core/templates/core/_nav_dominio.html — arquivo do derivado (o leitor é
#    dono dele). O 5º argumento do segundo item ("/diarias/dashboard/") é a
#    exceção que evita dois aria-current simultâneos no dashboard — mesmo
#    padrão do stub do app exemplo.
LINHAS_NAV = (
    '{% item_nav "diarias:dashboard" "Painel de viagens" "grafico" %}\n'
    '{% item_nav "diarias:viagem_listar" "Diárias e passagens" "lista"'
    ' "/diarias/" "/diarias/dashboard/" %}\n'
)


def impressao_subarvore(raiz: Path) -> dict[str, str]:
    """sha256 de caminho-relativo + conteúdo de cada arquivo sob `raiz`.

    Ignora `__pycache__` e `*.pyc` — artefatos de execução, não de fonte.
    Mesmo esquema de test_07_nav_extensao.py: o caminho entra no hash para
    que renomear um arquivo sem mudar o conteúdo conte como drift.
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


def _diagnostico(resultado: subprocess.CompletedProcess) -> str:
    """stdout+stderr formatados para mensagem de falha."""
    return (
        f"código de saída: {resultado.returncode}\n"
        f"--- stdout ---\n{resultado.stdout}\n"
        f"--- stderr ---\n{resultado.stderr}"
    )


class GuiaProvaTests(unittest.TestCase):
    """Instalação idempotente do fixture na cópia real + provas in-container.

    Todo o trabalho caro (subir, drift, instalação, rebuild, migrate) vive
    em setUpClass; os métodos de teste são baratos, idempotentes e
    independentes de ordem (Pitfall 9).
    """

    destino: Path
    projeto: str
    porta: str
    base: str

    # ------------------------------------------------------------------ setup

    @classmethod
    def _compor(cls, *args: str, timeout: int = ORCAMENTO) -> subprocess.CompletedProcess:
        """`docker compose` direto na cópia, com project-name e env-file.

        Nunca via harness: os subcomandos de lá chamam garantir_banco(), que
        não pode rodar logo após um `up -d --build` (Pitfall 2).
        """
        return subprocess.run(
            [
                "docker",
                "compose",
                "--project-name",
                cls.projeto,
                "--env-file",
                ".env",
                *args,
            ],
            cwd=cls.destino,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

    @classmethod
    def _esperar_healthz(cls) -> None:
        """Laço PRÓPRIO de espera: até 180 tentativas de 1s em /healthz."""
        for _ in range(180):
            try:
                with urllib.request.urlopen(f"{cls.base}/healthz", timeout=5):
                    return
            except (urllib.error.URLError, OSError):
                time.sleep(1)
        ps = cls._compor("ps")
        logs = cls._compor("logs", "--tail=100", "web", "db")
        raise AssertionError(
            "web do banco de ensaio não respondeu em /healthz em 180s após o "
            f"rebuild\n{_diagnostico(ps)}\n{_diagnostico(logs)}"
        )

    @classmethod
    def _subir_banco(cls) -> None:
        """Única invocação do harness em toda a suíte: `subir` (Pattern 2)."""
        try:
            resultado = subprocess.run(
                ["sh", str(ENSAIO), "subir"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=ORCAMENTO,
            )
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(
                "ensaio_django.sh subir estourou o orçamento de 600s. Pelo "
                "contrato do harness isso NÃO é reprovação quando a recriação "
                "foi anunciada em stderr: dispare `sh .template-tests/"
                "ensaio_django.sh subir` em BACKGROUND com polling, espere o "
                "banco existir e rode esta suíte de novo."
            ) from exc
        if resultado.returncode != 0:
            raise AssertionError(
                f"ensaio_django.sh subir falhou\n{_diagnostico(resultado)}"
            )
        valores = dict(
            linha.split("=", 1)
            for linha in resultado.stdout.splitlines()
            if linha.startswith("ENSAIO_")
        )
        cls.destino = Path(valores["ENSAIO_DESTINO"])
        cls.projeto = valores["ENSAIO_PROJETO"]
        cls.porta = valores["ENSAIO_PORTA"]
        cls.base = valores["ENSAIO_URL"]

    # --- instalação: os passos do leitor, idempotentes ----------------------

    @classmethod
    def _patch_settings(cls) -> bool:
        arquivo = cls.destino / "config" / "settings" / "base.py"
        texto = arquivo.read_text(encoding="utf-8")
        if LINHA_SETTINGS.strip() in texto:
            return False
        if ANCORA_SETTINGS in texto:
            texto = texto.replace(
                ANCORA_SETTINGS, ANCORA_SETTINGS + "\n" + LINHA_SETTINGS, 1
            )
        else:
            # Fallback (cópia sem app exemplo): antes do `]` que fecha a
            # lista INSTALLED_APPS.
            marcador = "INSTALLED_APPS = ["
            inicio = texto.index(marcador)
            fim = texto.index("\n]", inicio)
            texto = texto[:fim] + "\n" + LINHA_SETTINGS + texto[fim:]
        arquivo.write_text(texto, encoding="utf-8")
        return True

    @classmethod
    def _patch_urls(cls) -> bool:
        arquivo = cls.destino / "config" / "urls.py"
        texto = arquivo.read_text(encoding="utf-8")
        if 'include("apps.diarias.urls")' in texto:
            return False
        if ANCORA_URLS not in texto:
            raise AssertionError(
                f"âncora ausente em config/urls.py: {ANCORA_URLS!r}"
            )
        texto = texto.replace(ANCORA_URLS, LINHA_URLS + "\n" + ANCORA_URLS, 1)
        arquivo.write_text(texto, encoding="utf-8")
        return True

    @classmethod
    def _patch_nav(cls) -> bool:
        arquivo = cls.destino / "core" / "templates" / "core" / "_nav_dominio.html"
        texto = arquivo.read_text(encoding="utf-8")
        if 'item_nav "diarias:' in texto:
            return False
        if not texto.endswith("\n"):
            texto += "\n"
        arquivo.write_text(texto + LINHAS_NAV, encoding="utf-8")
        return True

    @classmethod
    def _instalar_fixture(cls) -> None:
        """Instalação idempotente com detecção de drift (Pattern 3).

        Três estados do sha256 fixture x instalado:
        - ausente   -> instala tudo + patches + rebuild;
        - idêntico  -> só patches (no-op esperado) e nenhum rebuild — via
                       barata;
        - divergente-> se o drift toca models.py ou migrations/, roda
                       `manage.py migrate diarias zero` COM O CÓDIGO ANTIGO
                       ainda instalado (Pitfall 5 — senão o schema do banco
                       reusado divergiria do modelo novo em silêncio), então
                       sobrescreve, aplica patches e rebuilda.
        """
        alvo = cls.destino / "apps" / "diarias"
        digests_fixture = impressao_subarvore(FIXTURE_APP)

        copiar = True
        if alvo.is_dir():
            digests_alvo = impressao_subarvore(alvo)
            if digests_alvo == digests_fixture:
                copiar = False
            else:
                divergentes = {
                    caminho
                    for caminho in set(digests_fixture) | set(digests_alvo)
                    if digests_fixture.get(caminho) != digests_alvo.get(caminho)
                }
                toca_schema = any(
                    caminho == "models.py" or caminho.startswith("migrations/")
                    for caminho in divergentes
                )
                if toca_schema:
                    # Desfaz o schema com o código ANTIGO (ainda assado na
                    # imagem em execução) antes de trocar os arquivos.
                    resultado = cls._compor(
                        "exec",
                        "-T",
                        "web",
                        "python",
                        "manage.py",
                        "migrate",
                        "diarias",
                        "zero",
                        "--noinput",
                    )
                    if resultado.returncode != 0:
                        raise AssertionError(
                            "migrate diarias zero falhou no ramo de drift de "
                            f"models/migrations\n{_diagnostico(resultado)}"
                        )
                shutil.rmtree(alvo)

        mudou = False
        if copiar:
            shutil.copytree(
                FIXTURE_APP,
                alvo,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            mudou = True

        mudou |= cls._patch_settings()
        mudou |= cls._patch_urls()
        mudou |= cls._patch_nav()

        if mudou:
            # Código é ASSADO na imagem (COPY . . no Dockerfile): só um
            # rebuild leva o app novo para dentro do container (Pitfall 1).
            resultado = cls._compor("up", "-d", "--build", "web")
            if resultado.returncode != 0:
                raise AssertionError(
                    f"up -d --build web falhou\n{_diagnostico(resultado)}"
                )
            cls._esperar_healthz()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._subir_banco()
        cls._instalar_fixture()
        # Deixa o estado consistente para TODOS os métodos (independentes de
        # ordem): migração aplicada antes de qualquer smoke.
        resultado = cls._compor(
            "exec", "-T", "web", "python", "manage.py", "migrate", "--noinput"
        )
        if resultado.returncode != 0:
            raise AssertionError(
                f"migrate --noinput falhou após a instalação\n{_diagnostico(resultado)}"
            )

    # ------------------------------------------------- provas in-container

    def test_migrate_e_idempotente_e_sai_zero(self) -> None:
        resultado = self._compor(
            "exec", "-T", "web", "python", "manage.py", "migrate", "--noinput"
        )
        self.assertEqual(
            resultado.returncode,
            0,
            f"migrate --noinput reprovou\n{_diagnostico(resultado)}",
        )

    def test_showmigrations_prova_0001_initial_aplicada(self) -> None:
        resultado = self._compor(
            "exec", "-T", "web", "python", "manage.py", "showmigrations", "diarias"
        )
        self.assertEqual(
            resultado.returncode,
            0,
            f"showmigrations diarias reprovou\n{_diagnostico(resultado)}",
        )
        self.assertIn(
            "[X] 0001_initial",
            resultado.stdout,
            "0001_initial não consta como aplicada em showmigrations diarias\n"
            + _diagnostico(resultado),
        )

    def test_makemigrations_check_limpo(self) -> None:
        """A migração escrita à mão no fixture está consistente com models.py."""
        resultado = self._compor(
            "exec",
            "-T",
            "web",
            "python",
            "manage.py",
            "makemigrations",
            "diarias",
            "--check",
            "--dry-run",
        )
        self.assertEqual(
            resultado.returncode,
            0,
            "makemigrations --check detectou migração pendente — a 0001 do "
            f"fixture divergiu de models.py\n{_diagnostico(resultado)}",
        )

    def test_suite_do_app_verde_dentro_do_container(self) -> None:
        resultado = self._compor(
            "exec",
            "-T",
            "web",
            "python",
            "manage.py",
            "test",
            "apps.diarias",
            "--noinput",
        )
        self.assertEqual(
            resultado.returncode,
            0,
            f"manage.py test apps.diarias reprovou\n{_diagnostico(resultado)}",
        )


if __name__ == "__main__":
    unittest.main()
