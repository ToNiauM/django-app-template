#!/bin/sh
# Matriz integrada do template: renderiza variantes reais sem tocar no host.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
COPIER="${ROOT}/.venv-template/bin/copier"
TMP=$(mktemp -d)

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

copiar() {
    destino="$1"
    exemplo="$2"
    nome="$3"
    slug="$4"
    hostname="$5"
    porta="$6"
    banco="$7"
    sigla="$8"
    cor="$9"

    # --vcs-ref=HEAD: com uma tag de release no repositório, o Copier copiaria por
    # padrão a última tag — o teste precisa do estado atual do template.
    "${COPIER}" copy --defaults --vcs-ref=HEAD \
        --data "sistema_nome=${nome}" \
        --data "sistema_slug=${slug}" \
        --data "sistema_hostname=${hostname}" \
        --data "sistema_porta=${porta}" \
        --data "sistema_banco=${banco}" \
        --data "sistema_sigla=${sigla}" \
        --data "cor_primaria=${cor}" \
        --data "incluir_app_exemplo=${exemplo}" \
        "${ROOT}" "${destino}" >/dev/null
}

auditar_neutralidade() {
    python3 - "$1" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
tokens = (
    "sistema_base",
    "Sistema Base",
    "PCA",
    "CFC",
    "orcamento",
    "financeiro",
    "dividaativa",
    "orcamento.cfc.org.br",
    "cfc.org.br",
    "toniaum/pca",
    "github.com/ToNiauM/pca",
    "pca_rehearsal_",
    "pca_pgdata",
    "_retention_test",
    "dominio-da-vps",
)


def occurrences(text: str, token: str):
    """Encontra o identificador como unidade lexical, sem falsos positivos."""
    return (match.start() for match in re.finditer(
        rf"(?<!\w){re.escape(token)}(?!\w)", text, flags=re.IGNORECASE
    ))


hits = []
for path in sorted(root.rglob("*")):
    relative = path.relative_to(root).as_posix()
    for token in tokens:
        for column in occurrences(relative, token):
            hits.append(f"path:{relative}:1:{column + 1}:{token}")
    if not path.is_file():
        continue
    text = path.read_bytes().decode("utf-8", errors="replace")
    if relative == ".copier-answers.yml":
        # `_src_path` é metadado obrigatório do Copier para viabilizar update.
        # Ele aponta para o checkout local do template, não é identidade do
        # sistema gerado; só este valor de metadado é neutralizado na auditoria.
        text = re.sub(r"(_src_path:\s*)[^,}\n]+", r"\1<origem-copier>", text)
    for token in tokens:
        for position in occurrences(text, token):
            line = text.count("\n", 0, position) + 1
            previous_newline = text.rfind("\n", 0, position)
            column = position + 1 if previous_newline < 0 else position - previous_newline
            hits.append(f"content:{relative}:{line}:{column}:{token}")

if hits:
    print("FALHOU: identidade, domínio ou artefato interno encontrado:", file=sys.stderr)
    print("\n".join(hits), file=sys.stderr)
    raise SystemExit(1)
PY
}

exigir_ausencia_de_artefatos_template() {
    destino="$1"
    for item in \
        .planning .template-tests copier.yml .venv-template IDEIA.md REVIEW.md CLAUDE.md \
        .copier-answers.yml.jinja; do
        [ ! -e "${destino}/${item}" ] || falhar "artefato interno chegou ao destino: ${item}"
    done
    if find "${destino}" -name '*.jinja' -print -quit | grep -q .; then
        falhar 'fonte .jinja chegou ao destino gerado'
    fi
}

exigir_operacao() {
    destino="$1"
    exemplo="$2"
    slug="$3"

    cp "${destino}/.env.example" "${destino}/.env"
    python3 -m compileall -q "${destino}/config" "${destino}/core"
    if [ "${exemplo}" = true ]; then
        python3 -m compileall -q "${destino}/apps/exemplo"
    fi
    (
        cd "${destino}"
        docker compose --env-file .env config >/dev/null
    )
    for script in entrypoint.sh ops/backup/backup.sh ops/backup/retencao.sh \
        ops/backup/entrypoint.sh ops/backup/ensaio_restore_local.sh \
        ops/backup/testar_retencao.sh ops/backup/testar_ensaio_restore.sh; do
        sh -n "${destino}/${script}"
    done
    sh "${destino}/ops/backup/testar_ensaio_restore.sh" >/dev/null
    grep -Fq 'manter_ultimos()' "${destino}/ops/backup/retencao.sh" || \
        falhar 'retenção não usa a função compartilhada'
    grep -Fq 'trap limpar 0' "${destino}/ops/backup/testar_retencao.sh" || \
        falhar 'teste de retenção não tem cleanup confinado'
    grep -Fq 'listen 443 ssl' "${destino}/ops/nginx/${slug}.conf" || \
        falhar 'vhost TLS não foi renderizado'
    grep -Fq 'http://127.0.0.1:' "${destino}/ops/nginx/${slug}.conf" || \
        falhar 'vhost não aponta para loopback'
    grep -Fq 'pg_restore --clean --if-exists --no-owner' "${destino}/ops/MIGRACAO.md" || \
        falhar 'runbook portátil de restore ausente'
}

exigir_variante() {
    destino="$1"
    exemplo="$2"
    nome="$3"
    sigla="$4"
    slug="$5"

    [ -f "${destino}/.copier-answers.yml" ] || falhar 'respostas Copier não foram persistidas'
    grep -Fq "# ${nome}" "${destino}/README.md" || falhar 'README renderizado não corresponde ao sistema'
    grep -Fq "Sistema Django **${sigla}**" "${destino}/README.md" || \
        falhar 'README do sistema não foi renderizado'
    ! grep -Fq 'Template Django com Copier' "${destino}/README.md" || \
        falhar 'README interno do template chegou ao sistema'
    ! grep -Eq '^(SECRET_KEY|POSTGRES_PASSWORD|R2_ACCESS_KEY_ID|R2_SECRET_ACCESS_KEY):' \
        "${destino}/.copier-answers.yml" || falhar 'segredo entrou nas respostas Copier'
    grep -Fq 'SECRET_KEY=replace-with-' "${destino}/.env.example" || \
        falhar 'placeholder de SECRET_KEY ausente'
    grep -Fq 'POSTGRES_PASSWORD=replace-with-' "${destino}/.env.example" || \
        falhar 'placeholder de senha PostgreSQL ausente'
    exigir_ausencia_de_artefatos_template "${destino}"
    auditar_neutralidade "${destino}"
    exigir_operacao "${destino}" "${exemplo}" "${slug}"

    # Guarda anti-v0.1.0: se a árvore gerada não vem do working tree (--vcs-ref=HEAD
    # ausente ou quebrado), o Copier renderiza a última tag e estas duas asserções
    # falham ruidosamente em vez de o gate passar em silêncio medindo versão antiga.
    [ -f "${destino}/core/static/img/logo-entidade.svg" ] || \
        falhar 'árvore gerada não tem o logo da Fase 6: a suíte está renderizando uma tag antiga, não o HEAD'
    # -F faria substring: '_commit: v0.1.0' também bate em 'v0.1.0-48-g3014d27' (o
    # describe correto do HEAD). -E ancora no separador/fim para exigir a tag exata.
    ! grep -Eq '_commit: v0\.1\.0(,|$)' "${destino}/.copier-answers.yml" || \
        falhar 'árvore gerada registrou _commit: v0.1.0 — falta --vcs-ref=HEAD'

    if [ "${exemplo}" = true ]; then
        [ -d "${destino}/apps/exemplo" ] || falhar 'app exemplo ausente na variante true'
        grep -Fq 'apps.exemplo.apps.ExemploConfig' "${destino}/config/settings/base.py" || \
            falhar 'settings não integra app exemplo'
        grep -Fq 'apps.exemplo.urls' "${destino}/config/urls.py" || \
            falhar 'urls não integra app exemplo'
        grep -Fq 'exemplo:' "${destino}/core/templates/core/_nav.html" || \
            falhar 'navegação não integra app exemplo'
    else
        [ ! -e "${destino}/apps/exemplo" ] || falhar 'app exemplo chegou na variante false'
        ! grep -Fq 'apps.exemplo' "${destino}/config/settings/base.py" || \
            falhar 'settings manteve acoplamento do exemplo'
        ! grep -Fq 'apps.exemplo' "${destino}/config/urls.py" || \
            falhar 'urls manteve acoplamento do exemplo'
        ! grep -Fq 'exemplo:' "${destino}/core/templates/core/_nav.html" || \
            falhar 'navegação manteve acoplamento do exemplo'
    fi
}

exigir_invalido() {
    chave="$1"
    valor="$2"
    destino="${TMP}/invalido-${chave}"
    set +e
    "${COPIER}" copy --defaults \
        --data sistema_nome=SistemaInvalido \
        --data sistema_slug=invalido \
        --data sistema_hostname=invalido.exemplo.gov.br \
        --data sistema_porta=8123 \
        --data sistema_banco=invalido \
        --data sistema_sigla=SI \
        --data cor_primaria='#2255aa' \
        --data "${chave}=${valor}" \
        "${ROOT}" "${destino}" >"${TMP}/${chave}.out" 2>"${TMP}/${chave}.err"
    status=$?
    set -e
    [ "${status}" -ne 0 ] || falhar "validator aceitou ${chave}=${valor}"
    [ ! -f "${destino}/.copier-answers.yml" ] || \
        falhar "validator deixou destino utilizável para ${chave}=${valor}"
}

exigir_copier
copiar "${TMP}/com-exemplo" true 'Sistema Aurora Com Exemplo' aurora aurora.exemplo.gov.br 8123 aurora SACE '#2255aa'
copiar "${TMP}/sem-exemplo" false 'Sistema Boreal Sem Exemplo' boreal boreal.exemplo.gov.br 8234 boreal SBEX '#116699'
exigir_variante "${TMP}/com-exemplo" true 'Sistema Aurora Com Exemplo' SACE aurora
exigir_variante "${TMP}/sem-exemplo" false 'Sistema Boreal Sem Exemplo' SBEX boreal

exigir_invalido sistema_nome ''
exigir_invalido sistema_slug 'invalido-slug'
exigir_invalido sistema_hostname 'https://invalido.exemplo.gov.br'
exigir_invalido sistema_porta 80
exigir_invalido cor_primaria '#abc'

printf 'OK: matriz Copier copy, exclusões, neutralidade e operação passou.\n'
