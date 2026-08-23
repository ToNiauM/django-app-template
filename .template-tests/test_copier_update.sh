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

preparar_commit_destino() {
    git -C "$DESTINO" add .
    # O template ignora arquivos locais; as respostas são a exceção contratual
    # porque `copier update` depende delas e o ensaio deve versioná-las.
    git -C "$DESTINO" add -f .copier-answers.yml
}

exigir_sem_exemplo() {
    [ ! -e "${DESTINO}/apps/exemplo" ] || falhar 'diretório apps/exemplo foi ressuscitado'
    ! grep -Fq 'apps.exemplo' "${DESTINO}/config/settings/base.py" || \
        falhar 'settings ressuscitou o app exemplo'
    ! grep -Fq 'apps.exemplo' "${DESTINO}/config/urls.py" || \
        falhar 'urls ressuscitou o app exemplo'
    # _nav.html é do núcleo e nunca teve 'exemplo:' — mas isto sozinho não
    # prova mais o opt-out (D-89): quem carrega os itens do domínio agora é
    # _nav_dominio.html, do derivado.
    ! grep -Fq 'exemplo:' "${DESTINO}/core/templates/core/_nav.html" || \
        falhar 'nav ressuscitou o app exemplo'
    # _nav_dominio.html é do derivado; _skip_if_exists garante que o
    # `copier update` NUNCA o reescreve. Se este arquivo algum dia contiver
    # 'exemplo:' isso NÃO é ressurreição do app: o item já estava lá antes
    # (escrito pelo derivado ou semeado na primeira cópia), o núcleo não o
    # tocou, e o item some sozinho em runtime porque reverse() levanta
    # NoReverseMatch quando a rota deixa de existir (item_nav trata isso,
    # T-07-08). A garantia deste teste é que o arquivo do derivado
    # SOBREVIVE ao update, não que ele fique livre de 'exemplo:'.
    [ -f "${DESTINO}/core/templates/core/_nav_dominio.html" ] || \
        falhar '_nav_dominio.html do derivado foi apagado pelo update'
}

assert_no_conflict_markers() {
    if MATCHES=$(grep -RInF --exclude-dir=.git -e '<<<<<<<' -e '=======' -e '>>>>>>>' "$DESTINO" 2>/dev/null); then
        printf 'FALHOU: marcadores inline encontrados após update:\n%s\n' "${MATCHES}" >&2
        exit 1
    fi
}

exigir_copier
# --no-tags: o repositório real já carrega a tag v0.1.0 da release. Sem esta
# flag, `git clone` traz essa tag para o clone efêmero e a criação de
# `v0.1.0` própria do ensaio (linha abaixo) falha com "tag already exists" —
# o ensaio precisa das suas PRÓPRIAS tags, isoladas de qualquer tag real do
# repositório de origem.
git clone -q --no-hardlinks --no-tags "${ROOT}" "${TEMPLATE}"
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
preparar_commit_destino
git -C "$DESTINO" commit -qm 'test: estado A gerado'
test -z "$(git -C "$DESTINO" status --porcelain)" || falhar 'estado A não ficou limpo'
COMMIT_A=$(commit_resposta)
[ -n "${COMMIT_A}" ] || falhar 'estado A não registrou _commit'

# O derivado escreve o PRÓPRIO item de menu antes do update — é o cenário
# real do critério 7 (D-89): o autor do sistema gerado edita o arquivo que é
# dele, nunca _nav.html.
printf '{%% load navegacao %%}\n{%% item_nav "core:shell" "Painel" "casa" %%}\n' \
    > "${DESTINO}/core/templates/core/_nav_dominio.html"
preparar_commit_destino
git -C "$DESTINO" commit -qm 'test: derivado declara o próprio menu'
test -z "$(git -C "$DESTINO" status --porcelain)" || falhar 'commit do menu do derivado não ficou limpo'

printf '\nAtualização contratual B: núcleo entregue pelo Copier.\n' >> "${TEMPLATE}/core/README.md"
git -C "${TEMPLATE}" add core/README.md
git -C "${TEMPLATE}" commit -qm 'test: mudança de núcleo B'
git -C "${TEMPLATE}" tag v0.1.1

exigir_limpo
"${COPIER}" update --defaults --data incluir_app_exemplo=false --vcs-ref v0.1.1 --trust "$DESTINO" >/dev/null
grep -Fq 'Atualização contratual B: núcleo entregue pelo Copier.' "${DESTINO}/core/README.md" || \
    falhar 'mudança B não chegou ao destino'
COMMIT_B=$(commit_resposta)
[ -n "${COMMIT_B}" ] && [ "${COMMIT_A}" != "${COMMIT_B}" ] || \
    falhar '_commit não avançou de A para B'
exigir_sem_exemplo
grep -Fq 'Painel' "${DESTINO}/core/templates/core/_nav_dominio.html" || \
    falhar 'update apagou os itens do derivado'
assert_no_conflict_markers "$DESTINO"
preparar_commit_destino
git -C "$DESTINO" commit -qm 'test: estado B atualizado sem exemplo'
test -z "$(git -C "$DESTINO" status --porcelain)" || falhar 'estado B não ficou limpo'

printf '\nAtualização contratual C: núcleo permanece sincronizável.\n' >> "${TEMPLATE}/core/README.md"
git -C "${TEMPLATE}" add core/README.md
git -C "${TEMPLATE}" commit -qm 'test: mudança de núcleo C'
git -C "${TEMPLATE}" tag v0.1.2

exigir_limpo
"${COPIER}" update --defaults --data incluir_app_exemplo=false --vcs-ref v0.1.2 --trust "$DESTINO" >/dev/null
grep -Fq 'Atualização contratual C: núcleo permanece sincronizável.' "${DESTINO}/core/README.md" || \
    falhar 'mudança C não chegou ao destino'
COMMIT_C=$(commit_resposta)
[ -n "${COMMIT_C}" ] && [ "${COMMIT_B}" != "${COMMIT_C}" ] || \
    falhar '_commit não avançou de B para C'
exigir_sem_exemplo
grep -Fq 'Painel' "${DESTINO}/core/templates/core/_nav_dominio.html" || \
    falhar 'update apagou os itens do derivado'
assert_no_conflict_markers "$DESTINO"
preparar_commit_destino
git -C "$DESTINO" commit -qm 'test: estado C atualizado sem ressurreição'
test -z "$(git -C "$DESTINO" status --porcelain)" || falhar 'estado C não ficou limpo'

grep -Fq 'A → B → C' "${ROOT}/README.md" || \
    falhar 'README não documenta o ensaio A → B → C'
printf 'OK: update Copier A→B→C entregou núcleo e preservou o opt-out.\n'
