# Phase 3 Plan 02: CRUD de Referência com Modais HTMX Summary

**Completed:** 2026-08-18
**Plan:** 03-02-PLAN.md
**Duration:** ~6 min

## What Was Done

1. **Formulário e Views de CRUD (Task 1):**
   - Criado `apps/exemplo/forms.py` (`ItemExemploForm`) baseado em `ModelForm` com validação de `clean_valor` (valores negativos proibidos) e widgets estilizados com design tokens Tailwind.
   - Implementadas as views em `apps/exemplo/views.py`:
     - `item_listar_view`: busca textual `Q(titulo__icontains=q) | Q(descricao__icontains=q)`, filtros multi-seleção via `getlist("categoria")` e `getlist("status")`, ordenação segura via whitelist `COLUNAS_ORDENACAO_PERMITIDAS` (fallback seguro `-criado_em`), paginação server-side com `Paginator(qs, 10)`, helper `extrair_querystring_filtros` e alternância entre página completa e partial HTMX.
     - `item_criar_view`: criação com modal HTMX, retornando `status=422` em formulários inválidos e `HX-Trigger: itemSalvo` em sucesso.
     - `item_editar_view`: edição com modal HTMX, retornando `status=422` em formulários inválidos e `HX-Trigger: itemSalvo` em sucesso.
     - `item_excluir_view`: modal de confirmação e exclusão segura via POST com CSRF token e `HX-Trigger: itemSalvo`.

2. **Templates, Rotas e Navegação (Task 2):**
   - Criado `apps/exemplo/urls.py` com namespace `exemplo` e conectado em `config/urls.py`.
   - Atualizado `core/templates/core/_nav.html` com o item de navegação `Itens (CRUD)` com estado ativo (`bg-brand-tint text-brand-ink` + indicador vertical 2px `bg-brand`).
   - Desenvolvidos os templates parciais e principais sob `apps/exemplo/templates/exemplo/`:
     - `item_listar.html`: casca completa com cabeçalho, breadcrumbs e botão "Novo item".
     - `_filtros.html`: formulário com busca debounced (300ms), selects de categoria e status, e botão Limpar.
     - `_tabela_resultado.html`: tabela responsiva com ordenação nos cabeçalhos (↑, ↓, ↕), badges semânticos de status, valores monetários formatados com `|moeda`, paginação com querystring preservada e botões Editar/Excluir.
     - `_form_modal.html`: modal Alpine.js com foco automático, tecla Escape, backdrop, erros inline e `form.non_field_errors`.
     - `_confirmar_exclusao_modal.html`: modal de confirmação com styling destrutivo e token CSRF.

3. **Suíte de Testes Automatizados (Task 3):**
   - Criado `apps/exemplo/tests/test_crud.py` com 11 casos de teste cobrindo autenticação obrigatória, renderização padrão vs HTMX, busca textual, filtros multi-seleção, ordenação com whitelist, paginação com preservação de filtros, ciclo completo de criação/edição/exclusão HTMX e retorno HTTP 422.
   - Todos os 11 testes executados e aprovados com 100% de sucesso.

## Key Files Created / Modified

- `apps/exemplo/forms.py` — `ItemExemploForm` com validações
- `apps/exemplo/views.py` — views do CRUD com HTMX e ordenação segura
- `apps/exemplo/urls.py` — rotas de CRUD
- `config/urls.py` — inclusão de `apps.exemplo.urls`
- `core/templates/core/_nav.html` — item de navegação `Itens (CRUD)`
- `apps/exemplo/templates/exemplo/item_listar.html` — template principal
- `apps/exemplo/templates/exemplo/_filtros.html` — partial de busca e filtros
- `apps/exemplo/templates/exemplo/_tabela_resultado.html` — partial da tabela e paginação
- `apps/exemplo/templates/exemplo/_form_modal.html` — modal de criação/edição
- `apps/exemplo/templates/exemplo/_confirmar_exclusao_modal.html` — modal de exclusão
- `apps/exemplo/tests/test_crud.py` — suíte de testes de integração e comportamento

## Verification

- `docker compose run --rm -v "$PWD:/app" --entrypoint python web manage.py test apps.exemplo.tests.test_crud` → 11/11 testes passaram (OK)
- `docker compose up -d --build` → Build do Tailwind compilou todos os seletores CSS do CRUD (14341 bytes)

## Deviations from Plan

None — implementação seguiu rigorosamente os contratos UI-SPEC e decisões D-25, D-26, D-27, D-28, D-29.
