---
phase: 05-verifica-o-e-documenta-o
verified: 2026-08-18T20:54:14Z
status: passed
score: 40/40 must-haves verified
---

# Fase 5: Verificação e Documentação — Relatório de Verificação

**Meta da fase:** O fluxo de nascimento completo é provado ponta a ponta — sistema gerado passa a suíte de testes e fica navegável sem editar código — e o README documenta do `copier copy` ao proxy/DNS.
**Verificado:** 2026-08-18T20:54:14Z
**Status:** passed

## Goal Achievement

### Observable Truths — Plano 05-01 (tracer de nascimento)

| # | Truth | Status | Evidência |
|---|-------|--------|-----------|
| 1 | Cópia Copier nova com `incluir_app_exemplo=true` sobe db/web, aceita migrate/createsuperuser (`nascimento@example.invalid`) e responde em `/healthz` e `/login/` sem editar código | ✓ VERIFIED | `.template-tests/test_05_nascimento.sh` linhas 122–190: `copier copy --data 'incluir_app_exemplo=true'`, `up -d --build db web`, `migrate --noinput`, `createsuperuser --noinput` com o e-mail fixo, smokes `curl` em `/healthz` e `/login/`. Execuções verdes registradas em 05-01-SUMMARY (69 testes) e 05-02-SUMMARY (72 testes, exit 0) |
| 2 | A cópia executa `python manage.py test core apps.exemplo --noinput` e falha encerra o ensaio com status não zero | ✓ VERIFIED | Linha 187–188 do tracer: `compose exec -T web python manage.py test core apps.exemplo --noinput \|\| falhar ...`; `falhar` faz `exit 1`; script roda com `set -eu` |
| 3 | Segredos somente no `.env`/processo efêmero, web em `127.0.0.1`, remoção por padrão só do que o ensaio criou | ✓ VERIFIED | Segredos gerados via `secrets.token_urlsafe` e escritos apenas no `.env` do destino `mktemp` (linhas 136–161); `unset` após uso; smokes e porta apenas em `127.0.0.1`; `limpar` usa `--project-name "${PROJETO}"` próprio, `down --volumes --remove-orphans` e `rm -rf` restrito a `${TMP}` de `mktemp` (linhas 79–98). Sem prune/glob |
| 4 | `--keep` conserva o ambiente somente após sucesso e fornece destino, projeto Compose e URL | ✓ VERIFIED | `limpar` só retém quando `MANTER=true` **e** `SUCESSO=true` (linha 85); `SUCESSO=true` só após todos os gates (linha 192); bloco `--keep` imprime exatamente `NASCIMENTO_DESTINO`, `NASCIMENTO_PROJETO_COMPOSE`, `NASCIMENTO_URL` (linhas 193–197), sem credenciais |

### Observable Truths — Plano 05-02 (README canônico)

| # | Truth | Status | Evidência |
|---|-------|--------|-----------|
| 5 | Operador percorre no README-raiz a jornada completa, em ordem, do `copier copy` ao login/shell/CRUD/dashboard sem executar Django/Compose na árvore Jinja | ✓ VERIFIED | Verificação de ordem re-executada agora e PASS: marcadores `copier copy` → `cp .env.example .env` → `config -q` → `up -d --build db web` → `migrate --noinput` → `createsuperuser` → `/healthz` em ordem dentro de `## Nascimento local de um sistema`; URLs `/login/`, `/exemplo/`, `/exemplo/dashboard/` presentes; todo comando de runtime só aparece após "Entre no projeto gerado" (README.md passos 5–15) |
| 6 | README separa respostas Copier de segredos locais, documenta criação do `.env` e mantém `.copier-answers.yml` versionado sem credenciais | ✓ VERIFIED | README.md passos 4 ("Segredos nunca são respostas Copier"), 5–8 (`.env` local, `SECRET_KEY`, `POSTGRES_PASSWORD`/`DATABASE_URL`, R2 placeholders) e 9 (primeiro commit preservando `.copier-answers.yml` sem credenciais) |
| 7 | Publicação conserva bind `127.0.0.1`, usa o vhost gerado para Nginx/TLS, orienta DNS e valida `/healthz` externamente | ✓ VERIFIED | Verificação de conteúdo re-executada agora e PASS: `## Publicação com proxy, TLS e DNS` contém `WEB_BIND_ADDRESS=127.0.0.1` invariante, DNS, portas 80/443, Certbot, `ops/nginx/<slug>.conf`, `nginx -t`, `https://<hostname>/healthz` externo e link `ops/MIGRACAO.md` |
| 8 | Comandos de regressão distinguem contratos da fonte, ensaio real de nascimento e inspeção manual, sem alegar automação de navegador | ✓ VERIFIED | `## Regressão do template` lista as três camadas com os quatro comandos e afirma explicitamente: "Nenhum desses comandos automatiza cliques nem regressão visual ... inspeção breve das telas no navegador ... é um checkpoint manual complementar" (README.md linhas 216–258) |

### Observable Truths — Plano 05-03 (inspeção humana 32/32)

Os 17 critérios *covered* estão sustentados pela suíte Django verde dentro da cópia gerada (72 testes, exit 0 — 05-03-SUMMARY D1) mais os passos 1–5 do checkpoint; os 15 itens `verification: backstop` são não-inferíveis e exigem evidência explícita — que **existe**: checkpoint humano bloqueante executado, usuário inspecionou o sistema no navegador (túnel SSH para a URL loopback) e aprovou explicitamente "approved" 32/32, sem nenhum identificador `[surface/state]` de falha devolvido (05-03-SUMMARY, Task 2). Nenhum backstop foi passado por presença de símbolo: a disposição é ✓ com evidência de comportamento diretamente observado por humano.

| # | Truth (identificador) | Status | Evidência |
|---|------------------------|--------|-----------|
| 9–12 | `[login-form/empty]`, `[login-form/error]` (covered); `[responsive-shell-navigation/overflow]`, `[responsive-shell-navigation/long-text]` (covered) | ✓ VERIFIED | Suíte `core` verde na cópia + passos 1–2 do checkpoint aprovado |
| 13–18 | `[crud-list/empty\|populated\|partial\|overflow\|zero-one-many\|long-text]` (covered) | ✓ VERIFIED | Suíte `apps.exemplo` verde na cópia + passo 3 do checkpoint aprovado (25 itens seed + filtro vazio) |
| 19–22 | `[crud-modal-form/empty\|error\|partial\|long-text]` (covered) | ✓ VERIFIED | Suíte `apps.exemplo` verde + passo 4 do checkpoint aprovado |
| 23–25 | `[dashboard/empty\|populated\|zero-one-many]` (covered) | ✓ VERIFIED | Suíte verde (cardinalidades) + passo 5 do checkpoint aprovado |
| 26–29 | `[login-form/loading\|partial\|overflow\|long-text]` (backstop) | ✓ VERIFIED | Confirmação visual humana explícita — checkpoint aprovado 32/32, nenhum omitido |
| 30–31 | `[responsive-shell-navigation/loading\|error]` (backstop) | ✓ VERIFIED | Idem — throttling/offline temporários de navegador, gaveta não presa |
| 32–33 | `[crud-list/loading\|error]` (backstop) | ✓ VERIFIED | Idem — swaps HTMX estáveis, recuperação confirmada |
| 34–35 | `[crud-modal-form/loading\|overflow]` (backstop) | ✓ VERIFIED | Idem — modal estável e rolável em viewport móvel |
| 36–40 | `[dashboard/loading\|error\|partial\|overflow\|long-text]` (backstop) | ✓ VERIFIED | Idem — bloqueio temporário do asset ECharts, KPIs/navegação acessíveis |

**Score:** 40/40 truths verificadas (8 inferíveis por código/execução + 17 covered + 15 backstop com evidência humana explícita; 0 abstenções — nenhum backstop ficou sem evidência)

### Required Artifacts

| Artifact | Esperado | Status | Detalhes |
|----------|----------|--------|----------|
| `.template-tests/test_05_nascimento.sh` | Tracer executável Copier → .env → Compose → migrate → createsuperuser → suíte → smoke, contendo `python manage.py test core apps.exemplo --noinput` | ✓ EXISTS + SUBSTANTIVE | 199 linhas, bit executável, `sh -n` OK; contém a string exigida (linha 187); símbolos `falhar`, `exigir_copier`, `diagnosticar`, `aguardar_web`, `limpar` e flag `--keep` presentes |
| `README.md` | Runbook canônico contendo `.template-tests/test_05_nascimento.sh` | ✓ EXISTS + SUBSTANTIVE | 299 linhas; seções `## Nascimento local de um sistema`, `## Publicação com proxy, TLS e DNS`, `## Regressão do template`; referencia o tracer nas linhas 229 e 244 |
| `.planning/phases/05-verifica-o-e-documenta-o/05-UI-SPEC.md` | Contrato visual de 17 covered + 15 backstop | ✓ EXISTS + SUBSTANTIVE | 32/32 considerações serializadas (17 covered, 15 backstop), sign-off `gsd-ui-checker` verified |
| Cópia retida do ensaio (transitória) | Ambiente Copier/Compose para inspeção | ✓ CONSUMED + REMOVED | Por design, não deve mais existir: 05-03-SUMMARY registra `down --volumes --remove-orphans` no projeto `nascimento3481424`, pós-verificação por labels e diretório removido; re-checado agora: 0 containers com o label do projeto |

**Artifacts:** 4/4 verificados

### Key Link Verification

| From | To | Via | Status | Detalhes |
|------|----|----|--------|----------|
| test_05_nascimento.sh | copier.yml | `copier copy` com 8 respostas e `incluir_app_exemplo=true` | ✓ WIRED | Linhas 122–131: `"${COPIER}" copy --defaults` com as oito `--data`, incluindo `incluir_app_exemplo=true` |
| test_05_nascimento.sh | compose.yml renderizado | `--project-name`, `config -q`, `up -d --build db web` | ✓ WIRED | Função `compose` (linhas 53–58) + linhas 168–172 |
| test_05_nascimento.sh | core/apps.exemplo tests da cópia | `exec -T web python manage.py test core apps.exemplo --noinput` | ✓ WIRED | Linha 187 |
| test_05_nascimento.sh | core.Usuario da cópia retida | `DJANGO_SUPERUSER_EMAIL=nascimento@example.invalid` + confirmação `is_staff`/`is_superuser` | ✓ WIRED | Linhas 176–185: env-only, `get_user_model().objects.get(email=...)`, assert sem tocar na senha |
| README.md | README.md.jinja | handoff para operação cotidiana do sistema renderizado | ✓ WIRED | Linhas 7–9 e 141–142: "README renderizado dentro do próprio sistema gerado" |
| README.md | ops/MIGRACAO.md | link para restore/VM/recuperação | ✓ WIRED | Linha 211: link para `ops/MIGRACAO.md` com aviso de não repetir restore no primeiro nascimento |
| README.md | test_05_nascimento.sh | mesma sequência Copier/.env/Compose/Django/HTTP | ✓ WIRED | Linhas 229 e 244–251: comando na regressão + descrição fiel dos marcos do tracer |
| `test_05_nascimento.sh --keep` | `http://127.0.0.1:<porta>/login/` | NASCIMENTO_URL + identidade fixa + senha em memória | ✓ WIRED (consumido) | 05-03-SUMMARY Task 1: extração por prefixo dos três campos, `/healthz` e `/login/` 200, superusuário confirmado, seed 25 itens |
| 05-UI-SPEC.md | `/`, `/exemplo/`, `/exemplo/dashboard/` | checkpoint manual no sistema gerado sem editar código | ✓ WIRED (consumido) | 05-03-SUMMARY Task 2: inspeção 32/32 aprovada; 0 arquivos versionados alterados durante as tasks |

**Wiring:** 9/9 conexões verificadas

## Requirements Coverage

| Requisito | Status | Blocking Issue |
|-----------|--------|----------------|
| QA-01: Template inclui suíte de testes do core e do app exemplo, e o sistema gerado passa essa suíte | ✓ SATISFIED | — Runner Django executado **dentro** da cópia Copier (não na raiz Jinja): 69–72 testes verdes em três execuções registradas; contratos da fonte re-executados agora: 15 testes OK em 69 s |
| QA-02: `copier copy` + `.env` + `compose up` + `migrate` + `createsuperuser` produz sistema navegável sem editar código | ✓ SATISFIED | — Sequência completa automatizada pelo tracer (exit 0) + navegabilidade confirmada por inspeção humana 32/32 (login, shell, CRUD, modal, dashboard) sem edição de código; ambiente efêmero removido e verificado por labels |
| DOC-01: README do template documenta o nascimento do `copier copy` ao proxy/DNS | ✓ SATISFIED | — Jornada numerada 1–15 (copy → .env → compose → migrate → createsuperuser → /healthz) + telas navegáveis + publicação proxy/TLS/DNS + regressão; ambas as verificações de ordem/conteúdo re-executadas e PASS |

**Coverage:** 3/3 requisitos satisfeitos. Cross-referência com `.planning/REQUIREMENTS.md`: QA-01, QA-02 e DOC-01 constam do documento, estão marcados `[x]` e a tabela de rastreabilidade os atribui à Fase 5 com status Complete. Os IDs declarados nos frontmatters (05-01: QA-01, QA-02; 05-02: DOC-01, QA-01, QA-02; 05-03: QA-01, QA-02) cobrem exatamente os três IDs da fase — nenhum ID órfão ou faltante.

### Prohibitions (must-NOT) dos planos

| Plano | Proibição | Disposição |
|-------|-----------|------------|
| 05-01/QA-01 (transparency) | Não declarar sucesso com testes só na árvore Jinja nem ocultar falha da suíte da cópia | ✓ HONRADA — testes rodam via `compose exec` no destino gerado; qualquer falha propaga por `\|\| falhar` + `set -eu` |
| 05-01/QA-02 (safety) | Não alterar/remover recursos que o ensaio não criou | ✓ HONRADA — cleanup restrito ao projeto Compose próprio e ao `TMP` de `mktemp`; sem prune/glob; 0 recursos remanescentes por label |
| 05-02/DOC-01 (safety) | README não instrui Django/Compose na árvore-fonte Jinja | ✓ HONRADA — aviso explícito no topo; todo comando de runtime aparece após `cd` no projeto gerado |
| 05-02/DOC-01 (transparency) | README não alega automação de cliques/regressão visual | ✓ HONRADA — declaração explícita de que a inspeção de navegador é checkpoint manual complementar |
| 05-03/QA-02 (transparency) | Checkpoint não altera UI para produzir aprovação | ✓ HONRADA — 0 arquivos versionados modificados nas tasks (único commit do plano é o SUMMARY); aprovação sem desvios |

## Anti-Patterns Found

Nenhum stub, placeholder, TODO ou arquivo vazio nos artefatos da fase. Os achados abaixo vêm do code review (05-REVIEW.md) e foram pesados contra a meta da fase:

| Origem | Achado | Severidade | Impacto na meta da fase |
|--------|--------|------------|--------------------------|
| CR-01 | `copier copy` sem `--vcs-ref HEAD` nos ensaios: com checkout limpo **e tag existente**, o Copier renderiza a última tag, não o HEAD | ⚠️ Warning (latente) | Não bloqueia: o repositório tem **0 tags** (verificado agora com `git tag`), então toda a evidência desta fase renderizou de fato o HEAD. Torna-se real na primeira release — corrigir antes de criar `v0.1.0` |
| WR-03 | Fluxo `--keep` documentado no README não explica o contrato `NASCIMENTO_ADMIN_PASSWORD`; operador que seguir só a documentação fica sem credencial para o checkpoint manual | ⚠️ Warning | Não bloqueia DOC-01: o runbook de nascimento (createsuperuser interativo) está completo; a lacuna atinge só o checkpoint de regressão do template |
| WR-06 | Passo 3 do nascimento não pina a tag escolhida no passo 2 (`--vcs-ref v0.1.0`) | ⚠️ Warning (latente) | Mesma raiz de CR-01; sem tags hoje, sem efeito prático ainda |
| WR-05 | Padrão `test_04_*.py` do README omite `test_quick_comentarios_template.py` | ⚠️ Warning | Não bloqueia: a suíte completa (`test_*.py`) foi re-executada agora — 15 testes OK |
| WR-01/02/04, IN-01..06 | Robustez do regex de contrato, traps de sinal, escopo de export, duplicações | ℹ️ Info/Warning | Qualidade/robustez; nenhum invalida a evidência produzida |

**Anti-patterns:** 0 bloqueadores, 4 warnings latentes/documentais, demais informativos.

## Human Verification Required

Nenhuma pendente. O checkpoint humano bloqueante desta fase (Plano 05-03 Task 2) **já foi executado e aprovado**: o usuário inspecionou pessoalmente o sistema gerado no navegador (túnel SSH para a URL loopback) e aprovou 32/32 sem desvios; o ambiente efêmero foi integralmente removido em seguida (0 containers/redes/volumes por label Compose). A evidência está registrada em `05-03-SUMMARY.md`.

## Gaps Summary

**Nenhum gap crítico.** A meta da fase está atingida: o nascimento foi provado ponta a ponta em uma cópia Copier real (build, boot, migrate, superusuário, 72 testes Django, smokes HTTP), a navegabilidade foi confirmada por inspeção humana 32/32 sem editar código, e o README documenta do `copier copy` ao proxy/TLS/DNS com verificações de ordem/conteúdo passando.

### Non-Critical Gaps (podem ser tratados em seguida, antes da primeira release)

1. **Ensaios sem `--vcs-ref HEAD` (CR-01/WR-06 do review)**
   - Issue: a partir da primeira tag semver, `test_05_nascimento.sh`, `test_04_04_optional_exemplo.py` e o passo 3 do README passam a renderizar a release anterior em vez do HEAD/tag escolhida.
   - Impacto: nulo hoje (0 tags no repositório — a evidência desta fase é do HEAD); silenciosamente perigoso após `v0.1.0`.
   - Recomendação: aplicar os fixes propostos no 05-REVIEW.md **antes de criar a primeira tag**.

2. **Contrato `NASCIMENTO_ADMIN_PASSWORD` do `--keep` não documentado (WR-03)**
   - Issue: o README prescreve a inspeção manual na cópia retida, mas não documenta que a senha do admin precisa ser pré-exportada (ou redefinida via `changepassword`).
   - Impacto: limitado — afeta a conveniência do checkpoint de regressão, não o nascimento de sistemas.
   - Recomendação: documentar a variável na seção de regressão e/ou imprimir instrução de recuperação no bloco `--keep`.

3. **Padrão de descoberta do README omite `test_quick_comentarios_template.py` (WR-05)**
   - Issue: `-p 'test_04_*.py'` não cobre a regressão dos vazamentos de comentário.
   - Impacto: limitado — a suíte completa continua verde (re-executada nesta verificação).
   - Recomendação: trocar para `-p 'test_*.py'` no README.

## Recommended Fix Plans

Nenhum plano de correção é exigido para fechar a fase (status passed). Se o orquestrador quiser fechar os gaps não críticos antes da primeira release, um único plano pequeno basta:

### 05-04-PLAN.md (opcional): Pinar vcs-ref e fechar lacunas documentais da regressão

**Objective:** Tornar os ensaios determinísticos frente a tags futuras e completar o contrato do `--keep` no README.

**Tasks:**
1. Adicionar `--vcs-ref HEAD` em `test_05_nascimento.sh` e `test_04_04_optional_exemplo.py` (e avaliar `test_copier_copy.sh`); pinar `--vcs-ref <tag>` no passo 3 do README.
2. Documentar `NASCIMENTO_ADMIN_PASSWORD` na regressão do README e trocar o padrão de descoberta para `test_*.py`.
3. Verificar: suíte `test_*.py` verde + verificações de ordem/conteúdo do README passando.

**Estimated scope:** Small

## Verification Metadata

**Verification approach:** Goal-backward (meta da fase → truths dos três PLANs → artefatos reais)
**Must-haves source:** frontmatters de 05-01/05-02/05-03-PLAN.md
**Automated checks:** re-executados nesta verificação — suíte completa `python3 -m unittest discover -s .template-tests -p 'test_*.py'` (15 testes, OK, 69 s), duas verificações Python de ordem/conteúdo do README (PASS), `sh -n` + bit executável do tracer, `copier 9.17.1`, greps dos key_links, `git tag` (0 tags), 0 recursos Docker com o label do ensaio. O tracer shell não foi re-executado (proibido pelo contexto de execução; evidência em 05-01/05-02/05-03-SUMMARY).
**Human checks required:** 0 pendentes (checkpoint 32/32 já aprovado pelo usuário e registrado)
**Honest-verifier:** 15 truths `verification: backstop` — todas com evidência explícita (comportamento diretamente observado no checkpoint humano); 0 abstenções `insufficient_spec`
**Total verification time:** ~6 min

---
*Verificado: 2026-08-18T20:54:14Z*
*Verificador: Claude (gsd-verifier)*
