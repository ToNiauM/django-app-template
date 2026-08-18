---
phase: 02-shell-visual-e-kernel
plan: 02
subsystem: shell-visual
tags: [django, templates, alpine, htmx, tailwind, breadcrumbs, navegacao]
requires:
  - "02-01: context processor identidade ({{ sistema_nome }}/{{ sistema_sigla }}) e tokens Tailwind (brand/page/surface/ink) + regra [x-cloak]"
provides:
  - "Shell autenticado completo (D-09): aside fixa 232px no desktop, gaveta Alpine no mobile com overlay, estado desktop reativo via listener de matchMedia (Pitfall 8)"
  - "Blocos de página do shell (D-11): cabecalho_pagina (breadcrumbs + h1 titulo_pagina) e conteudo_pagina — contrato que o apps/exemplo da Fase 3 estende"
  - "core/_nav.html (D-10): ponto de extensão de navegação com contrato de item documentado (aria-current, classes ativo/inativo, fechamento da gaveta)"
  - "core/_breadcrumbs.html (D-12): contrato trilha — lista de dicts rotulo/url montada pela view; último item sem url vira <span aria-current=\"page\">"
  - "base.html com body neutro (Pitfall 11 fechado) e título default via {{ sistema_nome }} (D-16); login centrado por wrapper próprio"
affects: [02-03, 02-04, fase-3-apps-exemplo]
tech-stack:
  added: []
  patterns:
    - "Estado de breakpoint reativo no Alpine: matchMedia + listener de change alimentando x-data (nunca leitura direta de window em x-show)"
    - "Empilhamento fixo do shell: header mobile z-30 < overlay z-40 < aside z-50 (gaveta aberta cobre o header)"
    - "Breadcrumbs sem templatetag: a view monta a trilha com dados do contexto; o partial só renderiza"
key-files:
  created:
    - core/templates/core/_breadcrumbs.html
    - core/templates/core/_nav.html
    - core/tests/test_shell.py
  modified:
    - core/templates/core/shell.html
    - core/templates/base.html
    - core/templates/core/login.html
    - core/views.py
decisions:
  - "Kernel da fase entrega ZERO template tags customizadas por decisão: D-12 veta templatetag com ORM por trás e a trilha vem pronta da view — o item 'template tags' de CORE-04 é atendido deliberadamente sem tags (resposta explícita, não lacuna)"
  - "Botão Sair mantém o padrão da Fase 1: <form hx-post> com {% csrf_token %} de fallback no-JS (IN-02) — em vez de botão solto com hx-post, preservando logout funcional sem JavaScript"
  - "Nomes dos blocos do base.html (titulo/content/scripts) mantidos (Assumption A5); D-11 vale para os blocos internos do shell; shell expõe também titulo_pagina_head para compor o <title> com · {{ sistema_sigla }}"
  - "Comentário pré-existente do base.html reformulado para não conter o literal 'hx-boost' (critério de aceitação: zero ocorrências em core/templates/)"
metrics:
  duration: 7min
  completed: 2026-08-18
---

# Phase 2 Plan 02: Shell Visual (aside + gaveta + nav + breadcrumbs) Summary

Shell autenticado completo com aside fixa/gaveta Alpine reativa a breakpoint, navegação como ponto de extensão (`_nav.html`), breadcrumbs pelo contrato `trilha` e blocos de página nomeados — a interface pública que o `apps/exemplo` da Fase 3 consumirá; body do base.html destravado sem quebrar o login centrado.

## O que foi construído

### Task 1 — Partials `_breadcrumbs.html`/`_nav.html` + trilha no shell_view (commit d9669ef)

- `core/templates/core/_breadcrumbs.html`: transplante generalizado do partial canônico. Contrato `trilha` documentado em pt-BR no topo: lista de dicts `{"rotulo": str, "url": str|None}` montada PELA VIEW; itens com `url` viram `<a>`, o último (sempre sem `url`) vira `<span aria-current="page">`; separador `/` com `aria-hidden="true"`; tipografia `text-xs font-medium uppercase text-ink-2`. O partial nunca consulta banco nem usa templatetag com ORM.
- `core/templates/core/_nav.html`: ponto de extensão de navegação (D-10). Item "Início" com detecção de ativo por `request.path == url_inicio` → `aria-current="page"`, `bg-brand-tint text-brand-ink` e barra vertical de 2px `bg-brand`; inativo usa `text-ink-2 hover:bg-surface-2`; `@click="if (!desktop) sidebarAberta = false"` fecha a gaveta no mobile (depende do x-data do shell). Comentário documenta o contrato de item para apps de domínio copiarem. Sem `hx-swap-oob` e sem querystring (específicos do domínio de origem).
- `core/views.py`: `shell_view` passa `trilha = [{"rotulo": "Início", "url": None}]` como exemplo vivo; docstring atualizada explicando o contrato em pt-BR.

### Task 2 — shell.html completo + base.html destravado + login centrado (commit 573a6db)

- `core/templates/core/shell.html`: raiz `x-data` com `desktop: window.matchMedia('(min-width: 768px)').matches` e `sidebarAberta: false`; `x-init` registra listener de `change` do MediaQueryList (Pitfall 8 comentado — x-show não reavalia sem dependência reativa). Header mobile `z-30` com hambúrguer; overlay `z-40` (`x-show="sidebarAberta && !desktop" x-cloak`); aside `z-50` `w-[232px]` (`x-show="sidebarAberta || desktop" x-cloak`) — empilhamento comentado. Topo da aside com `{{ sistema_sigla }}`/`{{ sistema_nome }}` (D-16, sem logo de domínio); corpo com `{% include "core/_nav.html" %}`; rodapé com avatar de iniciais (`usuario_atual.email|slice:":2"|upper`), e-mail truncado e Sair via `<form hx-post>` + `{% csrf_token %}` (fallback no-JS). `<main class="flex-1 md:ml-[232px] px-6 pb-6 pt-20 md:py-6 min-w-0">` com `{% block cabecalho_pagina %}` (breadcrumbs + `<h1>{% block titulo_pagina %}Início{% endblock %}</h1>`) e `{% block conteudo_pagina %}` (card de boas-vindas neutro). `<title>` composto por `{% block titulo_pagina_head %} · {{ sistema_sigla }}`.
- `core/templates/base.html`: body virou `min-h-screen bg-page text-ink font-sans text-base` (centering removido — Pitfall 11 comentado); default do `{% block titulo %}` agora é `{{ sistema_nome }}`.
- `core/templates/core/login.html`: card envolvido em wrapper `min-h-screen flex flex-col items-center justify-center px-4`; título `Entrar · {{ sistema_nome }}`.

### Task 3 — Testes do shell + rebuild + suíte completa (commit 83d9743)

- `core/tests/test_shell.py` (5 testes): nav com `aria-current` + identidade + e-mail no shell autenticado; redirect para `/login/` sem sessão (T-02-03); contrato `trilha` via `render_to_string` (link no meio, texto puro no último); blocos default renderizados na raiz; regressão do login centrado (`justify-center` no corpo).
- `docker compose up -d --build`: imagem reconstruída (templates novos + CSS com classes brand emitidas pela primeira vez), `web` healthy.

## Verificação

- Suíte completa no container: **21/21 OK** (13 Fase 1 + 3 identidade + 5 shell).
- `manage.py check`: sem erros.
- `grep -c "brand-tint" core/static/dist/tailwind.css` no container: 1 (tokens de marca agora emitidos).
- `curl -fsS http://127.0.0.1:8000/healthz` → `{"status": "ok"}`.
- `grep -rn "PCA\|pca" core/templates/ core/views.py` — zero menções a domínio nos arquivos tocados.
- `grep -rc "hx-boost" core/templates/` soma 0 (D-09).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Bloqueio de critério] Comentário pré-existente do base.html continha o literal "hx-boost"**
- **Found during:** Task 2 (critério `grep -rc "hx-boost" core/templates/` soma 0)
- **Issue:** O comentário de CSRF da Fase 1 no `base.html` mencionava "hx-boost" como explicação — o grep do critério não distingue comentário de uso real.
- **Fix:** Comentário reformulado ("o htmx não reescreve <html>/<body> nas trocas parciais") mantendo a explicação sem o literal.
- **Files modified:** core/templates/base.html
- **Commit:** 573a6db

**2. [Menor] Botão Sair como `<form hx-post>` em vez de `<button hx-post>` solto**
- **Found during:** Task 2
- **Issue:** O plano descrevia botão com `hx-post` + `{% csrf_token %}`; um `csrf_token` exige um `<form>` ao redor para o fallback no-JS funcionar de fato (padrão IN-02 da Fase 1).
- **Fix:** Rodapé usa `<form hx-post="{% url 'core:logout' %}" hx-target="body">` com o token dentro — mesmo comportamento htmx, fallback real sem JS.
- **Files modified:** core/templates/core/shell.html
- **Commit:** 573a6db

## Nota deliberada: zero template tags customizadas

O kernel desta fase entrega ZERO template tags customizadas por decisão: D-12 veta templatetag com ORM por trás e a trilha vem pronta da view. O item "template tags" de CORE-04 é atendido deliberadamente sem tags — resposta explícita para a verificação pós-execução, não uma lacuna.

## Known Stubs

Nenhum — a nav tem um único item ("Início") por design (ponto de extensão documentado; apps de domínio adicionam os seus na Fase 3), e o conteúdo default do `conteudo_pagina` é o fallback legítimo do bloco que as telas de domínio sobrescrevem.

## Threat Flags

Nenhuma superfície nova fora do threat model do plano: nenhum endpoint novo, nenhum `@login_not_required` adicionado, trilha montada só pela view (sem input de usuário), nenhum `|safe` nos partials.

## Self-Check: PASSED

- 7 arquivos criados/modificados existem no disco.
- Commits d9669ef, 573a6db e 83d9743 presentes no histórico.
- Suíte completa e `check` passando no container; `web` healthy.
