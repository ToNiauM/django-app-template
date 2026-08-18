---
phase: 05-verifica-o-e-documenta-o
reviewed: 2026-08-18T20:49:11Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - README.md
  - .template-tests/test_05_nascimento.sh
  - .template-tests/test_04_04_optional_exemplo.py
  - .template-tests/test_04_07_collectstatic.py
  - apps/__init__.py
findings:
  critical: 1
  warning: 6
  info: 6
  total: 13
status: issues_found
---

# Fase 05: Relatório de Revisão de Código

**Revisado:** 2026-08-18T20:49:11Z
**Profundidade:** standard
**Arquivos revisados:** 5
**Status:** issues_found

## Summary

Revisão adversarial dos artefatos da fase de verificação e documentação: o
runbook de nascimento (`README.md`), o tracer real de nascimento
(`test_05_nascimento.sh`), dois contratos Python (`test_04_04`, `test_04_07`)
e `apps/__init__.py`. A qualidade geral é alta — quoting POSIX correto,
segredos passados por ambiente (nunca argv), trap de limpeza idempotente,
placeholders do `.env` verificados contra o `.env.example.jinja` real e URLs
do README consistentes com `config/urls.py.jinja` (`/healthz` sem barra
final, `/login/`, `/exemplo/`, `/exemplo/dashboard/`; as oito perguntas
conferem com `copier.yml`).

Há, porém, um defeito crítico de escopo de renderização: nenhum dos ensaios
pina `--vcs-ref`, e o Copier, diante de um checkout git local **limpo**,
renderiza a **última tag** — não o HEAD. O fluxo de release documentado no
README ("execute a regressão completa antes de criar a tag") é exatamente o
cenário em que HEAD está à frente da última tag: a partir da primeira release,
o gate passaria validando código antigo. Também foram encontrados um regex de
contrato que sobre-captura no Dockerfile (falso negativo possível), traps de
sinal que não encerram o script, e uma lacuna de contrato no `--keep` que
inviabiliza o checkpoint manual prescrito pelo próprio README.

`apps/__init__.py` está correto: pacote raiz de uma linha, copiado verbatim
para os sistemas gerados (não está no `_exclude` de `copier.yml`), e coberto
pelos novos asserts de `test_04_04` em ambas as variantes.

## Critical Issues

### CR-01: Ensaios rodam `copier copy` sem `--vcs-ref HEAD` — com checkout limpo e tag existente, a regressão valida a release anterior, não o código sob revisão

**File:** `.template-tests/test_05_nascimento.sh:122` (também `.template-tests/test_04_04_optional_exemplo.py:18-47`)
**Issue:** O Copier, ao copiar de um repositório git local, clona para um
diretório temporário e faz checkout da **última tag** por padrão; só inclui a
árvore de trabalho quando há mudanças não commitadas (DirtyLocalWarning). Hoje
o repositório não tem tags, então HEAD é usado por acaso — mas o
`README.md:262-299` institui o fluxo "publique em tags semver" e "antes de
criar a tag, execute a regressão completa, incluindo o ensaio de nascimento".
Nesse fluxo, no momento da regressão a árvore está limpa e commitada, e HEAD
está à frente da última tag: `test_05_nascimento.sh` e as renderizações de
`test_04_04` passariam a exercitar a release **anterior**, aprovando
silenciosamente um HEAD quebrado. O comportamento do gate muda conforme o
estado da árvore (sujo = HEAD+dirty; limpo = última tag), o que também torna o
ensaio não determinístico. (`test_copier_copy.sh`, fora do escopo desta
revisão, compartilha o padrão; `test_copier_update.sh` pina `--vcs-ref`
corretamente.)
**Fix:**
```sh
# test_05_nascimento.sh, linha 122
"${COPIER}" copy --vcs-ref HEAD --defaults \
```
```python
# test_04_04_optional_exemplo.py, lista de args em render()
[str(COPIER), "copy", "--vcs-ref", "HEAD", "--defaults", ...]
```

## Warnings

### WR-01: Regex do contrato de collectstatic sobre-captura desde o primeiro `RUN` do Dockerfile — asserts passam mesmo com o contrato quebrado

**File:** `.template-tests/test_04_07_collectstatic.py:25-42`
**Issue:** `re.search(r"RUN (?P<environment>.*?)\\\n    python manage.py collectstatic --noinput", dockerfile, re.DOTALL)`
casa a partir da **primeira** ocorrência de `RUN ` no arquivo (linha 15 do
Dockerfile, `RUN npx ...` do estágio `assets`), pois `re.search` retorna o
match mais à esquerda independentemente da lazy quantifier. O grupo
`environment` abrange três comandos `RUN` e até a fronteira de estágio
(`FROM python:3.12-slim`). Consequência: se alguém mover
`SECRET_KEY=build` (ou qualquer atribuição) para um `RUN` anterior e deixar o
`RUN` do collectstatic sem ambiente, os `assertIn` continuam passando — o
teste deixa de garantir exatamente a propriedade que existe para proteger
(build quebraria em runtime sem o gate acusar).
**Fix:**
```python
collectstatic = re.search(
    r"RUN (?P<environment>(?:[A-Za-z_]+=[^\n]*\\\n\s*)+)"
    r"python manage\.py collectstatic --noinput",
    dockerfile,
)
```
(Sem `re.DOTALL`; o grupo só aceita linhas de atribuição contíguas ao próprio
comando collectstatic.)

### WR-02: Traps de sinal executam a limpeza mas não encerram o script

**File:** `.template-tests/test_05_nascimento.sh:99` (e `:66-77`)
**Issue:** `trap limpar 0 HUP INT TERM` roda `limpar` no sinal e **retoma** a
execução. Exemplo concreto: Ctrl-C durante o `curl` da condição do `while` em
`aguardar_web` (linha 69) — `set -e` não se aplica a condições — dispara
`limpar` (containers derrubados, `${TMP}` removido, `LIMPEZA_FEITA=true`) e o
loop continua martelando um ambiente já destruído por até 180 iterações antes
de falhar com a mensagem enganosa "web não respondeu em /healthz". Além disso
o exit status de uma execução interrompida não é `128+sinal`, mascarando a
interrupção para quem orquestra o ensaio.
**Fix:**
```sh
trap limpar EXIT
for sinal in HUP INT TERM; do
    trap "limpar; trap - EXIT; exit 1" "${sinal}"
done
```

### WR-03: Com `--keep`, o operador fica sem credencial para o checkpoint manual que o README prescreve

**File:** `.template-tests/test_05_nascimento.sh:163-166,193-197` (e `README.md:253-258`)
**Issue:** O README define a inspeção manual das telas (login, shell, CRUD,
dashboard) na cópia retida com `--keep` como checkpoint do operador. Mas a
senha do admin é gerada aleatoriamente (linha 164), corretamente nunca
impressa, e `limpar` a descarta via `unset` mesmo no caminho `--keep`
bem-sucedido (linha 86). O bloco final imprime destino, projeto e URL — sem
qualquer caminho para autenticar. O único jeito de cumprir o checkpoint é
pré-exportar `NASCIMENTO_ADMIN_PASSWORD`, contrato que não aparece nem no
README nem na mensagem de uso (`uso: ... [--keep]`, linha 104). O fluxo
documentado é, na prática, inexecutável para quem seguir só a documentação.
**Fix:** Documentar `NASCIMENTO_ADMIN_PASSWORD` no README (seção Regressão) e
na mensagem de uso; e, no bloco `--keep`, imprimir a instrução de recuperação
sem vazar o segredo, por exemplo:
```sh
printf '%s\n' 'Para autenticar: exporte NASCIMENTO_ADMIN_PASSWORD antes do ensaio,'
printf '%s\n' 'ou redefina com: docker compose exec web python manage.py changepassword nascimento@example.invalid'
```

### WR-04: `export NASCIMENTO_ADMIN_PASSWORD` expõe o segredo a todos os processos filhos subsequentes desnecessariamente

**File:** `.template-tests/test_05_nascimento.sh:166,176-181`
**Issue:** O único consumo do valor é a expansão
`DJANGO_SUPERUSER_PASSWORD="${NASCIMENTO_ADMIN_PASSWORD}"` (linha 177), que
não exige export. Com o export, a senha do admin entra no ambiente de **todo**
filho a partir dali: `docker compose up --build`, `curl`, heredocs Python —
ampliando a superfície de vazamento sem necessidade. Adicionalmente, o padrão
"atribuição-prefixo antes de chamada de **função**" (`VAR=x compose ...`) tem
persistência não especificada pelo POSIX após o retorno da função (funciona em
dash/bash, mas é frágil), e `DJANGO_SUPERUSER_PASSWORD`/`DJANGO_SUPERUSER_EMAIL`
nunca são desfeitos em `limpar` (linhas 86 e 94 só cobrem as três variáveis
originais).
**Fix:** Remover o `export` da linha 166 e confinar a exportação a um
subshell:
```sh
(
    export DJANGO_SUPERUSER_EMAIL='nascimento@example.invalid'
    export DJANGO_SUPERUSER_PASSWORD="${NASCIMENTO_ADMIN_PASSWORD}"
    compose exec -T -e DJANGO_SUPERUSER_EMAIL -e DJANGO_SUPERUSER_PASSWORD \
        web python manage.py createsuperuser --noinput
) || falhar 'createsuperuser --noinput falhou'
```

### WR-05: Comando de regressão do README omite silenciosamente uma suíte de regressão existente

**File:** `README.md:226` (contexto: `.template-tests/test_quick_comentarios_template.py`)
**Issue:** O gate documentado usa
`python3 -m unittest discover -s .template-tests -p 'test_04_*.py'`, que não
casa com `test_quick_comentarios_template.py` — a suíte de regressão dos
vazamentos de comentário de template (commits `ba86084`/`ab76eb7`). Quem
seguir o README à risca antes de uma release nunca executa essa regressão, e
o bug que ela protege pode reaparecer sem detecção no gate.
**Fix:** Trocar o padrão para cobrir todos os contratos Python:
```bash
python3 -m unittest discover -s .template-tests -p 'test_*.py'
```
(ou renomear o arquivo para o namespace `test_04_*` / documentá-lo
explicitamente na lista da regressão).

### WR-06: Passo 3 do nascimento não pina a tag escolhida no passo 2

**File:** `README.md:37-44`
**Issue:** O passo 2 manda "escolher uma tag estável, por exemplo `v0.1.0`"
("sistemas nascem de releases revisadas, não de commits arbitrários"), mas o
comando do passo 3 (`copier copy /caminho/para/template /caminho/para/novo-sistema`)
não tem `--vcs-ref`. O Copier usará a **última** tag do checkout (não
necessariamente a escolhida) e, se o checkout estiver sujo, incluirá mudanças
não commitadas — contradizendo diretamente o contrato do passo 2. A escolha da
tag não tem efeito algum no comando documentado.
**Fix:**
```bash
/caminho/para/template/.venv-template/bin/copier copy --vcs-ref v0.1.0 /caminho/para/template /caminho/para/novo-sistema
```

## Info

### IN-01: Checagens de ferramentas e de versão do Copier duplicadas

**File:** `.template-tests/test_05_nascimento.sh:21-25,30-37,107-111`
**Issue:** O loop das linhas 107-109 re-verifica `docker`, `curl` e `python3`
já cobertos pelo `preflight` (linhas 30-33), e `exigir_copier` (chamado na
linha 111, **depois** do preflight) repete a verificação de versão da linha 37
— código morto na prática. **Fix:** consolidar em um único ponto (manter só o
preflight, ou chamá-lo depois das checagens rápidas e remover as duplicatas).

### IN-02: Timeout de `aguardar_web` pode exceder os "180 segundos" prometidos

**File:** `.template-tests/test_05_nascimento.sh:66-77`
**Issue:** São 180 iterações de `curl` (sem `--max-time`) + `sleep 1`; se a
conexão pendurar em vez de ser recusada, cada tentativa pode levar muito mais
que 1s e a mensagem "dentro de 180 segundos" fica incorreta. **Fix:**
`curl -fsS --max-time 2 ...`.

### IN-03: TOCTOU na alocação da porta efêmera

**File:** `.template-tests/test_05_nascimento.sh:113-120`
**Issue:** A porta é obtida com bind em `porta 0` e liberada antes do
`compose up`; outro processo pode ocupá-la na janela, produzindo uma falha de
boot com diagnóstico confuso. Risco baixo e trade-off razoável — apenas
registre que uma colisão esporádica deve ser tratada re-executando o ensaio.

### IN-04: Falha do Copier em `render()` esconde o stderr do validator

**File:** `.template-tests/test_04_04_optional_exemplo.py:18-46`
**Issue:** `subprocess.run(..., capture_output=True, check=True)` levanta
`CalledProcessError` cuja mensagem padrão não inclui o stderr capturado; erros
de validator do Copier ficam invisíveis no relatório do unittest. **Fix:**
envolver em `try/except CalledProcessError as exc: raise AssertionError(exc.stderr) from exc`
ou remover `capture_output=True`.

### IN-05: Uso inconsistente de `--env-file .env` entre os passos 10 e 11-15

**File:** `README.md:89-126`
**Issue:** O passo 10 usa `docker compose --env-file .env config -q`, mas os
passos 11-15 omitem a flag. Ambos funcionam (o Compose lê `.env` do diretório
do projeto por padrão), porém a inconsistência sugere que a flag é
significativa quando não é — enquanto `test_05_nascimento.sh` a usa em todas
as invocações. **Fix:** padronizar (remover a flag do passo 10 ou usá-la em
todos os passos).

### IN-06: Guarda `TMP_VALIDADO` é sempre verdadeira

**File:** `.template-tests/test_05_nascimento.sh:7-8,95`
**Issue:** `TMP` e `TMP_VALIDADO` são atribuídos uma única vez a partir do
mesmo `mktemp -d` e nunca reatribuídos; a comparação
`[ "${TMP}" = "${TMP_VALIDADO}" ]` antes do `rm -rf` é código morto (cinto de
segurança defensivo). **Fix:** documentar a intenção com um comentário ou
simplificar para `[ -d "${TMP}" ] && rm -rf "${TMP}"` — mantendo a proteção
real, que é `TMP` vir exclusivamente de `mktemp`.

---

_Revisado: 2026-08-18T20:49:11Z_
_Revisor: Claude (gsd-code-reviewer)_
_Profundidade: standard_
