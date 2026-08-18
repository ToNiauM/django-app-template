#!/bin/sh
# Prova o cleanup do ensaio de restore sem executar Docker ou acessar R2.
set -eu

NOME=$(basename "$0")
SELF_PATH=$(CDPATH= cd -- "$(dirname "$0")" && pwd)/${NOME}

if [ "${NOME}" = "docker" ]; then
    : "${SHIM_LOG:?SHIM_LOG é obrigatório no shim}"
    printf 'docker %s\n' "$*" >> "${SHIM_LOG}"

    case "${1:-}" in
        volume)
            [ "${2:-}" = "create" ] && exit 0
            ;;
        network)
            [ "${2:-}" = "create" ] && exit 0
            ;;
        run)
            if [ "${FAIL_AT:-}" = "run" ] && [ "${2:-}" = "-d" ]; then
                exit 91
            fi
            case " $* " in
                *" lsf "*)
                    printf '2026-08-18 03:00:00;anterior.dump\n2026-08-19 03:00:00;mais-recente.dump\n'
                    ;;
                *" cat "*) printf 'dump-customizado-simulado' ;;
            esac
            exit 0
            ;;
        exec)
            if [ "${FAIL_AT:-}" = "interrupt" ]; then
                kill -TERM "${REHEARSAL_TARGET_PID:?pid do ensaio ausente}"
            fi
            exit 0
            ;;
    esac
    exit 0
fi

if [ "${NOME}" = "rclone" ]; then
    : "${SHIM_LOG:?SHIM_LOG é obrigatório no shim}"
    printf 'rclone %s\n' "$*" >> "${SHIM_LOG}"
    exit 0
fi

if [ "${NOME}" = "rehearsal-runner" ]; then
    export REHEARSAL_TARGET_PID="$$"
    exec sh "${REHEARSAL_SCRIPT:?REHEARSAL_SCRIPT é obrigatório}"
fi

RAIZ=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
ALVO="${RAIZ}/ops/backup/ensaio_restore_local.sh"
TMP=$(mktemp -d)
BIN="${TMP}/bin"
LOG="${TMP}/comandos.log"
mkdir -p "${BIN}"
ln -s "${SELF_PATH}" "${BIN}/docker"
ln -s "${SELF_PATH}" "${BIN}/rclone"
ln -s "${SELF_PATH}" "${BIN}/rehearsal-runner"
printf 'segredo-simulado\n' > "${TMP}/.env"

limpar() {
    [ "${KEEP_TEST_TMP:-0}" = "1" ] || rm -rf "${TMP}"
}
trap limpar EXIT HUP INT TERM

falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}

validar_remocoes() {
    caso="$1"
    deve_ter_container="$2"

    volume=$(awk '/^docker volume create / { print $4; exit }' "${LOG}")
    rede=$(awk '/^docker network create / { print $4; exit }' "${LOG}")
    container=$(awk '/^docker run -d --name / { print $5; exit }' "${LOG}")
    [ -n "${volume}" ] || falhar "${caso}: volume efêmero não foi criado"
    [ -n "${rede}" ] || falhar "${caso}: rede efêmera não foi criada"

    esperadas=$(printf 'docker network rm %s\ndocker volume rm %s' "${rede}" "${volume}")
    if [ "${deve_ter_container}" = "sim" ]; then
        [ -n "${container}" ] || falhar "${caso}: container efêmero não foi criado"
        esperadas=$(printf 'docker rm -f %s\n%s' "${container}" "${esperadas}")
    fi
    removidas=$(grep '^docker \(rm -f\|network rm\|volume rm\)' "${LOG}" || true)
    [ "${removidas}" = "${esperadas}" ] || falhar "${caso}: cleanup fora da lista esperada"
    ! grep -E 'docker (rm|network rm|volume rm).*(preexistente|producao|production|pca)' "${LOG}" || \
        falhar "${caso}: tentou remover recurso preexistente ou de produção"
}

executar_caso() {
    caso="$1"
    falha="$2"
    sucesso_esperado="$3"
    tem_container="$4"
    : > "${LOG}"

    set +e
    env PATH="${BIN}:${PATH}" \
    SHIM_LOG="${LOG}" \
    FAIL_AT="${falha}" \
    REHEARSAL_SCRIPT="${ALVO}" \
    SISTEMA_SLUG=aurora \
    R2_BUCKET=backups-simulados \
    REHEARSAL_BACKUP_IMAGE=backup-simulado \
    REHEARSAL_WEB_IMAGE=web-simulada \
    REHEARSAL_ENV_FILE="${TMP}/.env" \
    sh "${BIN}/rehearsal-runner" >"${TMP}/${caso}.out" 2>"${TMP}/${caso}.err"
    status=$?
    set -e

    if [ "${sucesso_esperado}" = "sim" ]; then
        [ "${status}" -eq 0 ] || falhar "${caso}: ensaio deveria concluir"
    else
        [ "${status}" -ne 0 ] || falhar "${caso}: ensaio deveria falhar/interromper"
    fi
    validar_remocoes "${caso}" "${tem_container}"
}

executar_caso sucesso '' sim sim
executar_caso falha run nao nao
executar_caso interrupcao interrupt nao sim

printf 'OK: sucesso, falha e interrupção removem somente recursos do ensaio.\n'
