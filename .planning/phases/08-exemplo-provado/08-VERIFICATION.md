---
phase: 08-exemplo-provado
verified: 2026-08-26T14:05:00Z
status: passed
score: 12/12 must-haves verified
overrides_applied: 0
---

# Phase 8: Exemplo Provado — Verification Report

**Phase Goal:** O código que o guia vai ensinar existe antes do texto: o app de diárias e passagens vive como fixture em `.template-tests/fixtures/guia/`, instala numa cópia Copier real e é provado de ponta a ponta — sem nunca vazar para o template ou para o sistema gerado.
**Verified:** 2026-08-26T14:05:00Z
**Status:** passed (com 2 achados críticos herdados do app de referência registrados como avisos — ver "Anti-Patterns / Review Findings")
**Re-verification:** No — initial verification

## Verification Method

Nenhuma alegação de SUMMARY foi aceita como evidência. Toda prova abaixo foi re-executada nesta sessão de verificação: greps estruturais sobre os 22 arquivos do fixture, `py_compile` de todos os `.py`, `git ls-files`, e **execução real do test_command integral** (`python3 -m unittest discover -s .template-tests -p 'test_*.py'`) → `Ran 48 tests in 194.883s — OK`, incluindo os 6 testes de `test_08_guia_prova` contra o banco de ensaio Docker vivo (containers `ensaio8a2164277e-web-1`/`-db-1`) e os 3 de `test_08_guia_vazamento` com renders Copier reais em tempdir.

## Goal Achievement

### Observable Truths (roadmap SCs 1-4 + plan must_haves merged)

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | **SC1:** Suíte nova gera cópia Copier real via `ensaio_django.sh`, instala o fixture como `apps/diarias` e sai verde: migração aplicada, testes do app passando, smoke HTTP respondendo | ✓ VERIFIED | Executado nesta sessão: `test_08_guia_prova` 6/6 OK — `test_migrate_e_idempotente_e_sai_zero`, `test_showmigrations_prova_0001_initial_aplicada`, `test_makemigrations_check_limpo`, `test_suite_do_app_verde_dentro_do_container`, `test_smoke_anonimo_302_para_login_nas_tres_telas`, `test_smoke_autenticado_200_com_danca_real_de_csrf` |
| 2 | **SC2:** Teste negativo verde: cópia recém-nascida NÃO contém `apps/diarias` nem arquivo do fixture, nas 2 variantes | ✓ VERIFIED | `test_08_guia_vazamento` 3/3 OK executado nesta sessão: lista EXATA de `apps/` nas duas variantes de `incluir_app_exemplo`, interseção de sha256 de bytes vazia com guarda anti falso verde (`assertGreaterEqual` >= 10 hashes do fixture), `git ls-files` limpo |
| 3 | **SC3:** Suíte roda junto com as existentes pelo test_command padrão | ✓ VERIFIED | `python3 -m unittest discover -s .template-tests -p 'test_*.py'` → 48 testes OK (39 pré-existentes + 3 vazamento + 6 prova); nenhum teste de `fixtures/guia/apps/diarias/tests/` coletado no host (sem `__init__.py` em `fixtures/`, `guia/`, `apps/` — confirmado por `ls`) |
| 4 | **SC4:** Fixture cobre tudo que o guia vai ensinar: modelo, admin, listagem paginada com filtros, modal 422/`HX-Trigger`, `_nav_dominio.html` com `{% item_nav %}` e dashboard ECharts com paleta da marca | ✓ VERIFIED | `models.py` (Viagem + StatusChoices + HistoricalRecords), `admin.py` (SimpleHistoryAdmin), `Paginator(qs, 10)` + `getlist("status")` restrito a `StatusChoices.values`, 3× `"viagemSalva"` + status 422, `LINHAS_NAV` com 2 `{% item_nav "diarias:..." %}` patcheando `core/templates/core/_nav_dominio.html` (link provado por asserção HTTP no recorte do `<nav>`), `dashboard.html` com `json_script:"paleta-graficos"` + `esc()` (5×) + `tema:alterado` + zero hex. Caveat: CR-01/CR-02 herdados (ver avisos) |
| 5 | Fixture é app Django completo espelhando arquivo a arquivo o app exemplo (12 .py + 6 templates + 4 tests) | ✓ VERIFIED | 22 arquivos presentes em `.template-tests/fixtures/guia/apps/diarias/`; todos `.py` compilam; zero `.jinja`; zero resíduo `exemplo:`/`itemSalvo` |
| 6 | Modelo Viagem único, sem FK, status TextChoices, HistoricalRecords (D-01..D-04) | ✓ VERIFIED | `HistoricalRecords()` 1×; `ForeignKey` ausente em models.py; StatusChoices com 4 valores; migração cria `Viagem` + `HistoricalViagem` e `makemigrations --check` in-container saiu limpo |
| 7 | Nenhuma view acessível sem login; nenhuma ordenação de entrada crua | ✓ VERIFIED | 5× `@login_required`; `COLUNAS_ORDENACAO_PERMITIDAS` definida e usada com `.get(`; `order_by(request` ausente; 302 → `/login/` nas 3 telas provado por HTTP real |
| 8 | Dashboard consome paleta via json_script `paleta-graficos`, esc() em formatters, reconstrução em `tema:alterado` | ✓ VERIFIED | `json_script:"paleta-graficos"` presente; `corCard` declarada dentro de `montarGraficos()` (linha 179 > 166); paleta servida por `core.tema.familia_marca` na view; zero hex em views.py e dashboard.html; `id="paleta-graficos"` assertado por HTTP autenticado |
| 9 | Testes do app cobrem 302/200, 422, HX-Trigger, agregações — verdes DENTRO do container | ✓ VERIFIED | `test_suite_do_app_verde_dentro_do_container` OK nesta sessão (`manage.py test apps.diarias` código 0); test_crud.py com `force_login`, 6× 422, 3× `HX-Trigger`, 9× `reverse("diarias:...")` |
| 10 | Asserções do teste negativo são estruturais (diretório/bytes), nunca grep de "diarias" — sobrevivem à Fase 9 | ✓ VERIFIED | Interseção de sha256 de conteúdo puro + listas exatas de `apps/`; `ensaio_django` ausente do módulo (independência do banco compartilhado); guarda simétrica de fixture rastreado (22 arquivos em `git ls-files`) |
| 11 | Instalação idempotente com drift por sha256 — banco reusado nunca prova código morto | ✓ VERIFIED | Drift sha256 (caminho+conteúdo) fixture×instalado em setUpClass; `migrate diarias zero` no ramo de drift de models/migrations; harness invocado só com `subir` (`grep -E '"(testar|porta|url|executar)"'` vazio); `restart` ausente; laço próprio de `/healthz`; execução desta sessão usou a via barata (sem rebuild) e saiu verde |
| 12 | O domínio nunca vaza para o template (git ls-files limpo fora do fixture) | ✓ VERIFIED | `git ls-files | grep -E '^apps/diarias|/diarias/'` fora de `.template-tests/fixtures/` → vazio, re-executado nesta sessão |

**Score:** 12/12 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `.template-tests/fixtures/guia/apps/diarias/models.py` | Viagem + StatusChoices + HistoricalRecords | ✓ VERIFIED | Compila; contém `HistoricalRecords()`; zero FK |
| `.../views.py` | Listagem whitelist, modal 422, dashboard ORM | ✓ VERIFIED | `COLUNAS_ORDENACAO_PERMITIDAS`, `Paginator(qs, 10)`, 3× `viagemSalva`, `familia_marca` importado de `core.tema` |
| `.../urls.py` | 5 rotas com namespace | ✓ VERIFIED | `app_name = "diarias"`, 5 rotas nomeadas |
| `.../migrations/0001_initial.py` | Migração shipada Viagem+HistoricalViagem | ✓ VERIFIED | Consistência com models.py provada por `makemigrations --check` in-container (verde nesta sessão) |
| `.../admin.py` | SimpleHistoryAdmin | ✓ VERIFIED | Import e uso presentes |
| `.../management/commands/seed_diarias.py` | Seed idempotente | ✓ VERIFIED | 2× `get_or_create`, zero `random` (mas ver WR-01) |
| `.../templates/diarias/` (6 arquivos) | Espelho 1:1 do exemplo | ✓ VERIFIED | 6 arquivos; H1 `<h1 ...>Diárias e passagens</h1>` (linha 12); zero classe vetada; `hx-post` + csrf no modal |
| `.../tests/` (test_models, test_crud, test_dashboard) | Provas internas do app | ✓ VERIFIED | 12 testes verdes dentro do container nesta sessão |
| `.template-tests/test_08_guia_vazamento.py` | Teste negativo PRV-03, min 80 linhas | ✓ VERIFIED | 221 linhas; `TemporaryDirectory` 3×; `--vcs-ref` 3×; 3/3 verde |
| `.template-tests/test_08_guia_prova.py` | Prova e2e PRV-01, min 150 linhas | ✓ VERIFIED | 578 linhas; `setUpClass` presente; 6/6 verde |
| `.dockerignore` (modificado) | `dados/` excluído do contexto de build | ✓ VERIFIED | Linha 10: `dados/` — conserto que viabiliza o rebuild pós-boot que o guia ensina |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| urls.py | views.py | path() → 5 views | ✓ WIRED | 5 rotas resolvem (provado por 302/200 HTTP real e `reverse()` nos testes) |
| views.py | templates/diarias/*.html | render() com nomes do contrato | ✓ WIRED | `_tabela_resultado.html`, `_form_modal.html` etc. presentes e renderizando (200 autenticado) |
| migração 0001 | models.py | campos idênticos | ✓ WIRED | `makemigrations diarias --check --dry-run` código 0 in-container |
| test_08_guia_prova.py | ensaio_django.sh | `subir` único em setUpClass | ✓ WIRED | Parse de `ENSAIO_DESTINO/PORTA/PROJETO/URL`; nenhum outro subcomando do harness |
| test_08_guia_prova.py | cópia gerada | copytree + LINHA_SETTINGS/LINHA_URLS/LINHAS_NAV + up -d --build | ✓ WIRED | Constantes nomeadas presentes; patches idempotentes com guarda `not in texto`; nav provado por `href="/diarias/dashboard/"` no recorte do `<nav>` |
| test_08_guia_prova.py | container web | docker compose exec -T (migrate/showmigrations/test) | ✓ WIRED | 4 provas in-container verdes nesta sessão |
| dashboard.html | core/tema.py | json_script `paleta-graficos` | ✓ WIRED | View serve `familia_marca(settings.COR_PRIMARIA)`; HTTP autenticado contém `id="paleta-graficos"` |
| test_08_guia_vazamento.py | copier | render leve `--vcs-ref=HEAD` | ✓ WIRED | 2 variantes renderizadas de verdade nesta sessão (~parte dos 195s) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Suíte integral do projeto (SC3) | `python3 -m unittest discover -s .template-tests -p 'test_*.py'` | `Ran 48 tests in 194.883s — OK` | ✓ PASS |
| Prova e2e (SC1) — 6 métodos | idem (coletados no discover) | 6/6 ok contra banco de ensaio Docker vivo | ✓ PASS |
| Vazamento (SC2) — 3 métodos | idem | 3/3 ok, renders Copier reais | ✓ PASS |
| Compilação de todo o fixture | `python3 -m py_compile` (11 arquivos) | código 0 | ✓ PASS |
| Nenhum teste do fixture no host | listagem verbosa do discover | somente módulos `.template-tests/test_*.py` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| PRV-01 | 08-01, 08-02, 08-04 | Fixture instala numa cópia Copier real e passa: migração, testes do app e smoke das telas | ✓ SATISFIED | 6 testes de prova verdes nesta sessão (migração, `[X] 0001_initial`, `--check`, testes in-container, 302, 200+CSRF) |
| PRV-03 | 08-03 | Teste negativo prova que nenhum código de domínio chega ao template nem à cópia | ✓ SATISFIED | 3 testes de vazamento verdes; `git ls-files` limpo re-verificado diretamente |
| PRV-02 | — (Fase 9) | Cercas de código do guia byte-idênticas ao fixture | N/A | Mapeado para a Fase 9 em REQUIREMENTS.md — não é órfão desta fase |

Nenhum requirement órfão: REQUIREMENTS.md mapeia exatamente PRV-01 e PRV-03 para a Fase 8, ambos declarados em planos e satisfeitos.

### Anti-Patterns / Review Findings

Nenhum debt marker (TBD/FIXME/XXX/TODO) nos arquivos da fase (matches de "placeholder" são atributos HTML legítimos de inputs; "TODOS" é português). Nenhum stub: todos os artefatos são substantivos e exercitados por testes reais.

O 08-REVIEW.md registrou 2 achados críticos, confirmados por leitura de código nesta verificação, **herdados byte a byte do app de referência `apps/exemplo`** — o contrato desta fase é espelhar a referência 1:1, e os defeitos são evidência de espelhamento fiel, não de desvio:

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `views.py` / `_tabela_resultado.html` | 37-42 / cabeçalhos | CR-01: `extrair_querystring_filtros` exclui só `pagina` → parâmetro `ordem` duplicado; alternância de ordenação quebra após o 1º clique/filtro | ⚠️ Warning (herdado da referência) | UX de ordenação parcialmente quebrada em todo sistema derivado do guia |
| `_filtros.html` | 94, 104 | CR-02: `hx-trigger` sem verbo AJAX é no-op no htmx 1.9.12 → busca com debounce e filtro "ao vivo" inertes (só Enter submete) | ⚠️ Warning (herdado da referência) | O comportamento "ao vivo" que o guia se propõe a ensinar não dispara |
| `seed_diarias.py` | 40-52 | WR-01: chave do get_or_create inclui `data_inicio` derivada de `localdate()` — idempotência só vale no mesmo dia | ⚠️ Warning | Banco de ensaio reusado entre dias infla 14 linhas/dia se o seed rodar (o smoke não roda seed) |
| `views.py` | 98-101 etc. | WR-02: resposta de sucesso cria `id="modal-container"` duplicado com `x-init` morto | ⚠️ Warning (herdado) | HTML inválido, funciona por acidente do querySelector |
| `views.py` | 63-64, 76 | WR-03: `ordem_atual` ecoa parâmetro cru (sem XSS/injeção; UI dessincroniza com `?ordem=zzz`) | ⚠️ Warning (herdado) | Estado de UI inconsistente com a query real |

**Disposição:** nenhum desses achados falha um must-have ou success criterion da fase — a listagem paginada com filtros existe, filtra e pagina (provado por HTTP e testes); o defeito está na camada de disparo/toggle do DOM, idêntica à referência. **Corrigir só o fixture faria guia e referência divergirem** (o review recomenda corrigir os dois em conjunto). CR-01 e CR-02 DEVEM ser resolvidos — fixture E `apps/exemplo` juntos — antes de a Fase 9 canonizar este código no texto do guia, sob pena de propagar os defeitos a todo sistema derivado.

### Human Verification Required

Nenhum item. Todas as verdades têm evidência programática executada nesta sessão, incluindo o smoke HTTP autenticado com dança real de CSRF. Os defeitos de interatividade CR-01/CR-02 já estão estabelecidos por leitura de código (não há incerteza a resolver por teste manual).

### Gaps Summary

Nenhum gap. Os 4 success criteria do roadmap e todos os must_haves dos 4 planos estão verificados contra o codebase com execução real da suíte integral (48/48 verde). PRV-01 e PRV-03 satisfeitos. Os achados críticos do review são dívida herdada da referência `apps/exemplo` (fora do escopo do espelhamento desta fase) e estão encaminhados como pré-condição da Fase 9.

---

_Verified: 2026-08-26T14:05:00Z_
_Verifier: Claude (gsd-verifier)_
