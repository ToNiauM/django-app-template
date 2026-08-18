#!/bin/sh
# Dump PostgreSQL customizado, cópias diária/semanal e retenção no R2.
set -eu

. "$(dirname "$0")/retencao.sh"

: "${SISTEMA_SLUG:?SISTEMA_SLUG é obrigatório}"
: "${DB_HOST:?DB_HOST é obrigatório}"
: "${DB_USER:?DB_USER é obrigatório}"
: "${DB_NAME:?DB_NAME é obrigatório}"
: "${R2_BUCKET:?R2_BUCKET é obrigatório}"
: "${BACKUP_RETENCAO_DIARIA:?BACKUP_RETENCAO_DIARIA é obrigatório}"
: "${BACKUP_RETENCAO_SEMANAL:?BACKUP_RETENCAO_SEMANAL é obrigatório}"
: "${BACKUP_DIA_SEMANAL:?BACKUP_DIA_SEMANAL é obrigatório}"

DATA=$(date +%Y-%m-%d_%H%M%S)
DIA_SEMANA=$(date +%u)
ARQUIVO="/tmp/${SISTEMA_SLUG}_${DATA}.dump"

limpar() {
    rm -f "${ARQUIVO}"
}
trap limpar 0

echo "[backup] iniciando dump de ${DB_NAME}@${DB_HOST}"
pg_dump --format=custom --host="${DB_HOST}" --username="${DB_USER}" "${DB_NAME}" > "${ARQUIVO}"

echo "[backup] enviando cópia diária"
rclone copy "${ARQUIVO}" "r2:${R2_BUCKET}/daily/"

if [ "${DIA_SEMANA}" = "${BACKUP_DIA_SEMANAL}" ]; then
    echo "[backup] dia semanal configurado — enviando cópia semanal"
    rclone copy "${ARQUIVO}" "r2:${R2_BUCKET}/weekly/"
fi

manter_ultimos "daily" "${BACKUP_RETENCAO_DIARIA}"
manter_ultimos "weekly" "${BACKUP_RETENCAO_SEMANAL}"
echo "[backup] concluído"
