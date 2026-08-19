---
phase: 06-customiza-o-visual-e-persist-ncia-de-dados
reviewed: 2026-08-19T12:05:12Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - .env.example.jinja
  - .gitignore.jinja
  - .template-tests/test_04_05_backup.py
  - .template-tests/test_05_nascimento.sh
  - .template-tests/test_06_persistencia.py
  - README.md
  - README.md.jinja
  - compose.yml.jinja
  - copier.yml
  - core/README.md
  - core/static/img/logo-entidade.svg
  - core/static/img/logo-subsistema.svg
  - core/templates/base.html
  - core/templates/core/login.html
  - core/templates/core/shell.html
  - core/tests/test_logos.py
  - ops/MIGRACAO.md.jinja
findings:
  critical: 1
  warning: 6
  info: 3
  total: 10
status: issues_found
---

# Phase 06: Code Review Report

**Reviewed:** 2026-08-19T12:05:12Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

Revisão adversarial da fase 06 (customização visual e persistência de dados): bind mount do PostgreSQL, `.gitignore` gerado, logos por arquivo fixo e documentação de operação/migração. A implementação central (bind mount no `compose.yml.jinja`, `.gitignore.jinja`, templates com `{% static %}`) está correta e bem testada nos caminhos felizes.

Os defeitos concentram-se nos runbooks operacionais e nas bordas do contrato de persistência: o procedimento de restauração de dump do `ops/MIGRACAO.md.jinja` não funciona como escrito (o dump baixado morre junto com o container efêmero — falha em cenário de recuperação de desastre, exatamente quando o operador está sob pressão); o atalho de migração de named volume no `README.md.jinja` falha silenciosamente se o volume antigo não existir; e a proteção D-73 pode ser reintroduzida silenciosamente por um `PGDATA_DIR` sem prefixo `./`, footgun que a sintaxe longa de volumes eliminaria estruturalmente. Dois testes novos têm lacunas que enfraquecem exatamente o que seus docstrings prometem provar.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Dump baixado do R2 é destruído junto com o container efêmero — o runbook de recuperação não funciona como escrito

**File:** `ops/MIGRACAO.md.jinja:66-75`
**Issue:** O passo de download grava o dump em `/tmp/restore.dump` **dentro** do container criado por `docker compose run --rm`:

```sh
docker compose run --rm --entrypoint rclone backup copyto \
  "r2:${R2_BUCKET}/daily/<dump-mais-recente>.dump" /tmp/restore.dump
```

O serviço `backup` não tem nenhum volume no `compose.yml.jinja`, e `--rm` remove o container (e sua camada de escrita) ao final do comando. O `rclone copyto` termina com sucesso, mas o arquivo deixa de existir imediatamente. O passo seguinte lê do **host** (`... < /caminho/para/restore.dump`), portanto a sequência documentada nunca produz um restore. Este é o runbook de recuperação de desastre — falhar aqui significa um operador travado no meio de uma migração/recuperação real. (Defeito pré-existente da fase 04-06, mas a fase 06 editou este arquivo e esta é a fase de persistência — é o momento de corrigir.)

**Fix:** Montar um diretório do host no container efêmero e gravar o dump nele:

```sh
docker compose run --rm -v "$(pwd):/restore" --entrypoint rclone backup copyto \
  "r2:${R2_BUCKET}/daily/<dump-mais-recente>.dump" /restore/restore.dump
```

E ajustar o comando de restore para `< ./restore.dump` (lembrando de remover o arquivo depois — ele contém dados de produção).

## Warnings

### WR-01: Comandos do runbook interpolam variáveis do `.env` que não existem no shell do host

**File:** `ops/MIGRACAO.md.jinja:65-75, 85`
**Issue:** `"r2:${R2_BUCKET}/daily/"`, `--username="$POSTGRES_USER" --dbname="$POSTGRES_DB"` e `curl ... :${WEB_PORT}/healthz` são expandidos pelo shell do **host**, mas o runbook nunca instrui a exportar o `.env` (`docker compose` lê o `.env` para interpolar o compose file, não para popular o shell do operador). Como escrito, `pg_restore` roda com `--username=` vazio e o `rclone lsf` consulta `r2:/daily/` — todos os comandos da seção 3 e o smoke da seção 4 falham numa VM limpa.
**Fix:** Ou instruir explicitamente no início da seção 3: `set -a; . ./.env; set +a`, ou fazer a expansão dentro do container, que já tem as variáveis:

```sh
docker compose exec -T db sh -c \
  'pg_restore --clean --if-exists --no-owner --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' \
  < ./restore.dump
```

### WR-02: Atalho de migração de named volume cria volume vazio silenciosamente e simula sucesso

**File:** `README.md.jinja:121-123`
**Issue:** No atalho documentado:

```bash
docker run --rm -v {{ sistema_slug }}_pgdata:/de -v "$(pwd)/dados/pg:/para" \
  postgres:17 sh -c 'cp -a /de/. /para/'
```

se o volume `{{ sistema_slug }}_pgdata` não existir (sistema já migrado, VM diferente, projeto Compose renomeado), o Docker **cria um volume vazio com esse nome sem avisar**, o `cp` copia nada, e o comando termina com código 0. O operador acredita que os dados migraram; o próximo `up` roda `initdb` num diretório vazio e o sistema nasce sem os dados — a classe exata de perda silenciosa que a D-73 combate. O parágrafo seguinte ainda instrui `docker volume rm {{ sistema_slug }}_pgdata`, que nesse cenário removeria o volume vazio recém-criado, mascarando o rastro do erro.
**Fix:** Precondicionar a existência do volume no próprio bloco documentado:

```bash
docker volume inspect {{ sistema_slug }}_pgdata >/dev/null || { echo "volume antigo não existe"; exit 1; }
docker run --rm -v {{ sistema_slug }}_pgdata:/de -v "$(pwd)/dados/pg:/para" \
  postgres:17 sh -c 'cp -a /de/. /para/'
```

### WR-03: Sintaxe curta de volume permite reintroduzir silenciosamente o risco D-73 via `PGDATA_DIR` sem prefixo

**File:** `compose.yml.jinja:21`
**Issue:** Com `- ${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data`, um valor como `PGDATA_DIR=dados` (sem `./`) é interpretado pelo Compose como **named volume** — recriando exatamente o risco de `down -v` destruir o banco que esta fase existe para eliminar. Hoje a única defesa é um comentário no `.env.example` (linhas 42-47), que ninguém valida em runtime. A sintaxe longa de volumes elimina o footgun por construção: com `type: bind`, qualquer valor é tratado como caminho e um valor inválido falha ruidosamente no `up` em vez de degradar para named volume.
**Fix:**

```yaml
    volumes:
      - type: bind
        source: ${PGDATA_DIR:-./dados/pg}
        target: /var/lib/postgresql/data
        bind:
          create_host_path: true
```

Ajustar em conjunto a asserção de string literal em `.template-tests/test_06_persistencia.py:64-66` (a asserção estrutural via `docker compose config --format json` em `test_04_05_backup.py:78` já cobre `type == "bind"` e continua passando).

### WR-04: `PGDATA_DIR` customizado escapa do `.gitignore` gerado — D-74 só vale para o default

**File:** `.gitignore.jinja:12`, `.env.example.jinja:42-47`, `README.md.jinja:29-34`
**Issue:** O `.gitignore` gerado ignora apenas `/dados/`. O template convida o operador a trocar o caminho (`PGDATA_DIR=./banco/pg`, por exemplo) em três documentos diferentes, e nenhum deles avisa que o novo caminho precisa entrar no `.gitignore`. Resultado num sistema com caminho customizado dentro do repositório: `git add .` ou tenta commitar o diretório do banco, ou (mais provável, com o diretório 700/uid 999) passa a falhar com erro de permissão em todo `git status`/`git add` — quebrando o fluxo de commit documentado no nascimento. O objetivo declarado de D-74 ("`git add .` nunca commita `/dados/`") não se sustenta fora do default.
**Fix:** Acrescentar uma frase nos três pontos de documentação: "se mudar `PGDATA_DIR` para um caminho relativo dentro do repositório, adicione esse caminho ao `.gitignore` antes do primeiro `up`". Alternativa mais forte: documentar que caminhos customizados devem ser absolutos e fora do repositório.

### WR-05: Teste do `.gitignore` gerado não distingue o arquivo renderizado do verbatim do template

**File:** `.template-tests/test_06_persistencia.py:92-102`
**Issue:** `GitignoreGeradoTests` afirma validar que "o sistema gerado nasce com `.gitignore` **renderizado**" (mecanismo `.jinja` vence o verbatim, Pitfall 3). Mas as duas únicas asserções de conteúdo — `.env` e `/dados/` — estão presentes **tanto** em `.gitignore.jinja` quanto no `.gitignore` verbatim do template (que também seria copiado, já que não está no `_exclude`). Se uma regressão futura invertesse a precedência e o verbatim do template vencesse, este teste continuaria verde. A única linha que distingue os dois arquivos é `.venv-template/`, presente apenas no verbatim.
**Fix:** Adicionar a asserção discriminante:

```python
self.assertNotIn(".venv-template/", linhas)
```

### WR-06: Asserção de `alt` quebra em sistemas cuja sigla contém caracteres HTML-escapáveis

**File:** `core/tests/test_logos.py:46`
**Issue:** O docstring do arquivo promete "o mesmo teste precisa passar em qualquer sistema gerado do template", mas:

```python
self.assertIn('alt="Logo de ' + settings.SISTEMA_SIGLA, conteudo)
```

compara a sigla crua contra HTML autoescapado. O validator Copier de `sistema_sigla` exige apenas não-vazio (`copier.yml:77-82`) — uma sigla legítima como `P&D` vira `P&amp;D` no HTML renderizado e o teste falha no sistema gerado, derrubando inclusive o ensaio de nascimento (`test_05` roda `manage.py test core`).
**Fix:**

```python
from django.utils.html import escape
self.assertIn('alt="Logo de ' + escape(settings.SISTEMA_SIGLA), conteudo)
```

## Info

### IN-01: Checagens de ferramentas e do Copier triplicadas no tracer

**File:** `.template-tests/test_05_nascimento.sh:21-25, 29-49, 115-117`
**Issue:** `exigir_copier` (executável + versão), o `preflight` (executável + versão + `command -v` de docker/curl/python3) e o loop `for ferramenta` (docker/curl/python3 de novo) verificam as mesmas condições três vezes, em ordens diferentes (`preflight` roda antes de `exigir_copier` e já checa a versão). Redundância que dilui a mensagem de erro canônica de cada checagem.
**Fix:** Consolidar tudo no `preflight` e remover o loop das linhas 115-117; manter `exigir_copier` apenas se a mensagem específica de versão for desejada, chamando-o de dentro do `preflight`.

### IN-02: Loop de espera do healthcheck do banco sem timeout no runbook

**File:** `ops/MIGRACAO.md.jinja:56-59`
**Issue:** O `until ... sleep 2; done` espera para sempre se o `db` nunca ficar `healthy` (por exemplo, `PGDATA_DIR` apontando para a raiz de um disco com `lost+found`, cenário citado no próprio `.env.example`). Num runbook, um loop infinito sem instrução de saída deixa o operador sem sinal de falha.
**Fix:** Limitar as tentativas (ex.: `for i in $(seq 1 60); do ...; done` seguido de `docker compose logs db`) ou instruir a inspecionar os logs se a espera passar de N segundos.

### IN-03: `capture_output=True` + `check=True` engole o stderr do Copier nas falhas de render

**File:** `.template-tests/test_06_persistencia.py:28-53`, `.template-tests/test_04_05_backup.py:20-45`
**Issue:** Quando o `copier copy` falha, `subprocess.CalledProcessError` é levantada com o stderr capturado mas **não exibido** (o `__str__` da exceção mostra só comando e returncode). O desenvolvedor vê "returned non-zero exit status 1" sem a mensagem do validator/Jinja que explicaria a falha.
**Fix:** Envolver a chamada e re-levantar com contexto:

```python
try:
    subprocess.run([...], check=True, ...)
except subprocess.CalledProcessError as erro:
    raise AssertionError(f"copier copy falhou:\n{erro.stderr}") from erro
```

---

_Reviewed: 2026-08-19T12:05:12Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
