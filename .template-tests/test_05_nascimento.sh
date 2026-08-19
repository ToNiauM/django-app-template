#!/bin/sh
# Tracer de nascimento: valida um sistema Copier real sem tocar no template.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
COPIER="${ROOT}/.venv-template/bin/copier"
TMP=$(mktemp -d)
TMP_VALIDADO=${TMP}
DESTINO="${TMP}/nascimento"
PROJETO="nascimento${$}"
MANTER=false
SUCESSO=false
LIMPEZA_FEITA=false
PORTA=''

falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}

exigir_copier() {
    [ -x "${COPIER}" ] || falhar "Copier aprovado ausente: ${COPIER}"
    "${COPIER}" --version | grep -Fx 'copier 9.17.1' >/dev/null || \
        falhar 'é obrigatório usar Copier 9.17.1 na .venv-template'
}

preflight() {
    printf '%s\n' 'PREFLIGHT 05-01: sintaxe, ferramentas, artefatos e contratos Copier'
    if ! (
        command -v timeout >/dev/null 2>&1 &&
        command -v python3 >/dev/null 2>&1 &&
        command -v docker >/dev/null 2>&1 &&
        command -v curl >/dev/null 2>&1 &&
        sh -n "${ROOT}/.template-tests/test_05_nascimento.sh" &&
        test -x "${ROOT}/.template-tests/test_05_nascimento.sh" &&
        test -x "${COPIER}" &&
        test "$("${COPIER}" --version)" = 'copier 9.17.1' &&
        test -f "${ROOT}/copier.yml" &&
        test -f "${ROOT}/compose.yml.jinja" &&
        test -f "${ROOT}/.env.example.jinja" &&
        test -f "${ROOT}/entrypoint.sh" &&
        test -x "${ROOT}/.template-tests/test_copier_copy.sh" &&
        timeout 10 docker info >/dev/null 2>&1 &&
        timeout 45 python3 -m unittest discover -s "${ROOT}/.template-tests" \
            -p 'test_04_07_collectstatic.py'
    ); then
        printf '%s\n' 'FALHOU: preflight 05-01' >&2
        exit 1
    fi
    printf '%s\n' 'OK: preflight 05-01'
}

compose() {
    (
        cd "${DESTINO}"
        docker compose --project-name "${PROJETO}" --env-file .env "$@"
    )
}

diagnosticar() {
    printf '%s\n' 'Diagnóstico do ensaio de nascimento (somente web e db):' >&2
    compose ps >&2 || true
    compose logs --tail=100 web db >&2 || true
}

aguardar_web() {
    tentativas=0
    while [ "${tentativas}" -lt 180 ]; do
        if curl -fsS "http://127.0.0.1:${PORTA}/healthz" >/dev/null; then
            return 0
        fi
        tentativas=$((tentativas + 1))
        sleep 1
    done
    diagnosticar
    falhar 'web não respondeu em /healthz dentro de 180 segundos'
}

limpar() {
    if [ "${LIMPEZA_FEITA}" = true ]; then
        return
    fi
    LIMPEZA_FEITA=true

    if [ "${MANTER}" = true ] && [ "${SUCESSO}" = true ]; then
        unset NASCIMENTO_ADMIN_PASSWORD SECRET_KEY POSTGRES_PASSWORD
        return
    fi

    if [ -d "${DESTINO:-}" ]; then
        compose down --volumes --remove-orphans >/dev/null 2>&1 || true
    fi

    unset NASCIMENTO_ADMIN_PASSWORD SECRET_KEY POSTGRES_PASSWORD
    # O initdb grava dados/pg como uid 999 e o usuário do host não consegue
    # removê-lo — sem esta limpeza via container root o rm -rf do TMP falha
    # silenciosamente e acumula lixo em /tmp (a imagem postgres:17 já está
    # local: o próprio tracer acabou de usá-la).
    if [ -d "${DESTINO:-}/dados" ]; then
        docker run --rm -v "${DESTINO}:/alvo" postgres:17 rm -rf /alvo/dados \
            >/dev/null 2>&1 || true
    fi
    if [ "${TMP}" = "${TMP_VALIDADO}" ] && [ -d "${TMP}" ]; then
        rm -rf "${TMP}"
    fi
}
trap limpar 0 HUP INT TERM

case "${1:-}" in
    '') ;;
    --keep) MANTER=true ;;
    *) falhar 'uso: .template-tests/test_05_nascimento.sh [--keep]' ;;
esac

for ferramenta in docker curl python3; do
    command -v "${ferramenta}" >/dev/null 2>&1 || falhar "ferramenta ausente: ${ferramenta}"
done
preflight
exigir_copier

PORTA=$(python3 - <<'PY'
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)

# --vcs-ref=HEAD: com uma tag de release no repositório, o Copier copiaria por
# padrão a última tag — o tracer precisa ensaiar o estado atual do template.
"${COPIER}" copy --defaults --vcs-ref=HEAD \
    --data 'sistema_nome=Sistema Nascimento' \
    --data 'sistema_slug=nascimento' \
    --data 'sistema_hostname=nascimento.example.invalid' \
    --data "sistema_porta=${PORTA}" \
    --data 'sistema_banco=nascimento' \
    --data 'sistema_sigla=NAS' \
    --data 'cor_primaria=#2255aa' \
    --data 'incluir_app_exemplo=true' \
    "${ROOT}" "${DESTINO}" >/dev/null

[ -d "${DESTINO}" ] || falhar 'Copier não criou o destino efêmero esperado'
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
    "DATABASE_URL=postgres://nascimento:replace-with-a-database-password@db:5432/nascimento": (
        f"DATABASE_URL=postgres://nascimento:{os.environ['POSTGRES_PASSWORD']}@db:5432/nascimento"
    ),
}
for source, target in replacements.items():
    if source not in text:
        raise SystemExit(f"placeholder esperado ausente: {source.split('=', 1)[0]}")
    text = text.replace(source, target, 1)
env_path.write_text(text)
PY
unset SECRET_KEY POSTGRES_PASSWORD

if [ -z "${NASCIMENTO_ADMIN_PASSWORD:-}" ]; then
    NASCIMENTO_ADMIN_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
fi
export NASCIMENTO_ADMIN_PASSWORD

compose config -q || falhar 'docker compose config -q falhou'
compose up -d --build db web || {
    diagnosticar
    falhar 'docker compose up -d --build db web falhou'
}
aguardar_web

compose exec -T web python manage.py migrate --noinput || falhar 'migrate --noinput falhou'
DJANGO_SUPERUSER_EMAIL=nascimento@example.invalid \
DJANGO_SUPERUSER_PASSWORD="${NASCIMENTO_ADMIN_PASSWORD}" \
    compose exec -T \
        -e DJANGO_SUPERUSER_EMAIL \
        -e DJANGO_SUPERUSER_PASSWORD \
        web python manage.py createsuperuser --noinput || falhar 'createsuperuser --noinput falhou'
compose exec -T web python manage.py shell -c \
    "from django.contrib.auth import get_user_model; u = get_user_model().objects.get(email='nascimento@example.invalid'); assert u.is_staff and u.is_superuser" || \
    falhar 'superusuário de ensaio não foi confirmado como staff e superuser'
printf '%s\n' 'OK: superusuário nascimento@example.invalid criado'

compose exec -T web python manage.py test core apps.exemplo --noinput || \
    falhar 'suíte Django da cópia gerada falhou'
curl -fsS "http://127.0.0.1:${PORTA}/healthz" >/dev/null || falhar 'smoke /healthz falhou'
curl -fsS "http://127.0.0.1:${PORTA}/login/" >/dev/null || falhar 'smoke /login/ falhou'

# Prova direta do critério de sucesso 4 do roadmap: o superusuário criado antes
# de `down -v` continua existindo depois — o bind mount em ./dados/pg torna a
# operação historicamente destrutiva inofensiva por construção.
[ -d "${DESTINO}/dados/pg" ] || falhar 'bind mount não materializou dados/pg no host'
compose down --volumes || falhar 'docker compose down --volumes falhou'
compose up -d db web || {
    diagnosticar
    falhar 'docker compose up -d db web após down -v falhou'
}
aguardar_web
compose exec -T web python manage.py shell -c \
    "from django.contrib.auth import get_user_model; get_user_model().objects.get(email='nascimento@example.invalid')" || \
    falhar 'dados não sobreviveram a docker compose down -v && up -d'
printf '%s\n' 'OK: dados sobreviveram a down --volumes + up -d'

SUCESSO=true
if [ "${MANTER}" = true ]; then
    printf 'NASCIMENTO_DESTINO=%s\n' "${DESTINO}"
    printf 'NASCIMENTO_PROJETO_COMPOSE=%s\n' "${PROJETO}"
    printf 'NASCIMENTO_URL=http://127.0.0.1:%s\n' "${PORTA}"
fi
printf '%s\n' 'OK: nascimento completo da cópia Copier passou.'
