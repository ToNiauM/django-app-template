#!/bin/sh
# Ensaio contratual A→B→C em repositórios temporários, sem refs reais.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
COPIER="${ROOT}/.venv-template/bin/copier"
TMP=$(mktemp -d)
TEMPLATE="${TMP}/template"
DESTINO="${TMP}/destino"

limpar() {
    rm -rf "${TMP}"
}
trap limpar 0 HUP INT TERM

falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}

exigir_copier() {
    [ -x "${COPIER}" ] || falhar "Copier aprovado ausente: ${COPIER}"
    "${COPIER}" --version | grep -Fx 'copier 9.17.1' >/dev/null || \
        falhar 'é obrigatório usar Copier 9.17.1 na .venv-template'
}

commit_resposta() {
    sed -n 's/.*_commit: \([^,}]*\).*/\1/p' "${DESTINO}/.copier-answers.yml" | head -n 1
}

exigir_limpo() {
    test -z "$(git -C "$DESTINO" status --porcelain)" || \
        falhar 'o destino precisa estar limpo antes do update'
}

commit_destino() {
    mensagem="$1"
    git -C "$DESTINO" add .
    git -C "$DESTINO" commit -qm "${mensagem}"
    test -z "$(git -C "$DESTINO" status --porcelain)" || \
        falhar "${mensagem}: commit não deixou a árvore limpa"
}

exigir_sem_exemplo() {
    [ ! -e "${DESTINO}/apps/exemplo" ] || falhar 'diretório apps/exemplo foi ressuscitado'
    ! grep -Fq 'apps.exemplo' "${DESTINO}/config/settings/base.py" || \
        falhar 'settings ressuscitou o app exemplo'
    ! grep -Fq 'apps.exemplo' "${DESTINO}/config/urls.py" || \
        falhar 'urls ressuscitou o app exemplo'
    ! grep -Fq 'exemplo:' "${DESTINO}/core/templates/core/_nav.html" || \
        falhar 'nav ressuscitou o app exemplo'
}

assert_no_conflict_markers() {
    if MATCHES=$(grep -RInF --exclude-dir=.git -e '<<<<<<<' -e '=======' -e '>>>>>>>' "$DESTINO" 2>/dev/null); then
        printf 'FALHOU: marcadores inline encontrados após update:\n%s\n' "${MATCHES}" >&2
        exit 1
    fi
}

exigir_copier
git clone -q --no-hardlinks "${ROOT}" "${TEMPLATE}"
git -C "${TEMPLATE}" config user.name 'Copier rehearsal'
git -C "${TEMPLATE}" config user.email 'copier-rehearsal@example.invalid'
git -C "${TEMPLATE}" tag v0.1.0

"${COPIER}" copy --vcs-ref v0.1.0 --defaults \
    --data sistema_nome='Sistema Atualizável' \
    --data sistema_slug=atualizavel \
    --data sistema_hostname=atualizavel.exemplo.gov.br \
    --data sistema_porta=8345 \
    --data sistema_banco=atualizavel \
    --data sistema_sigla=SAT \
    --data cor_primaria='#2255aa' \
    --data incluir_app_exemplo=true \
    "${TEMPLATE}" "${DESTINO}" >/dev/null
git -C "$DESTINO" init -q
git -C "$DESTINO" config user.name 'Copier rehearsal'
git -C "$DESTINO" config user.email 'copier-rehearsal@example.invalid'
commit_destino 'test: estado A gerado'
COMMIT_A=$(commit_resposta)
[ -n "${COMMIT_A}" ] || falhar 'estado A não registrou _commit'

printf '\nAtualização contratual B: núcleo entregue pelo Copier.\n' >> "${TEMPLATE}/core/README.md"
git -C "${TEMPLATE}" add core/README.md
git -C "${TEMPLATE}" commit -qm 'test: mudança de núcleo B'
git -C "${TEMPLATE}" tag v0.1.1

exigir_limpo
"${COPIER}" update --defaults --data incluir_app_exemplo=false --vcs-ref v0.1.1 --trust >/dev/null
grep -Fq 'Atualização contratual B: núcleo entregue pelo Copier.' "${DESTINO}/core/README.md" || \
    falhar 'mudança B não chegou ao destino'
COMMIT_B=$(commit_resposta)
[ -n "${COMMIT_B}" ] && [ "${COMMIT_A}" != "${COMMIT_B}" ] || \
    falhar '_commit não avançou de A para B'
exigir_sem_exemplo
assert_no_conflict_markers "$DESTINO"
commit_destino 'test: estado B atualizado sem exemplo'

printf '\nAtualização contratual C: núcleo permanece sincronizável.\n' >> "${TEMPLATE}/core/README.md"
git -C "${TEMPLATE}" add core/README.md
git -C "${TEMPLATE}" commit -qm 'test: mudança de núcleo C'
git -C "${TEMPLATE}" tag v0.1.2

exigir_limpo
"${COPIER}" update --defaults --vcs-ref v0.1.2 --trust >/dev/null
grep -Fq 'Atualização contratual C: núcleo permanece sincronizável.' "${DESTINO}/core/README.md" || \
    falhar 'mudança C não chegou ao destino'
COMMIT_C=$(commit_resposta)
[ -n "${COMMIT_C}" ] && [ "${COMMIT_B}" != "${COMMIT_C}" ] || \
    falhar '_commit não avançou de B para C'
exigir_sem_exemplo
assert_no_conflict_markers "$DESTINO"
commit_destino 'test: estado C atualizado sem ressurreição'

grep -Fq 'A → B → C' "${ROOT}/README.md" || \
    falhar 'README não documenta o ensaio A → B → C'
printf 'OK: update Copier A→B→C entregou núcleo e preservou o opt-out.\n'
