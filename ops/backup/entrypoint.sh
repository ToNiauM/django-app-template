#!/bin/sh
# Somente valores estritamente numéricos e em faixas conhecidas chegam ao crontab.
set -eu

falhar() {
    echo "[backup] configuração inválida: $1" >&2
    exit 1
}

inteiro_positivo() {
    valor="$1"
    nome="$2"
    case "${valor}" in
        ''|*[!0-9]*) falhar "${nome} deve ser um inteiro positivo" ;;
    esac
    [ "${valor}" -gt 0 ] || falhar "${nome} deve ser maior que zero"
}

BACKUP_HORA="${BACKUP_HORA:?BACKUP_HORA é obrigatório}"
BACKUP_MINUTO="${BACKUP_MINUTO:?BACKUP_MINUTO é obrigatório}"
BACKUP_RETENCAO_DIARIA="${BACKUP_RETENCAO_DIARIA:?BACKUP_RETENCAO_DIARIA é obrigatório}"
BACKUP_RETENCAO_SEMANAL="${BACKUP_RETENCAO_SEMANAL:?BACKUP_RETENCAO_SEMANAL é obrigatório}"
BACKUP_DIA_SEMANAL="${BACKUP_DIA_SEMANAL:?BACKUP_DIA_SEMANAL é obrigatório}"

case "${BACKUP_HORA}" in
    0|1|2|3|4|5|6|7|8|9|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23) ;;
    *) falhar "BACKUP_HORA deve estar entre 0 e 23" ;;
esac
case "${BACKUP_MINUTO}" in
    0|1|2|3|4|5|6|7|8|9|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|50|51|52|53|54|55|56|57|58|59) ;;
    *) falhar "BACKUP_MINUTO deve estar entre 0 e 59" ;;
esac
inteiro_positivo "${BACKUP_RETENCAO_DIARIA}" BACKUP_RETENCAO_DIARIA
inteiro_positivo "${BACKUP_RETENCAO_SEMANAL}" BACKUP_RETENCAO_SEMANAL
case "${BACKUP_DIA_SEMANAL}" in
    1|2|3|4|5|6|7) ;;
    *) falhar "BACKUP_DIA_SEMANAL deve estar entre 1 e 7" ;;
esac

printf '%s %s * * * /backup.sh >> /proc/1/fd/1 2>> /proc/1/fd/2\n' \
    "${BACKUP_MINUTO}" "${BACKUP_HORA}" > /etc/crontabs/root
exec crond -f -d 8
