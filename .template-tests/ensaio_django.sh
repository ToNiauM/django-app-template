#!/bin/sh
# Banco de ensaio: ferramenta reutilizável, não suíte — o nome não começa com
# `test_` de propósito, para que `python3 -m unittest discover -p 'test_*.py'`
# e o inventário de suítes do README não a confundam com uma regressão.
#
# Por que existe: o checkout do template NÃO é um projeto Django rodável — não
# há `compose.yml` (só `compose.yml.jinja`), nem `config/settings/base.py` (só
# `.py.jinja`), nem `config/urls.py`, nem container `web` para `sistema_base`.
# Um `docker compose exec -T web python manage.py test …` solto em
# /opt/sistema_base ERRA ("no configuration file provided") em vez de falhar —
# o pior resultado possível num gate, porque parece que rodou. A única forma
# honesta de exercitar Django nesta fase é DENTRO de uma cópia gerada — é isso
# que este script automatiza: renderiza uma cópia real com --vcs-ref=HEAD, sobe
# o Compose dela, publica a porta e roda qualquer alvo Django lá dentro.
#
# Orçamento de tempo (normativo para todos os planos da Fase 07 — não só para a
# primeira criação): toda mudança de código no working tree invalida a
# impressão digital, e o `subir`/`testar` seguinte RECRIA o banco: `copier
# copy`, `docker compose up -d --build` (que pode incluir `pip install`,
# `apt-get` e `npx tailwindcss@3.4.17` no build da imagem — cache Docker frio),
# espera de `/healthz` (até 180 tentativas de 1s) e `migrate`. Isso NÃO cabe no
# timeout padrão de 120s de quem invoca este script. Regra: quem chama
# subir/testar/derrubar usa timeout explícito de 600000 ms; a PRIMEIRA criação
# (cache Docker frio) roda em BACKGROUND com polling, porque pode passar de
# 600s sozinha. O laço de `/healthz` tem teto de 180s e imprime `compose ps` +
# `compose logs --tail=100 web db` em stderr antes de abortar — esse teto é do
# laço, não do build que o antecede. Reúso de banco (sem mudança de código) é
# de segundos — é para isso que a impressão digital existe. Fallback: se uma
# invocação anunciar recriação em stderr e AINDA ASSIM estourar 600000 ms, isso
# NÃO é reprovação de gate — repita o mesmo comando em background com polling e
# espere o código de saída real. Só reprova gate um comando que TERMINOU com
# código diferente de 0.
#
# Duas diferenças deliberadas em relação a test_05_nascimento.sh:
# (a) NÃO existe `trap limpar 0` sobre o banco: ele sobrevive à saída do script
#     de propósito — é isso que torna o segundo `testar` barato (reúso, não
#     recriação). Quem quer host limpo chama `derrubar` explicitamente.
# (b) este script NÃO cria superusuário nem exercita `down -v`/`up -d` — isso é
#     papel do tracer de nascimento; duplicá-lo aqui encareceria todo gate da
#     fase sem necessidade.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
COPIER="${ROOT}/.venv-template/bin/copier"

# Estado fora do repositório, derivado de TMPDIR + uid + hash do caminho
# absoluto do template — dois checkouts diferentes nunca colidem.
HASH_RAIZ=$(printf '%s' "${ROOT}" | sha1sum | cut -c1-16)
STATE_DIR="${TMPDIR:-/tmp}/ensaio-django-$(id -u)-${HASH_RAIZ}"
DESTINO="${STATE_DIR}/copia"
ARQ_PORTA="${STATE_DIR}/porta"
ARQ_PROJETO="${STATE_DIR}/projeto"
ARQ_FINGERPRINT="${STATE_DIR}/fingerprint"
FINGERPRINT_PY="${STATE_DIR}/_fingerprint.py"

PORTA=''
PROJETO=''

falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}

uso() {
    cat >&2 <<'EOF'
uso: .template-tests/ensaio_django.sh <subcomando> [args...]

Subcomandos:
  subir                 garante que existe um banco saudável (renderiza e sobe se preciso)
  porta                 idem subir, silencioso — imprime só o número da porta publicada
  url                   idem subir, silencioso — imprime só http://127.0.0.1:<porta>
  destino               idem subir, silencioso — imprime só o caminho absoluto da cópia
  testar <alvo...>      roda "manage.py test <alvo...> --noinput" dentro do container web
  executar <cmd...>     roda "docker compose exec -T web <cmd...>" na cópia
  compor <args...>      roda "docker compose --project-name ... --env-file .env <args...>" na cópia
  derrubar               down --volumes --remove-orphans, remove dados/, apaga a cópia e o estado
EOF
}

exigir_ferramentas() {
    for ferramenta in docker curl python3; do
        command -v "${ferramenta}" >/dev/null 2>&1 || falhar "ferramenta ausente: ${ferramenta}"
    done
}

exigir_copier() {
    [ -x "${COPIER}" ] || falhar "Copier aprovado ausente: ${COPIER}"
    "${COPIER}" --version | grep -Fx 'copier 9.17.1' >/dev/null || \
        falhar 'é obrigatório usar Copier 9.17.1 na .venv-template'
}

compose() {
    (
        cd "${DESTINO}"
        docker compose --project-name "${PROJETO}" --env-file .env "$@"
    )
}

diagnosticar() {
    printf '%s\n' 'Diagnóstico do banco de ensaio (somente web e db):' >&2
    compose ps >&2 || true
    compose logs --tail=100 web db >&2 || true
}

aguardar_web() {
    tentativas=0
    while [ "${tentativas}" -lt 180 ]; do
        if curl -fsS "http://127.0.0.1:${PORTA}/healthz" >/dev/null 2>&1; then
            return 0
        fi
        tentativas=$((tentativas + 1))
        sleep 1
    done
    diagnosticar
    falhar 'web do banco de ensaio não respondeu em /healthz dentro de 180 segundos'
}

# Escreve o script Python que calcula a impressão digital do working tree.
# Vive num arquivo (não num heredoc anexado ao próprio `python3 -`) porque a
# lista de caminhos ordenada chega via stdin/pipe — um heredoc no mesmo
# comando substituiria esse stdin em vez de coexistir com ele.
escrever_fingerprint_py() {
    mkdir -p "${STATE_DIR}"
    cat > "${FINGERPRINT_PY}" <<'PY'
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1])
dados = sys.stdin.buffer.read()
caminhos = dados.split(b"\0")
if caminhos and caminhos[-1] == b"":
    caminhos.pop()

digest = hashlib.sha1()
for caminho_bytes in caminhos:
    # Regra 1: o caminho entra no hash, não só o conteúdo — sem isso, renomear
    # um arquivo sem mudar o conteúdo deixaria o banco ser reaproveitado com a
    # árvore errada.
    digest.update(caminho_bytes)
    arquivo = root / caminho_bytes.decode("utf-8", errors="surrogateescape")
    if arquivo.is_file():
        try:
            conteudo = arquivo.read_bytes()
        except OSError:
            digest.update(b"AUSENTE")
            continue
        # Regra 3: só conteúdo entra; nada de mtime, permissão ou inode — um
        # touch que não muda byte nenhum não pode custar um up --build.
        digest.update(b"\0")
        digest.update(conteudo)
    else:
        # Regra 2: caminho listado pelo índice do git (git ls-files -c) mas
        # ausente no disco (removido com rm, não git rm) vira o marcador
        # AUSENTE — SEM o separador \0 que o caso presente usa acima, para que
        # um arquivo cujo conteúdo é literalmente "AUSENTE" não produza o
        # mesmo digest do caso apagado.
        digest.update(b"AUSENTE")

print(digest.hexdigest())
PY
}

impressao_atual() {
    escrever_fingerprint_py
    # LC_ALL=C: ordenação por valor de byte, estável entre hosts e locales —
    # sem isso a ordem do fluxo (e portanto o digest) dependeria do locale de
    # quem roda o script.
    git -C "${ROOT}" ls-files -z -co --exclude-standard -- . ':!.planning' ':!.template-tests' \
        | LC_ALL=C sort -z \
        | python3 "${FINGERPRINT_PY}" "${ROOT}"
}

banco_existe() {
    [ -d "${DESTINO}" ] && [ -f "${ARQ_PORTA}" ] && [ -f "${ARQ_PROJETO}" ] && [ -f "${ARQ_FINGERPRINT}" ]
}

banco_atualizado() {
    atual=$(impressao_atual)
    gravado=$(cat "${ARQ_FINGERPRINT}")
    [ "${atual}" = "${gravado}" ]
}

banco_saudavel() {
    porta_gravada=$(cat "${ARQ_PORTA}")
    curl -fsS "http://127.0.0.1:${porta_gravada}/healthz" >/dev/null 2>&1
}

derrubar_interno() {
    if banco_existe; then
        projeto_gravado=$(cat "${ARQ_PROJETO}" 2>/dev/null || printf '')
        if [ -n "${projeto_gravado}" ] && [ -d "${DESTINO}" ]; then
            (
                cd "${DESTINO}"
                docker compose --project-name "${projeto_gravado}" --env-file .env \
                    down --volumes --remove-orphans >/dev/null 2>&1 || true
            )
        fi
    fi
    # O initdb grava dados/pg como uid 999; o usuário do host não consegue
    # removê-lo — sem esta limpeza via container root o rm -rf do destino falha
    # silenciosamente e acumula lixo em /tmp.
    if [ -d "${DESTINO}/dados" ]; then
        docker run --rm -v "${DESTINO}:/alvo" postgres:17 rm -rf /alvo/dados \
            >/dev/null 2>&1 || true
    fi
    rm -rf "${DESTINO}"
    rm -f "${ARQ_PORTA}" "${ARQ_PROJETO}" "${ARQ_FINGERPRINT}"
}

criar_banco() {
    porta_livre=$(python3 - <<'PY'
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)
    projeto="ensaio$(printf '%s' "${ROOT}" | sha1sum | cut -c1-10)"

    mkdir -p "${STATE_DIR}"

    # --vcs-ref=HEAD: com uma tag de release no repositório, o Copier copiaria
    # por padrão a última tag — o banco de ensaio precisa do estado atual do
    # template. cor_primaria=#1e40af é o default do copier.yml de propósito:
    # o .env da cópia bate com o default declarado no input.css.
    "${COPIER}" copy --defaults --vcs-ref=HEAD \
        --data 'sistema_nome=Sistema Ensaio' \
        --data 'sistema_slug=ensaio' \
        --data 'sistema_hostname=ensaio.example.invalid' \
        --data "sistema_porta=${porta_livre}" \
        --data 'sistema_banco=ensaio' \
        --data 'sistema_sigla=ENS' \
        --data 'cor_primaria=#1e40af' \
        --data 'incluir_app_exemplo=true' \
        "${ROOT}" "${DESTINO}" >&2 || falhar 'copier copy falhou ao criar o banco de ensaio'

    [ -d "${DESTINO}" ] || falhar 'Copier não criou o destino do banco de ensaio'

    # Guarda anti-v0.1.0 (as mesmas duas asserções de test_copier_copy.sh,
    # aplicadas aqui ao banco de ensaio).
    [ -f "${DESTINO}/core/static/img/logo-entidade.svg" ] || \
        falhar 'banco de ensaio sem logo-entidade.svg: renderizou uma tag antiga, não o HEAD'
    if grep -Eq '_commit: v0\.1\.0(,|$)' "${DESTINO}/.copier-answers.yml"; then
        falhar 'banco de ensaio registrou _commit: v0.1.0 — falta --vcs-ref=HEAD'
    fi

    cp "${DESTINO}/.env.example" "${DESTINO}/.env"

    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    POSTGRES_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    export SECRET_KEY POSTGRES_PASSWORD
    python3 - "${DESTINO}/.env" <<'PY'
from pathlib import Path
import os
import sys

env_path = Path(sys.argv[1])
text = env_path.read_text()
replacements = {
    "SECRET_KEY=replace-with-a-long-random-secret": f"SECRET_KEY={os.environ['SECRET_KEY']}",
    "POSTGRES_PASSWORD=replace-with-a-database-password": (
        f"POSTGRES_PASSWORD={os.environ['POSTGRES_PASSWORD']}"
    ),
    "DATABASE_URL=postgres://ensaio:replace-with-a-database-password@db:5432/ensaio": (
        f"DATABASE_URL=postgres://ensaio:{os.environ['POSTGRES_PASSWORD']}@db:5432/ensaio"
    ),
}
for source, target in replacements.items():
    if source not in text:
        raise SystemExit(f"placeholder esperado ausente: {source.split('=', 1)[0]}")
    text = text.replace(source, target, 1)
env_path.write_text(text)
PY
    unset SECRET_KEY POSTGRES_PASSWORD

    PORTA="${porta_livre}"
    PROJETO="${projeto}"

    compose up -d --build db web >&2 || {
        diagnosticar
        falhar 'docker compose up -d --build db web falhou no banco de ensaio'
    }

    aguardar_web

    compose exec -T web python manage.py migrate --noinput >&2 || \
        falhar 'migrate --noinput falhou no banco de ensaio'

    printf '%s\n' "${PORTA}" > "${ARQ_PORTA}"
    printf '%s\n' "${PROJETO}" > "${ARQ_PROJETO}"
    impressao_atual > "${ARQ_FINGERPRINT}"
}

# Regra de reúso, nesta ordem: o banco é reaproveitado se e somente se a cópia
# existe, a impressão gravada é igual à atual e /healthz responde. Em qualquer
# outro caso: derruba e recria do zero (nunca re-renderiza por cima — o Copier
# não apaga arquivo que sumiu do template).
garantir_banco() {
    exigir_ferramentas
    exigir_copier

    if banco_existe && banco_atualizado && banco_saudavel; then
        PORTA=$(cat "${ARQ_PORTA}")
        PROJETO=$(cat "${ARQ_PROJETO}")
        return 0
    fi

    if banco_existe; then
        printf '%s\n' 'ENSAIO: recriando banco de ensaio (impressão digital mudou ou banco não saudável) — copier copy + docker compose up -d --build, pode levar minutos na primeira vez com cache frio.' >&2
    else
        printf '%s\n' 'ENSAIO: nenhum banco de ensaio encontrado — criando (copier copy + docker compose up -d --build), pode levar minutos na primeira vez com cache frio.' >&2
    fi

    derrubar_interno
    criar_banco
}

subcomando="${1:-}"
case "${subcomando}" in
    subir)
        garantir_banco
        printf 'ENSAIO_DESTINO=%s\n' "${DESTINO}"
        printf 'ENSAIO_PROJETO=%s\n' "${PROJETO}"
        printf 'ENSAIO_PORTA=%s\n' "${PORTA}"
        printf 'ENSAIO_URL=http://127.0.0.1:%s\n' "${PORTA}"
        ;;
    porta)
        garantir_banco
        printf '%s\n' "${PORTA}"
        ;;
    url)
        garantir_banco
        printf 'http://127.0.0.1:%s\n' "${PORTA}"
        ;;
    destino)
        garantir_banco
        printf '%s\n' "${DESTINO}"
        ;;
    testar)
        shift
        [ "$#" -ge 1 ] || falhar 'uso: ensaio_django.sh testar <alvo...>'
        garantir_banco
        set +e
        compose exec -T web python manage.py test "$@" --noinput
        codigo=$?
        set -e
        exit "${codigo}"
        ;;
    executar)
        shift
        [ "$#" -ge 1 ] || falhar 'uso: ensaio_django.sh executar <cmd...>'
        garantir_banco
        set +e
        compose exec -T web "$@"
        codigo=$?
        set -e
        exit "${codigo}"
        ;;
    compor)
        shift
        [ "$#" -ge 1 ] || falhar 'uso: ensaio_django.sh compor <args...>'
        garantir_banco
        set +e
        compose "$@"
        codigo=$?
        set -e
        exit "${codigo}"
        ;;
    derrubar)
        derrubar_interno
        rm -f "${FINGERPRINT_PY}"
        rmdir "${STATE_DIR}" 2>/dev/null || true
        ;;
    '')
        uso
        exit 2
        ;;
    *)
        uso
        exit 2
        ;;
esac
