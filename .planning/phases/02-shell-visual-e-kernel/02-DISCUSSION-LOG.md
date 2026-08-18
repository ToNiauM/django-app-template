# Phase 2: Shell Visual e Kernel - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-18
**Phase:** 2-Shell Visual e Kernel
**Mode:** `--auto` (todas as opções selecionadas automaticamente com a recomendação ancorada na PCA)
**Areas discussed:** Shell e navegação, Breadcrumbs, Admin customizado, Identidade parametrizada, PWA, Auditoria (simple-history)

---

## Shell e navegação

| Option | Description | Selected |
|--------|-------------|----------|
| Sidebar responsiva (padrão PCA) | Aside fixa desktop + gaveta Alpine mobile, nav em partial `_nav.html` editável | ✓ |
| Topbar horizontal | Navegação no header; diverge do padrão provado da família | |
| Nav dinâmica (registry/auto-descoberta) | Apps registram entradas via código; complexidade sem ganho para o template | |

**Choice:** Sidebar responsiva, partial editável como ponto de extensão, sem `hx-boost`.
**Notes:** Empilhamento z-index (header < overlay < aside) herdado da PCA.

---

## Breadcrumbs

| Option | Description | Selected |
|--------|-------------|----------|
| Contrato `trilha` da PCA (D-308) | View monta lista de dicts `{rotulo, url}`; partial burro, sem ORM | ✓ |
| Templatetag com resolução automática | Breadcrumbs inferidos de URL patterns; mágica difícil de documentar | |

**Choice:** Contrato `trilha` replicado.

---

## Admin customizado

| Option | Description | Selected |
|--------|-------------|----------|
| AdminSite isolado + override `extrastyle` (padrão PCA) | Módulo próprio sem registros (evita bug LazyObject), CSS injetado de `each_context` | ✓ |
| Pacote de tema pronto (django-jazzmin etc.) | Fora da stack fechada | |
| CSS estático em `static/admin/` | Não parametriza cor via settings em runtime | |

**Choice:** Padrão PCA; agrupamento custom do índice (`admin_grupo`) NÃO entra (acoplado ao domínio).

---

## Identidade parametrizada

| Option | Description | Selected |
|--------|-------------|----------|
| Settings/`.env` (runtime) + tailwind.config.js (build) | `SISTEMA_NOME`/`SISTEMA_SIGLA`/`COR_PRIMARIA`; dois touchpoints documentados para a Fase 4 | ✓ |
| Só tailwind.config.js | Admin/manifest não conseguiriam ler a cor em runtime | |
| Tabela de configuração no banco | Sobre-engenharia; identidade é fixa por sistema gerado | |

**Choice:** Dois touchpoints (`.env` + tailwind config), context processor expõe aos templates.

---

## PWA

| Option | Description | Selected |
|--------|-------------|----------|
| Manifest/SW por views na raiz, hand-rolled (padrão PCA) | Parametrizado por settings, `{% static %}` p/ ícones, cache só de `/static/` + offline.html | ✓ |
| Arquivos estáticos puros | Quebra parametrização e hashing do WhiteNoise (Pitfall A) | |
| Workbox/django-pwa | Dependência extra fora da stack; PCA provou que não precisa | |

**Choice:** Padrão PCA; ícones placeholder neutros documentados para substituição.

---

## Auditoria (simple-history)

| Option | Description | Selected |
|--------|-------------|----------|
| Instalar + middleware + `register(Usuario)` + doc do padrão | Usuario via `simple_history.register` (exigência p/ user model custom); domínio opta com `HistoricalRecords()` | ✓ |
| Instalar sem registrar nenhum modelo | Cumpre o mínimo mas perde o exemplo vivo | |
| `HistoricalRecords` direto no `Usuario` | Contraria a documentação do simple-history p/ user model customizado | |

**Choice:** Instalação completa com `Usuario` como exemplo vivo; convenção documentada no `core/README.md`.

---

## Claude's Discretion

- Nomes dos tokens Tailwind e paleta derivada da cor primária
- Design dos ícones placeholder
- Versionamento de cache do service worker
- Estilo visual dos breadcrumbs e da gaveta mobile
- `healthz` nesta fase ou na Fase 4

## Deferred Ideas

None — modo auto, sem novas capacidades sugeridas.
