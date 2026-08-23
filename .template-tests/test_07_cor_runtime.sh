#!/bin/sh
# Prova executável de D-80: "trocar COR_PRIMARIA no .env e recriar o
# container (docker compose up -d, sem reconstruir a imagem) muda a paleta
# inteira, nos dois temas, sem rebuild de imagem" é a afirmação mais
# importante da Fase 7 — este script é a única prova de que ela é
# verdadeira, e não apenas prosa dentro de um plano.
#
# NÃO roda em /opt/sistema_base: o checkout do template não é um projeto
# Django rodável (não há compose.yml, só compose.yml.jinja; não há
# config/settings/base.py, só .py.jinja; não há container web nenhum para
# "sistema_base"). A troca de cor só é observável dentro de uma cópia
# gerada — é o banco de ensaio do plano 07-01 (.template-tests/ensaio_django.sh)
# que a fornece.
#
# `up -d web`, NUNCA `restart web`: docker compose restart religa o MESMO
# container — ele não recria nada e portanto não relê o env_file (o
# ambiente de um container é fixado no momento da CRIAÇÃO). compose.yml.jinja
# não monta volume nenhum para .env dentro do container e .dockerignore
# exclui .env da imagem: COR_PRIMARIA só chega pelo ambiente do container,
# e só um `up -d` (recriação) relê esse ambiente. `up -d` sem reconstruir a
# imagem não é rebuild: ele reaproveita a imagem existente e só recria o
# container — é por isso que comparar o ID da imagem antes/depois (passo 6)
# é a prova certa de "sem rebuild", não a ausência de um comando de build
# no roteiro.
#
# Depois de um `compor up -d web`, a suíte NUNCA chama de volta o
# subcomando `porta`/`subir` de ensaio_django.sh para redescobrir a porta:
# garantir_banco() ali faz UMA única tentativa de curl em /healthz (sem
# retry) e, chamado logo depois de um `up -d` que acabou de recriar o
# container, quase sempre encontra o serviço ainda subindo — interpreta
# isso como "banco não saudável" e detona um `derrubar` + recriação
# completa (copier copy + build do zero), inclusive com uma porta NOVA.
# WEB_PORT nunca muda quando só COR_PRIMARIA é editada — por isso a porta é
# capturada UMA vez no passo 1 e reaproveitada em todos os passos
# seguintes; quem espera a nova porta responder é o laço de curl PRÓPRIO
# desta suíte, com retry, nunca uma chamada a ensaio_django.sh.
#
# Orçamento de tempo: os passos 1, 4 e 7 chamam o banco de ensaio e podem
# esperar /healthz; o passo 1 pode até recriar o banco inteiro. Rode esta
# suíte com o timeout longo (600000 ms) do contrato do plano 07-01, nunca
# com o timeout padrão de 120s.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
ENSAIO="${ROOT}/.template-tests/ensaio_django.sh"

falhar() {
    printf 'FALHOU: %s\n' "$1" >&2
    exit 1
}

# --- estado capturado para a restauração (trap) -----------------------
ENSAIO_DESTINO=''
PORTA=''
IMAGEM_ANTES=''
COR_TROCADA=false

esperar_healthz() {
    # Laço de retry PRÓPRIO desta suíte — nunca delega a espera a um
    # subcomando de ensaio_django.sh (ver comentário de cabeçalho).
    tentativas=0
    while [ "${tentativas}" -lt 180 ]; do
        curl -fsS "http://127.0.0.1:${PORTA}/healthz" >/dev/null 2>&1 && return 0
        tentativas=$((tentativas + 1))
        sleep 1
    done
    return 1
}

# A suíte roda no mesmo banco de ensaio que os outros gates da fase usam;
# deixá-lo com a cor trocada faria o próximo plano medir a coisa errada.
# restaurar() NÃO pode ter set -e ativo: sob set -e, uma falha DENTRO do
# próprio handler mascararia o motivo real da reprovação da suíte — por
# isso cada comando abaixo termina em "|| :" e o trap captura e repropaga
# o código de saída ORIGINAL, nunca o da restauração.
restaurar() {
    if [ "${COR_TROCADA}" = true ] && [ -n "${ENSAIO_DESTINO}" ]; then
        sed -i 's/^COR_PRIMARIA=.*/COR_PRIMARIA=#1e40af/' "${ENSAIO_DESTINO}/.env" 2>/dev/null || :
        bash "${ENSAIO}" compor up -d web >&2 2>/dev/null || :
        if [ -n "${PORTA}" ]; then
            esperar_healthz || :
        fi
    fi
}
trap 'codigo=$?; restaurar; exit "$codigo"' EXIT

# --- Passo 1: subir o banco de ensaio e capturar a linha de base ------
saida_subir=$(bash "${ENSAIO}" subir)
ENSAIO_DESTINO=$(printf '%s\n' "${saida_subir}" | sed -n 's/^ENSAIO_DESTINO=//p')
ENSAIO_URL=$(printf '%s\n' "${saida_subir}" | sed -n 's/^ENSAIO_URL=//p')
PORTA=$(printf '%s\n' "${saida_subir}" | sed -n 's/^ENSAIO_PORTA=//p')
[ -n "${ENSAIO_DESTINO}" ] && [ -n "${ENSAIO_URL}" ] && [ -n "${PORTA}" ] || \
    falhar 'ensaio_django.sh subir não devolveu ENSAIO_DESTINO/ENSAIO_URL/ENSAIO_PORTA'

# ID da imagem do serviço web — é isto que MUDARIA num rebuild. Se o Compose
# local não expuser `images -q`, o passo seguinte falharia ruidosamente;
# nesta máquina `images -q web` funciona e devolve o ID real da imagem.
IMAGEM_ANTES=$(bash "${ENSAIO}" compor images -q web)
[ -n "${IMAGEM_ANTES}" ] || falhar 'não foi possível capturar o ID da imagem web antes da troca de cor'

# --- Passo 2: a linha de base responde com o default do copier.yml ----
corpo_antes=$(curl -fsS "${ENSAIO_URL}/login/") || falhar 'GET /login/ falhou na linha de base'
printf '%s' "${corpo_antes}" | grep -Fq -- '--cor-brand: #1e40af' || \
    falhar 'linha de base não contém --cor-brand: #1e40af — o banco de ensaio não está respondendo ao default do copier.yml'
qtd_blocos_antes=$(printf '%s' "${corpo_antes}" | grep -c -- '--cor-brand:')
[ "${qtd_blocos_antes}" -ge 2 ] || \
    falhar "linha de base tem só ${qtd_blocos_antes} bloco(s) de --cor-brand: — esperado ao menos 2 (um por tema)"

# --- Passo 3: trocar COR_PRIMARIA no .env da cópia real ----------------
grep -Fq 'COR_PRIMARIA=#1e40af' "${ENSAIO_DESTINO}/.env" || \
    falhar '.env da cópia não tinha COR_PRIMARIA=#1e40af antes da troca — pré-condição quebrada'
sed -i 's/^COR_PRIMARIA=.*/COR_PRIMARIA=#0f766e/' "${ENSAIO_DESTINO}/.env"
COR_TROCADA=true

# --- Passo 4: recriar SÓ o web (up -d, sem reconstruir a imagem) e reesperar
bash "${ENSAIO}" compor up -d web >&2 || falhar 'docker compose up -d web falhou ao recriar com a nova cor'
esperar_healthz || falhar 'web não respondeu em /healthz depois da troca de COR_PRIMARIA'

# --- Passo 5: a cor nova resolve, a antiga sumiu ------------------------
corpo_depois=$(curl -fsS "${ENSAIO_URL}/login/") || falhar 'GET /login/ falhou depois da troca de cor'
printf '%s' "${corpo_depois}" | grep -Fq -- '--cor-brand: #0f766e' || \
    falhar 'a cor não resolve em runtime: --cor-brand: #0f766e ausente depois de trocar COR_PRIMARIA e recriar o web'
if printf '%s' "${corpo_depois}" | grep -Fq -- '--cor-brand: #1e40af'; then
    falhar 'a cor antiga (--cor-brand: #1e40af) ainda aparece depois da troca — a derivação não está lendo o .env em runtime'
fi

# --- Passo 6: prova de "sem rebuild" — o ID da imagem não mudou --------
IMAGEM_DEPOIS=$(bash "${ENSAIO}" compor images -q web)
[ "${IMAGEM_ANTES}" = "${IMAGEM_DEPOIS}" ] || \
    falhar 'a imagem foi reconstruída — a cor não está resolvendo em runtime'

# --- Passo 7: restaurar o estado do banco de ensaio ---------------------
sed -i 's/^COR_PRIMARIA=.*/COR_PRIMARIA=#1e40af/' "${ENSAIO_DESTINO}/.env"
bash "${ENSAIO}" compor up -d web >&2 || falhar 'docker compose up -d web falhou ao restaurar a cor original'
esperar_healthz || falhar 'web não respondeu em /healthz depois da restauração'
corpo_restaurado=$(curl -fsS "${ENSAIO_URL}/login/") || falhar 'GET /login/ falhou depois da restauração'
printf '%s' "${corpo_restaurado}" | grep -Fq -- '--cor-brand: #1e40af' || \
    falhar 'a restauração não voltou ao default #1e40af — banco de ensaio ficaria em estado alterado para os planos seguintes'
COR_TROCADA=false

printf '%s\n' 'OK: COR_PRIMARIA comanda a família de marca inteira em runtime, sem rebuild de imagem, e o banco de ensaio foi restaurado.'
