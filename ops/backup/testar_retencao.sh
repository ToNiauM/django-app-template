#!/bin/sh
# Ensaio remoto descartável da mesma função de retenção usada pela produção.
set -eu

. "$(dirname "$0")/retencao.sh"

: "${SISTEMA_SLUG:?SISTEMA_SLUG é obrigatório}"
: "${R2_BUCKET:?R2_BUCKET é obrigatório}"

# O namespace não pode coincidir com os prefixos de produção.
for arg in "$@"; do
    case "${arg}" in
        daily|weekly)
            echo "[testar_retencao] recusando prefixo de produção '${arg}'" >&2
            exit 1
            ;;
    esac
done

PREFIXO_TESTE="${SISTEMA_SLUG}_retencao_$$"
DIR_TMP=$(mktemp -d)

limpar() {
    rclone purge "r2:${R2_BUCKET}/${PREFIXO_TESTE}/" >/dev/null 2>&1 || true
    rm -rf "${DIR_TMP}"
}
trap limpar 0

echo "[testar_retencao] gerando nove objetos descartáveis"
agora=$(date +%s)
i=1
while [ "${i}" -le 9 ]; do
    arquivo="${DIR_TMP}/sintetico-${i}.dump"
    : > "${arquivo}"
    dias_atras=$((10 - i))
    touch -d "@$((agora - dias_atras * 86400))" "${arquivo}"
    i=$((i + 1))
done

rclone copy "${DIR_TMP}" "r2:${R2_BUCKET}/${PREFIXO_TESTE}/"
manter_ultimos "${PREFIXO_TESTE}" 7

restantes=$(rclone lsf "r2:${R2_BUCKET}/${PREFIXO_TESTE}/" 2>/dev/null | grep -c . || true)
echo "[testar_retencao] restantes: ${restantes}"
[ "${restantes}" -eq 7 ]
