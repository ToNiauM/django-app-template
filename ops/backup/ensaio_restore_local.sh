#!/bin/sh
# Ensaio de restore isolado: nenhum recurso da stack em execução é reutilizado.
set -eu

: "${SISTEMA_SLUG:?SISTEMA_SLUG é obrigatório}"
: "${R2_BUCKET:?R2_BUCKET é obrigatório}"
: "${REHEARSAL_BACKUP_IMAGE:?REHEARSAL_BACKUP_IMAGE é obrigatório}"
: "${REHEARSAL_WEB_IMAGE:?REHEARSAL_WEB_IMAGE é obrigatório}"

case "${SISTEMA_SLUG}" in
    *[!a-z0-9-]*|'')
        echo "[restore] SISTEMA_SLUG deve conter apenas a-z, 0-9 e hífen" >&2
        exit 1
        ;;
esac

REPO_DIR=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
ENV_FILE="${REHEARSAL_ENV_FILE:-${REPO_DIR}/.env}"
[ -f "${ENV_FILE}" ] || {
    echo "[restore] arquivo de ambiente não encontrado: ${ENV_FILE}" >&2
    exit 1
}

PREFIXO="${SISTEMA_SLUG}_rehearsal_$$"
VOLUME_PGDATA="${PREFIXO}_pgdata"
REDE="${PREFIXO}_net"
DB_CONTAINER="${PREFIXO}_db"
DB_NOME="${SISTEMA_SLUG}_rehearsal"
DB_USUARIO="${SISTEMA_SLUG}_rehearsal"
DB_SENHA=$(openssl rand -hex 16)
DUMP_LOCAL=$(mktemp "${TMPDIR:-/tmp}/${PREFIXO}.XXXXXX.dump")

VOLUME_CRIADO=0
REDE_CRIADA=0
CONTAINER_CRIADO=0

cleanup() {
    status=$?
    trap - EXIT HUP INT TERM

    if [ "${CONTAINER_CRIADO}" -eq 1 ]; then
        docker rm -f "${DB_CONTAINER}" >/dev/null 2>&1 || true
    fi
    if [ "${REDE_CRIADA}" -eq 1 ]; then
        docker network rm "${REDE}" >/dev/null 2>&1 || true
    fi
    if [ "${VOLUME_CRIADO}" -eq 1 ]; then
        docker volume rm "${VOLUME_PGDATA}" >/dev/null 2>&1 || true
    fi
    rm -f "${DUMP_LOCAL}"
    exit "${status}"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP

echo "[restore] descobrindo o dump customizado mais recente"
DUMP_FILE=$(docker run --rm --env-file "${ENV_FILE}" --entrypoint rclone \
    "${REHEARSAL_BACKUP_IMAGE}" lsf "r2:${R2_BUCKET}/daily/" \
    --format tp --separator ';' | sort -t';' -k1,1r | head -n 1 | cut -d';' -f2 | tr -d '\r')
[ -n "${DUMP_FILE}" ] || {
    echo "[restore] nenhum dump disponível em daily/" >&2
    exit 1
}

echo "[restore] copiando ${DUMP_FILE} para armazenamento temporário"
docker run --rm --env-file "${ENV_FILE}" --entrypoint rclone \
    "${REHEARSAL_BACKUP_IMAGE}" cat "r2:${R2_BUCKET}/daily/${DUMP_FILE}" > "${DUMP_LOCAL}"

docker volume create "${VOLUME_PGDATA}" >/dev/null
VOLUME_CRIADO=1
docker network create "${REDE}" >/dev/null
REDE_CRIADA=1
docker run -d --name "${DB_CONTAINER}" --network "${REDE}" \
    -v "${VOLUME_PGDATA}:/var/lib/postgresql/data" \
    -e "POSTGRES_DB=${DB_NOME}" \
    -e "POSTGRES_USER=${DB_USUARIO}" \
    -e "POSTGRES_PASSWORD=${DB_SENHA}" \
    -e "POSTGRES_INITDB_ARGS=--locale-provider=icu --icu-locale=pt-BR --encoding=UTF8" \
    postgres:17 >/dev/null
CONTAINER_CRIADO=1

tentativa=0
while ! docker exec "${DB_CONTAINER}" pg_isready -U "${DB_USUARIO}" -d "${DB_NOME}" >/dev/null 2>&1; do
    tentativa=$((tentativa + 1))
    [ "${tentativa}" -lt 60 ] || {
        echo "[restore] banco efêmero não ficou disponível" >&2
        exit 1
    }
    sleep 1
done

echo "[restore] restaurando dump no banco efêmero"
docker exec -i "${DB_CONTAINER}" pg_restore --clean --if-exists --no-owner \
    --username="${DB_USUARIO}" --dbname="${DB_NOME}" < "${DUMP_LOCAL}"

DATABASE_URL_EFEMERA="postgres://${DB_USUARIO}:${DB_SENHA}@${DB_CONTAINER}:5432/${DB_NOME}"
for comando in 'migrate --plan' 'migrate --noinput' 'check'; do
    # A imagem da aplicação é fornecida explicitamente; o script não usa Compose de produção.
    docker run --rm --network "${REDE}" --env-file "${ENV_FILE}" \
        -e "DATABASE_URL=${DATABASE_URL_EFEMERA}" \
        -e DJANGO_SETTINGS_MODULE=config.settings.prod \
        -e DEBUG=false \
        --entrypoint python "${REHEARSAL_WEB_IMAGE}" manage.py ${comando}
done

echo "[restore] ensaio concluído; cleanup confinado será executado"
