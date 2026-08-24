---
phase: 03-app-exemplo
verified: 2026-08-18T13:20:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
human_verification_resolved: 2026-08-24
human_verification_resolution: "Fechado por cobertura já existente, decisão do operador em 2026-08-24 durante o pré-fecho do marco v0.2.0. Duas fontes: (a) automatizada — apps/exemplo/tests/test_crud.py, 11 testes cobrindo HTTP 422 em formulário inválido e HX-Trigger: itemSalvo em sucesso; (b) inspeção humana — o gate visual bloqueante da 07-08 Task 2 foi aprovado pelo operador sobre as MESMAS 4 telas (login, shell, CRUD /exemplo/, dashboard /exemplo/dashboard/) nos 2 temas, cobrindo a opacidade do véu dos modais de criação e exclusão e a repintura dos gráficos ao trocar de tema sem recarregar. LIMITE CONHECIDO E ACEITO: três comportamentos dos roteiros originais não foram exercitados por inspeção humana direta — foco automático no primeiro campo do modal, redimensionamento da janela e drill-down por clique em barra/setor do dashboard."
human_verification:
  - test: "Acessar '/exemplo/' no navegador e testar abertura de modal 'Novo item', validação de formulário (HTTP 422) e salvamento com atualização automática da tabela via evento 'itemSalvo'."
    expected: "Modal abre com foco no primeiro campo, submissão inválida exibe erros inline em vermelho sem fechar o modal, submissão válida fecha o modal e atualiza a tabela via HTMX sem recarregar a página."
    why_human: "Validação visual de modais Alpine.js + HTMX, trap de foco e atualização dinâmica da tabela requerem interação real no navegador."
  - test: "Acessar '/exemplo/dashboard/' e validar renderização dos gráficos ECharts (barras e donut), tooltips monetários formatados em pt-BR, redimensionamento de tela e drill-down por clique."
    expected: "Gráficos ECharts renderizam com paleta corporativa, tooltips exibem 'R$ X.XXX,XX', redimensionar a janela ajusta os gráficos e clicar em uma barra/setor redireciona para a listagem do CRUD pré-filtrada."
    why_human: "Renderização do canvas Apache ECharts, eventos de mouse/clique e responsividade visual só podem ser avaliados em runtime visual."
---

# Phase 3: App Exemplo Verification Report

**Phase Goal:** `apps/exemplo/` demonstra o padrão de referência da casa — CRUD completo com tabela paginada server-side, filtros e modais HTMX, mais dashboard ECharts com agregações via ORM — e é removível sem quebrar o sistema.
**Verified:** 2026-08-18T13:20:00Z
**Status:** passed (2 itens de verificação humana fechados por cobertura em 2026-08-24)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Usuário opera CRUD de exemplo com tabela paginada server-side (10 itens/pág), ordenação com whitelist e filtros multi-seleção | ✓ VERIFIED | `apps/exemplo/views.py` (`item_listar_view`) implementa `Paginator(qs, 10)`, `Q(titulo__icontains=q) \| Q(descricao__icontains=q)`, `getlist('categoria')`, `getlist('status')`, whitelist `COLUNAS_ORDENACAO_PERMITIDAS` e `extrair_querystring_filtros`. Suíte `test_crud.py` com 11 testes cobrindo todos os fluxos. |
| 2 | Usuário cria e edita registros do exemplo via modal HTMX sem recarregar a página | ✓ VERIFIED | `apps/exemplo/views.py` (`item_criar_view`, `item_editar_view`, `item_excluir_view`) retornam HTTP 422 em formulários inválidos e `HX-Trigger: itemSalvo` em sucesso. `_form_modal.html` gerencia ciclo de vida via Alpine.js e container `modal-container` dispara trigger de refresh na tabela. |
| 3 | Dashboard ECharts exibe agregações calculadas via ORM (`annotate`/`aggregate`), nunca em Python | ✓ VERIFIED | `apps/exemplo/views.py` (`dashboard_view`) calcula KPIs via `.aggregate(total_itens=Count('id'), valor_total=Sum('valor'), ...)` e gráficos via `.values('categoria').annotate(...)` e `.values('status').annotate(...)`. Template serializa com `json_script` e integra `core/static/vendor/echarts.min.js`. |
| 4 | Remover o app `exemplo` (seguindo os passos documentados) deixa o sistema íntegro | ✓ VERIFIED | `apps/exemplo/README.md` documenta os 3 pontos de acoplamento (`INSTALLED_APPS`, `urls.py`, `_nav.html`) e o checklist de 4 passos de remoção. `apps/exemplo/tests/test_isolamento.py` valida via AST zero imports reversos do `core/` sobre `apps.exemplo`. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `apps/exemplo/models.py` | Modelo `ItemExemplo` com escolhas tipadas, validações numéricas e `HistoricalRecords` | ✓ VERIFIED | 70 linhas. `CategoriaChoices`, `StatusChoices`, `MinValueValidator(Decimal('0.00'))`, `history = HistoricalRecords()`. |
| `apps/exemplo/admin.py` | Registro no admin via `SimpleHistoryAdmin` | ✓ VERIFIED | 23 linhas. Registra `ItemExemplo` com `SimpleHistoryAdmin`, filtros e busca. |
| `apps/exemplo/forms.py` | `ItemExemploForm` baseado em `ModelForm` com validação de `clean_valor` e widgets Tailwind | ✓ VERIFIED | 55 linhas. Valida valores negativos com `ValidationError` e customiza inputs com design tokens. |
| `apps/exemplo/views.py` | Views de listagem, criação, edição, exclusão e dashboard com HTMX | ✓ VERIFIED | 240 linhas. Implementa `item_listar_view`, `item_criar_view`, `item_editar_view`, `item_excluir_view` e `dashboard_view`. |
| `apps/exemplo/urls.py` | Rotas com namespace `exemplo` | ✓ VERIFIED | 15 linhas. Mapeia `item_listar`, `dashboard`, `item_criar`, `item_editar`, `item_excluir`. |
| `apps/exemplo/templates/exemplo/item_listar.html` | Template principal do CRUD com casca, breadcrumbs e container de modais | ✓ VERIFIED | 46 linhas. Extende `core/shell.html` com `@item-salvo.window` listener. |
| `apps/exemplo/templates/exemplo/_tabela_resultado.html` | Partial da tabela com cabeçalhos ordenáveis, badges semânticos e paginação com querystring | ✓ VERIFIED | 255 linhas. Paginação responsiva, filtro `|moeda` e botões de ação. |
| `apps/exemplo/templates/exemplo/_filtros.html` | Formulário de busca debounced (300ms) e filtros de categoria/status | ✓ VERIFIED | 77 linhas. `hx-trigger="input changed delay:300ms, search"` e botão Limpar filtros. |
| `apps/exemplo/templates/exemplo/_form_modal.html` | Modal Alpine.js com foco automático, tecla Escape e suporte HTTP 422 | ✓ VERIFIED | 141 linhas. Validação inline e banner de non_field_errors. |
| `apps/exemplo/templates/exemplo/_confirmar_exclusao_modal.html` | Modal de confirmação de exclusão com CSRF e estilo destrutivo | ✓ VERIFIED | 61 linhas. Confirmação segura e POST via HTMX. |
| `apps/exemplo/templates/exemplo/dashboard.html` | Template do dashboard com KPIs, `json_script`, scripts ECharts e drill-down | ✓ VERIFIED | 214 linhas. 4 cards de KPI, gráficos de barras e donut, resize listener e clique para drill-down. |
| `apps/exemplo/README.md` | Guia de arquitetura e checklist de 4 passos para exclusão do app | ✓ VERIFIED | 68 linhas. Detalha os 3 pontos de acoplamento e instruções SQL/código de remoção. |
| `apps/exemplo/management/commands/seed_exemplo.py` | Comando para popular dados de demonstração com `--limpar` e `--quantidade` | ✓ VERIFIED | 106 linhas. Cria registros variados abrangendo todas as categorias e status. |
| `core/templatetags/formatos.py` | Filtros monetários pt-BR `moeda` e `moeda_curta` | ✓ VERIFIED | 60 linhas. Formata decimais sem prefixo R$ e abrevia milhões/milhares. |
| `core/static/vendor/echarts.min.js` | Bundle local minificado do Apache ECharts 5.x | ✓ VERIFIED | 1006 KB no sistema de arquivos local. |
| `apps/exemplo/tests/test_models.py` | Testes de modelo, choices, validações, auditoria e seed | ✓ VERIFIED | 91 linhas. 5 testes passando. |
| `apps/exemplo/tests/test_crud.py` | Testes de autenticação, filtros, ordenação, paginação e modais HTMX | ✓ VERIFIED | 231 linhas. 11 testes passando. |
| `apps/exemplo/tests/test_dashboard.py` | Testes das agregações ORM do dashboard e renderização | ✓ VERIFIED | 143 linhas. 5 testes passando. |
| `apps/exemplo/tests/test_isolamento.py` | Testes AST de isolamento arquitetural e ausência de dependências reversas | ✓ VERIFIED | 53 linhas. 2 testes passando. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `config/urls.py` | `apps.exemplo.urls` | `path("exemplo/", include("apps.exemplo.urls"))` | ✓ WIRED | Linha 11 em `config/urls.py`. |
| `core/templates/core/_nav.html` | `exemplo:dashboard` | `url_exemplo_dash` | ✓ WIRED | Linha 23 e 38 em `_nav.html`. |
| `core/templates/core/_nav.html` | `exemplo:item_listar` | `url_exemplo_crud` | ✓ WIRED | Linha 24 e 49 em `_nav.html`. |
| `config/settings/base.py` | `apps.exemplo.apps.ExemploConfig` | `INSTALLED_APPS` | ✓ WIRED | Linha 37 em `config/settings/base.py`. |
| `apps/exemplo/models.py` | `HistoricalRecords` | `history = HistoricalRecords()` | ✓ WIRED | Linha 62 em `apps/exemplo/models.py`. |
| `apps/exemplo/views.py` | `apps.exemplo.forms.ItemExemploForm` | Form instantiations | ✓ WIRED | Importado e utilizado em `item_criar_view` e `item_editar_view`. |
| `apps/exemplo/templates/exemplo/dashboard.html` | `core/static/vendor/echarts.min.js` | `{% static 'vendor/echarts.min.js' %}` | ✓ WIRED | Linha 91 em `dashboard.html`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `exemplo/_tabela_resultado.html` | `pagina.object_list` | `item_listar_view` via `Paginator(ItemExemplo.objects.all(), 10)` | Sim (PostgreSQL `exemplo_itemexemplo`) | ✓ FLOWING |
| `exemplo/dashboard.html` (KPIs) | `kpis` (`total_itens`, `valor_total`, etc.) | `dashboard_view` via `ItemExemplo.objects.filter(ativo=True).aggregate(...)` | Sim (Consultas agregadas SQL) | ✓ FLOWING |
| `exemplo/dashboard.html` (Gráficos) | `dados_categoria`, `dados_status` | `dashboard_view` via `.values().annotate()` + `json_script` | Sim (Agrupamentos SQL `GROUP BY`) | ✓ FLOWING |
| `exemplo/_form_modal.html` | `form` (`ItemExemploForm`) | `item_criar_view` / `item_editar_view` via ModelForm | Sim (Campos e instâncias do banco) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Suíte de testes completa do Django | `docker compose exec -T web python manage.py test` | `Ran 46 tests in 20.088s - OK` | ✓ PASS |
| Suíte de testes do app exemplo | `docker compose exec -T web python manage.py test apps/exemplo` | `Ran 23 tests in 10.425s - OK` | ✓ PASS |
| Formatação monetária pt-BR | `python -c "from core.templatetags.formatos import moeda, moeda_curta; assert moeda('1234.56') == '1.234,56'; assert moeda_curta('1500000') == '1,5 mi'"` | Execução com sucesso (OK) | ✓ PASS |
| Comando `seed_exemplo` com `--limpar` e `--quantidade 25` | `docker compose exec -T web python manage.py seed_exemplo --limpar --quantidade 25` | `Removidos 20 registros existentes do ItemExemplo. Sucesso: 25 itens de exemplo foram criados com sucesso!` | ✓ PASS |
| Healthcheck da aplicação | `docker compose exec -T web curl -s http://127.0.0.1:8000/healthz` | `{"status": "ok"}` | ✓ PASS |
| Proteção de autenticação em `/exemplo/` | `docker compose exec -T web curl -s -I http://127.0.0.1:8000/exemplo/` | `HTTP/1.1 302 Found` (`Location: /login/?next=/exemplo/`) | ✓ PASS |
| Proteção de autenticação em `/exemplo/dashboard/` | `docker compose exec -T web curl -s -I http://127.0.0.1:8000/exemplo/dashboard/` | `HTTP/1.1 302 Found` (`Location: /login/?next=/exemplo/dashboard/`) | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| Probes convencionais | `find scripts -path '*/tests/probe-*.sh'` | Nenhum probe declarado ou existente no projeto | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| **EX-01** | 03-01, 03-02 | Usuário pode operar um CRUD completo de exemplo: tabela paginada server-side, ordenação e filtros multi-seleção | ✓ SATISFIED | `apps/exemplo/views.py` (`item_listar_view`), templates de tabela/filtros e 11 testes em `test_crud.py`. |
| **EX-02** | 03-02 | Usuário pode criar/editar registros do exemplo via modal HTMX | ✓ SATISFIED | `apps/exemplo/views.py` (`item_criar_view`, `item_editar_view`, `item_excluir_view`), `_form_modal.html` com HTTP 422 e `HX-Trigger: itemSalvo`. |
| **EX-03** | 03-03 | Usuário pode ver dashboard ECharts de exemplo com agregações feitas via ORM (`annotate`/`aggregate`), nunca em Python | ✓ SATISFIED | `apps/exemplo/views.py` (`dashboard_view`), `dashboard.html`, `core/static/vendor/echarts.min.js` e 5 testes em `test_dashboard.py`. |
| **EX-04** | 03-01, 03-03 | App `exemplo` é autocontido e removível — apagá-lo (e suas referências documentadas) não quebra o sistema | ✓ SATISFIED | `apps/exemplo/README.md` (checklist de remoção) e `apps/exemplo/tests/test_isolamento.py` (validação AST de zero acoplamento). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| None | - | - | - | Nenhum anti-pattern, stub ou debt marker não auditado encontrado nos arquivos modificados. |

### Human Verification Required

### 1. CRUD de Referência com Modais HTMX

**Test:** Acessar `/login/`, autenticar com credenciais válidas, navegar para `Itens (CRUD)` (`/exemplo/`). Clicar em "Novo item" para abrir o modal. Tentar submeter campos vazios e valores negativos para conferir os erros inline e banner de validação HTTP 422. Preencher dados válidos, salvar e verificar se o modal fecha e a tabela atualiza automaticamente via HTMX. Testar também a edição e exclusão de um registro.
**Expected:** Modais abrem com foco correto, validações inválidas permanecem no modal com erros destacados, salvamento fecha o modal e recarrega a tabela sem refresh total da página (`F5`), exclusão remove a linha após confirmação.
**Why human:** Ciclo de vida dinâmico de eventos HTMX (`@item-salvo.window`), transições de modais Alpine.js e foco de teclado exigem validação interativa no navegador.

### 2. Dashboard Analítico e Interatividade ECharts

**Test:** Navegar para `Dashboard` (`/exemplo/dashboard/`). Verificar se os 4 cards de KPI exibem valores calculados e se os gráficos de Barras por Categoria e Donut por Status são desenhados. Passar o mouse sobre as barras e setores para inspecionar os tooltips formatados em moeda (`R$`). Clicar em uma barra (ex.: Categoria "Operacional") e verificar se ocorre o drill-down para `/exemplo/?categoria=OPERACIONAL`. Redimensionar a janela do navegador para verificar o redimensionamento suave dos gráficos.
**Expected:** Gráficos interativos renderizam com paleta corporativa, tooltips exibem dados monetários formatados, redimensionamento reajusta os canvases e o clique nos gráficos direciona corretamente para o CRUD filtrado.
**Why human:** Renderização de canvas HTML5, eventos de hover/clique e responsividade visual do ECharts só podem ser avaliados em runtime visual no navegador.

### Gaps Summary

Nenhum gap de código ou arquitetura foi identificado. Todas as 4 verdades do Roadmap e requisitos (EX-01, EX-02, EX-03, EX-04) foram comprovados no código e validados com 46 testes automatizados passando 100%. A fase aguarda apenas a conferência humana no navegador (UAT).

---

_Verified: 2026-08-18T13:20:00Z_
_Verifier: the agent (gsd-verifier)_
