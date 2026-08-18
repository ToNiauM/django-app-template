---
phase: 02-shell-visual-e-kernel
verified: 2026-08-18T05:10:00Z
status: passed
score: 23/23 must-haves verified
---

# Phase 2: Shell Visual e Kernel Verification Report

**Phase Goal:** O app `core` entrega a experiência visual completa e agnóstica de domínio: layout base com navegação e breadcrumbs, admin com identidade visual, PWA parametrizado e `django-simple-history` pronto para os modelos de domínio.
**Verified:** 2026-08-18T05:10:00Z
**Status:** passed
**Mode:** mvp (nota: o goal da fase não está em formato user-story; a cobertura de fluxo abaixo foi derivada dos success criteria do ROADMAP)

## User Flow Coverage

Fluxo do usuário derivado dos critérios da fase: «Usuário loga, navega no shell com nav/breadcrumbs, admin exibe a identidade, sistema instala como PWA, auditoria pronta para o domínio.»

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Abrir o sistema anônimo | Redirect para /login/ | `curl / anon → 302 /login/?next=/` (LoginRequiredMiddleware intacto) | ✓ |
| Ver a tela de login | Página centrada com identidade | `/login/` → 200; wrapper `justify-center` em login.html; título `Entrar · {{ sistema_nome }}` | ✓ |
| Navegar no shell logado | Aside fixa desktop / gaveta mobile, nav com item ativo, breadcrumbs | shell.html (aside `md:!flex` + gaveta Alpine), _nav.html (`aria-current="page"`), _breadcrumbs.html + `trilha` no shell_view; test_shell.py 5 testes OK | ✓ |
| Acessar /admin/ | Identidade visual do sistema | curl `/admin/login/` sem auth já mostra `Sistema Base — Administração`, `<title>… | SB</title>` e `--primary: #1e40af` injetado via extrastyle | ✓ |
| Instalar como PWA | manifest + SW + ícones parametrizados | curl `/manifest.json` → JSON com name/short_name/theme_color dos settings + 3 ícones via static(); `/sw.js` → 200 com `Service-Worker-Allowed: /` | ✓ |
| Auditoria pronta | Mudança em Usuario gera histórico com autor | Shell live-check: `create_user` → `history.count()==1`, tipo `+`; middleware + testes provam `history_user`; convenção D-23 no core/README.md | ✓ |

## Goal Achievement

### Observable Truths

#### Plan 02-01 (identidade parametrizada)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SISTEMA_NOME/SIGLA/COR_PRIMARIA como settings do .env com defaults + context processor (D-16) | ✓ VERIFIED | config/settings/base.py (env com defaults); `core.context_processors.identidade` registrado (linha 115); test_identidade.py passa |
| 2 | COR_PRIMARIA fora de #RRGGBB derruba o boot | ✓ VERIFIED | Executado no container com `COR_PRIMARIA=red`: `ImproperlyConfigured` com mensagem pt-BR (base.py:156-157) |
| 3 | Classes bg-page/bg-surface/text-ink existem no CSS gerado (Pitfall 6) | ✓ VERIFIED | No container: `grep bg-page core/static/dist/tailwind.css` ≥ 1 |
| 4 | Tokens brand derivam de UM único hex literal (D-17) | ✓ VERIFIED | tailwind.config.js: `const COR_PRIMARIA = "#1e40af"` + `misturar()` deriva brand-hover/brand-ink/brand-tint |
| 5 | Regra [x-cloak] no CSS final (Pitfall 7) | ✓ VERIFIED | input.css:16 + `grep x-cloak` no dist do container ≥ 1 (escopada a <768px pelo fix WR-02, deliberado) |

#### Plan 02-02 (shell visual)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 6 | Aside lateral fixa no desktop e gaveta Alpine no mobile (D-09) | ✓ VERIFIED | shell.html:46-47 — aside `md:!flex` (visibilidade desktop 100% CSS, fix WR-02/011d4c6) + `x-show="sidebarAberta"` para a gaveta; overlay z-40 `md:hidden`; teste trava `md:!flex` |
| 7 | _nav.html com item ativo via aria-current="page" comparando request.path (D-10) | ✓ VERIFIED | _nav.html:22-27: `{% url 'core:shell' as url_inicio %}` + `request.path == url_inicio` → `aria-current="page"` |
| 8 | Breadcrumbs pelo contrato trilha; último item sem url (D-12) | ✓ VERIFIED | _breadcrumbs.html (span aria-current no item sem url); shell_view monta `trilha` (views.py:143-144); teste de render_to_string passa |
| 9 | Blocos cabecalho_pagina/titulo_pagina/conteudo_pagina (D-11) | ✓ VERIFIED | shell.html:98-111 — os 3 blocos presentes com defaults reais |
| 10 | Login continua centrado após body destravado (Pitfall 11) | ✓ VERIFIED | base.html body sem centering (0 ocorrências); login.html com wrapper `justify-center` (1); teste de regressão passa |
| 11 | Título e header usam {{ sistema_nome }} — nenhum nome hard-coded (D-16) | ✓ VERIFIED | `grep "Sistema Base" shell.html` = 0; base.html e shell.html usam `{{ sistema_nome }}`/`{{ sistema_sigla }}` |

#### Plan 02-03 (admin + auditoria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 12 | /admin/ exibe nome do sistema e cor primária (CORE-03) | ✓ VERIFIED | curl `/admin/login/`: `Sistema Base — Administração` + `--primary: #1e40af`; test_admin.py passa |
| 13 | Zero register em core/admin_site.py (D-13) | ✓ VERIFIED | `grep -c register core/admin_site.py` = 0 |
| 14 | Usuario editável no admin por e-mail, sem username | ✓ VERIFIED | core/admin.py: UsuarioAdmin, `grep -c username` = 0; changelist 200 provado por teste |
| 15 | Salvar Usuario gera HistoricalUsuario; edições via request registram history_user (CORE-06) | ✓ VERIFIED | Live-check no shell: create → history count 1, tipo `+`; test_auditoria.py prova history_user; campos password/last_login EXCLUÍDOS do histórico (WR-01 — estado final intencional, migração 0003 aplicada) |
| 16 | core/README.md documenta a convenção `history = HistoricalRecords()` (D-23) | ✓ VERIFIED | README linhas 53-79: convenção nº 4 com exceção do user model e alerta `bulk_update_with_history` |
| 17 | D-14: override cirúrgico só do bloco extrastyle | ✓ VERIFIED | core/templates/admin/base_site.html: 11 linhas, só `extrastyle` + `{{ admin_tema_css\|safe }}` |
| 18 | D-15: nenhum agrupamento custom do índice do admin | ✓ VERIFIED | Nenhum `get_app_list`/`admin_grupo` em core/admin_site.py ou core/admin.py |

#### Plan 02-04 (PWA)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 19 | GET /manifest.json sem login → 200 com identidade dos settings e ícones via static() (D-18) | ✓ VERIFIED | curl sem sessão: 200, `name: Sistema Base`, `short_name: SB`, `theme_color: #1e40af`, 3 ícones `/static/img/...` |
| 20 | GET /sw.js sem login → 200 na raiz com Service-Worker-Allowed: / (D-19) | ✓ VERIFIED | curl -I: `HTTP 200`, `Content-Type: application/javascript`, `Service-Worker-Allowed: /` |
| 21 | SW cacheia só /static/, pré-cacheia offline.html, fallback de navegação; HTML/HTMX nunca em cache | ✓ VERIFIED | Corpo live do sw.js: `navigate` → network-first sem cache.put; guarda `startsWith("/static/")`; `static-v1` + offline.html pré-cacheado; teste asserta a estratégia |
| 22 | Sair limpa Cache Storage + htmx-history-cache ANTES do POST; body com hx-history="false" (V3) | ✓ VERIFIED | base.html:23 (`hx-history="false"`), :50 (`limparCachePwa()`); shell.html:82 `hx-on::before-request` no form hx-post |
| 23 | Ícones placeholder neutros regeneráveis por script (D-20) | ✓ VERIFIED | 3 PNGs com IHDR validado (192/512/512); ops/gerar_icones_pwa.py presente, zero menção a domínio |

**Score:** 23/23 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `config/settings/base.py` | Settings identidade + validação + processor registrado | ✓ EXISTS + SUBSTANTIVE | 7 matches de SISTEMA_*/COR_PRIMARIA; ImproperlyConfigured; processor registrado |
| `core/context_processors.py` | `def identidade` | ✓ EXISTS + SUBSTANTIVE | Linha 10, retorna os 3 valores dos settings |
| `tailwind.config.js` | Paleta + brand-tint derivado | ✓ EXISTS + SUBSTANTIVE | brand-hover/ink/tint via `misturar()`; único hex de marca |
| `core/static/src/input.css` | Regra [x-cloak] | ✓ EXISTS + SUBSTANTIVE | Linha 16 (escopada mobile pelo WR-02) |
| `core/tests/test_identidade.py` | Prova do contrato | ✓ EXISTS + SUBSTANTIVE | 30 linhas, 3 testes passando |
| `core/templates/core/shell.html` | Shell completo, contains cabecalho_pagina, min 60 linhas | ✓ EXISTS + SUBSTANTIVE | 114 linhas; aside + gaveta + blocos + rodapé com Sair |
| `core/templates/core/_nav.html` | aria-current + contrato documentado | ✓ EXISTS + SUBSTANTIVE | Contrato de item em comentário pt-BR; item Início ativo |
| `core/templates/core/_breadcrumbs.html` | Contrato trilha | ✓ EXISTS + SUBSTANTIVE | 11 ocorrências de `trilha`; span aria-current no último item |
| `core/views.py` | shell_view com trilha; manifest_view/service_worker_view exportadas | ✓ EXISTS + SUBSTANTIVE | trilha:143; manifest_view:148; service_worker_view:198; ambas @login_not_required |
| `core/tests/test_shell.py` | Prova nav/breadcrumbs/blocos/login | ✓ EXISTS + SUBSTANTIVE | Inclui teste do md:!flex pós-fix |
| `core/admin_site.py` | SistemaAdminSite com each_context, zero register | ✓ EXISTS + SUBSTANTIVE | each_context:40 injeta admin_tema_css; 0 registers |
| `core/apps.py` | SistemaAdminConfig com default_site | ✓ EXISTS + SUBSTANTIVE | default_site:26, default = False:30 |
| `core/admin.py` | simple_history.register + UsuarioAdmin | ✓ EXISTS + SUBSTANTIVE | register(Usuario, excluded_fields=["password","last_login"]):24 |
| `core/templates/admin/base_site.html` | Override cirúrgico extrastyle | ✓ EXISTS + SUBSTANTIVE | 11 linhas, só o bloco extrastyle |
| `core/migrations/0002_historicalusuario.py` | Tabela histórica | ✓ EXISTS + APPLIED | showmigrations: [X] 0002 e [X] 0003 (exclusão de campos, pós-review) |
| `core/README.md` | Convenção D-23 | ✓ EXISTS + SUBSTANTIVE | HistoricalRecords + bulk_update_with_history documentados |
| `core/tests/test_admin.py` / `test_auditoria.py` | Provas admin/auditoria | ✓ EXIST + SUBSTANTIVE | Passando na suíte |
| `core/urls.py` | Rotas manifest.json e sw.js na raiz | ✓ EXISTS + SUBSTANTIVE | Linhas 13-14, nomeadas core:manifest/core:service_worker |
| `core/static/offline.html` | Fallback neutro autocontido | ✓ EXISTS + SUBSTANTIVE | 2137 bytes; zero hex de marca (grep 1e40af/003c71 = 0) |
| `core/static/img/icon-{192,512,512-maskable}.png` | Ícones PWA | ✓ EXIST + VALID | Assinatura PNG + IHDR 192/512/512 confirmados via struct |
| `ops/gerar_icones_pwa.py` | Script de regeneração | ✓ EXISTS + SUBSTANTIVE | CLI cor/sigla com defaults; sem menção a domínio |
| `core/tests/test_pwa.py` | Prova manifest/sw/ícones | ✓ EXISTS + SUBSTANTIVE | 11 testes passando |

**Artifacts:** 22/22 verified

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| config/settings/base.py | core/context_processors.py | context_processors | ✓ WIRED | `core.context_processors.identidade` na linha 115 |
| tailwind.config.js | dist/tailwind.css | build multi-stage | ✓ WIRED | `bg-page`/`brand-tint` presentes no CSS dentro do container |
| core/views.py | _breadcrumbs.html | contexto trilha | ✓ WIRED | shell_view passa `trilha`; shell.html:100 `include ... with trilha=trilha` |
| shell.html | _nav.html | include no x-data | ✓ WIRED | Linha 68 |
| _nav.html | tokens de marca | bg-brand-tint/text-brand-ink | ✓ WIRED | Linhas 27-28 |
| settings | core/apps.py | INSTALLED_APPS | ✓ WIRED | `core.apps.SistemaAdminConfig` substitui o admin plain (linha 33, sem duplicata) |
| core/apps.py | core/admin_site.py | default_site | ✓ WIRED | `core.admin_site.SistemaAdminSite`; teste prova a instância |
| admin_site.py | admin/base_site.html | admin_tema_css | ✓ WIRED | each_context → extrastyle; curl confirma `--primary` no HTML servido |
| settings | simple_history | INSTALLED_APPS + middleware | ✓ WIRED | HistoryRequestMiddleware entre auth e htmx (linhas 48-52) |
| base.html | /manifest.json + /sw.js | link rel + serviceWorker.register | ✓ WIRED | Linhas 10 e 66 (`scope: "/"`) |
| core/views.py | icon-*.png | static() no manifest | ✓ WIRED | 5 chamadas static(); manifest live resolve os 3 src |
| shell.html | limparCachePwa (base.html) | hx-on::before-request | ✓ WIRED | Form Sair linha 82; função global no base.html linha 50 |

**Wiring:** 12/12 connections verified

## Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| CORE-03: Admin customizado com identidade visual | ✓ SATISFIED | - |
| CORE-04: Layout base com navegação, breadcrumbs, context processors e middleware | ✓ SATISFIED | Item "template tags" atendido deliberadamente com ZERO tags (D-12 veta templatetag com ORM; trilha vem da view — decisão registrada no plano e no SUMMARY, não lacuna) |
| CORE-05: PWA (manifest, ícones, service worker) parametrizada pelo nome do sistema | ✓ SATISFIED | - |
| CORE-06: django-simple-history configurado como padrão de auditoria | ✓ SATISFIED | - |

**Coverage:** 4/4 requirements satisfied

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| core/templates/core/_nav.html | 15, 25 | `@click="if (!desktop) ..."` referencia estado Alpine `desktop` removido pelo fix WR-02 (011d4c6) | ⚠️ Warning | No mobile, o clique no link dispara Alpine Expression Error no console (`desktop` indefinido) e o fechamento explícito da gaveta não roda — sem impacto funcional porque a navegação é full page load (D-09) e o reload fecha a gaveta de qualquer forma. Porém este é o "contrato de item" documentado que os apps da Fase 3 copiarão; corrigir para `@click="sidebarAberta = false"` (e ajustar o comentário) na próxima passada |

**Anti-patterns:** 1 found (0 blockers, 1 warning)

## Human Verification Required

Todos os must-haves automatizáveis foram verificados por CLI/curl/testes. Restam apenas confirmações visuais de UX de navegador, não bloqueantes:

### 1. Prompt de instalação PWA
**Test:** No Chrome/Edge logado em 127.0.0.1:8000, verificar DevTools → Application (manifest válido, SW ativo escopo "/") e o ícone "Instalar" na omnibox
**Expected:** Navegador oferece instalação com nome/ícone/cor do sistema
**Why human:** A heurística de instalabilidade e o prompt são comportamento do navegador, não observáveis por CLI

### 2. Página offline
**Test:** Com o SW ativo, derrubar a rede e navegar
**Expected:** Página offline neutra ("Você está offline...") com botão Tentar novamente
**Why human:** Requer SW registrado num navegador real e simulação de rede

### 3. Gaveta mobile e responsividade
**Test:** Estreitar a janela (<768px), abrir/fechar a gaveta pelo hambúrguer; redimensionar de volta
**Expected:** Gaveta cobre o header, overlay fecha ao clicar fora, aside desktop sempre visível (agora 100% CSS)
**Why human:** Comportamento visual/interativo de breakpoint

### 4. Cache Storage após logout
**Test:** Logar, navegar, clicar Sair, abrir DevTools → Application → Cache Storage
**Expected:** Vazio (limparCachePwa rodou antes do POST)
**Why human:** Estado do Cache Storage só é inspecionável no navegador

## Gaps Summary

**No gaps found.** Phase goal achieved. Ready to proceed.

Observações não-bloqueantes:
1. Referência morta a `desktop` em `_nav.html` (ver Anti-Patterns) — recomendação de limpeza de uma linha, não impede o goal.
2. Os fixes pós-review (9fa7d87 CR-01, 9532245 WR-01, 011d4c6 WR-02) foram verificados como o estado final intencional: fallback no-JS real nos forms de login/logout (`method`/`action` + branch `request.htmx`), exclusão de `password`/`last_login` do histórico (migração 0003 aplicada), e aside desktop via CSS `md:!flex`.

## Recommended Fix Plans

None — no critical gaps. A limpeza do `@click` em `_nav.html` pode entrar como tarefa trivial em qualquer plan futura da Fase 3 (que tocará o arquivo de qualquer forma ao adicionar itens de nav).

## Verification Metadata

**Verification approach:** Goal-backward (derived from phase goal)
**Must-haves source:** 02-01..02-04 PLAN.md frontmatter (truths + artifacts + key_links)
**Automated checks:** 57 passed (23 truths + 22 artifacts + 12 wirings), 0 failed; suíte de testes 46/46 OK no container
**Human checks required:** 4 (visuais, não bloqueantes)
**Total verification time:** ~8 min

---
*Verified: 2026-08-18T05:10:00Z*
*Verifier: Claude (subagent)*
