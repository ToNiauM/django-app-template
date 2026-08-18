# Phase 2: Shell Visual e Kernel - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning

<domain>
## Phase Boundary

O app `core` entrega a experiência visual completa e agnóstica de domínio: `base.html`/`shell.html` com navegação lateral e breadcrumbs funcionais, admin site customizado com a identidade visual do sistema (nome e cor primária), PWA instalável (manifest, ícones, service worker) parametrizada pelo nome do sistema, e `django-simple-history` instalado e documentado como padrão de auditoria para modelos de domínio.

Requisitos cobertos: CORE-03, CORE-04, CORE-05, CORE-06.

Fora desta fase: qualquer conteúdo de domínio (CRUD/dashboard chegam na Fase 3 via `apps/exemplo`), parametrização Copier (Fase 4 — aqui os valores são concentrados, não templatizados) e `ops/` (Fase 4).

</domain>

<decisions>
## Implementation Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, ancoradas na PCA — fonte de extração declarada em PROJECT.md — e generalizadas: zero menção a PCA/domínio no código novo.)*

### Shell e navegação (CORE-04)
- **D-09:** Layout do shell segue o padrão da PCA generalizado: `<aside>` lateral fixa no desktop, gaveta controlada por Alpine no mobile, com o empilhamento z-index provado na PCA (header < overlay < aside) para a gaveta cobrir o header ao abrir. Navegação por `<a href>` normal — **sem `hx-boost`** (decisão herdada da PCA; o CSRF via `htmx:configRequest` da Fase 1 permanece intacto).
- **D-10:** A navegação vive num partial editável `core/templates/core/_nav.html`, documentado como **ponto de extensão** onde os apps de domínio registram suas entradas (o `apps/exemplo` da Fase 3 será o exemplo vivo). Sem registry dinâmico/auto-descoberta — partial simples e explícito, como na PCA. Item ativo marcado com `aria-current="page"` + destaque visual comparando `request.path`.
- **D-11:** `shell.html` expõe blocos nomeados para as páginas (`cabecalho_pagina`, `titulo_pagina`, `conteudo_pagina`), espelhando a estrutura de blocos da PCA — é esse contrato que o `apps/exemplo` consumirá na Fase 3.

### Breadcrumbs (CORE-04)
- **D-12:** Contrato D-308 da PCA replicado: partial `core/templates/core/_breadcrumbs.html` que recebe `trilha` — lista de dicts `{"rotulo": str, "url": str|None}` montada **pela view** a partir de dados já no contexto. Último item é sempre a página atual e nunca tem `url` (texto puro); o partial **nunca** faz consulta nem usa templatetag com ORM por trás. Incluído dentro do bloco `cabecalho_pagina` do shell.

### Admin customizado (CORE-03)
- **D-13:** `AdminSite` próprio em **módulo isolado** `core/admin_site.py` que não registra nenhum ModelAdmin, ativado via `AdminConfig.default_site` em `core/apps.py` — `config/urls.py` não muda. O isolamento é obrigatório: a PCA documenta o bug de reentrância do `LazyObject._setup()` quando o site vive no mesmo módulo que faz `admin.site.register` (registros somem silenciosamente).
- **D-14:** Identidade visual do admin via override **cirúrgico** de `core/templates/admin/base_site.html`: só o bloco `extrastyle` recebe um `<style>` com os tokens de cor gerados em `each_context()` a partir dos settings. Nenhum outro aspecto do admin (layout, densidade, tabelas) é tocado. `site_header`/`site_title`/`index_title` derivam do nome do sistema nos settings.
- **D-15:** O agrupamento custom do índice do admin da PCA (`admin_grupo`/`get_app_list`) **não** entra no template — é acoplado ao domínio PCA. O template entrega só identidade visual + registro do `Usuario`.

### Identidade parametrizada (transversal — prepara a Fase 4)
- **D-16:** Identidade concentrada em settings lidos do `.env`: `SISTEMA_NOME` (ex.: "Sistema Base"), `SISTEMA_SIGLA` (short name da PWA) e `COR_PRIMARIA` (hex). São a fonte de runtime para admin, manifest e templates. Um context processor em `core/context_processors.py` expõe a identidade a todos os templates (título, header do shell).
- **D-17:** Tokens de marca do Tailwind (`brand`, `brand-tint`, etc.) definidos em `tailwind.config.js` — segundo touchpoint da cor, resolvido em build. Documentar explicitamente que a Fase 4 parametrizará **exatamente dois pontos** (`.env` + `tailwind.config.js`); nenhum valor de identidade pode aparecer hard-coded em template ou CSS fora desses dois pontos.

### PWA (CORE-05)
- **D-18:** `manifest.json` servido por **view** (`JsonResponse`, content-type `application/manifest+json`) na rota raiz — nunca arquivo estático puro: nome/short name/cores vêm dos settings e as URLs de ícones passam por `{% static %}`/`static()`, mantendo compatibilidade com hashing do WhiteNoise (Pitfall A da PCA).
- **D-19:** `sw.js` hand-rolled servido por view na **raiz do site** (`/sw.js`, nunca `/static/sw.js` — escopo do service worker), sem Workbox. Estratégia mínima da PCA: cacheia apenas `/static/`, pré-cacheia `offline.html` no `install` e usa fallback de navegação offline; HTML e fragmentos HTMX nunca são cacheados.
- **D-20:** Ícones PWA placeholder neutros (sem marca de domínio) em `core/static/img/`, referenciados pelo manifest e documentados como itens de substituição no nascimento de um sistema.

### Auditoria (CORE-06)
- **D-21:** `simple_history` em `INSTALLED_APPS` + `simple_history.middleware.HistoryRequestMiddleware` (depois dos middlewares de auth), como na PCA.
- **D-22:** `Usuario` auditado via `simple_history.register(Usuario)` (a documentação do simple-history exige registro explícito para user model customizado — não declarar `HistoricalRecords` no modelo). Serve de exemplo vivo do padrão.
- **D-23:** Modelos de domínio optam por auditoria declarando `history = HistoricalRecords()` — padrão documentado no `core/README.md` como convenção do template (o `apps/exemplo` da Fase 3 o exercitará).

### Claude's Discretion
- Nomes exatos dos tokens Tailwind e paleta derivada da cor primária (tints/shades).
- Design dos ícones placeholder (podem ser gerados — SVG/PNG simples com a sigla).
- Estratégia de versionamento de cache do service worker (nome de cache, invalidação).
- Estilo visual dos breadcrumbs e microinterações da gaveta mobile.
- Se o `healthz` da PCA entra nesta fase ou fica para a Fase 4 (ops).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fonte de extração (somente leitura — NUNCA modificar)
- `/opt/web/pca/core/admin_site.py` — AdminSite isolado; docstring documenta o bug de reentrância do `LazyObject` que obriga o módulo separado
- `/opt/web/pca/core/apps.py` — `AdminConfig.default_site` apontando para o site custom
- `/opt/web/pca/core/templates/admin/base_site.html` — override cirúrgico do bloco `extrastyle` (D-305 da PCA)
- `/opt/web/pca/core/templates/core/shell.html` — estrutura do shell (aside fixa + gaveta Alpine, empilhamento z-index, blocos de página)
- `/opt/web/pca/core/templates/core/_breadcrumbs.html` — contrato `trilha` (D-308 da PCA)
- `/opt/web/pca/core/templates/core/_nav_visoes.html` — padrão de nav com `aria-current` e item ativo (generalizar; o `hx-swap-oob` é específico do domínio PCA e não entra)
- `/opt/web/pca/core/views.py` — `manifest_view` e `service_worker_view` (pitfalls comentados inline)
- `/opt/web/pca/core/static/offline.html` — página de fallback offline
- `/opt/web/pca/core/tests/test_pwa.py`, `/opt/web/pca/core/tests/test_admin.py` — cobertura de referência para os testes desta fase
- `/opt/web/pca/config/settings/base.py` — posição do `simple_history` em `INSTALLED_APPS` e do `HistoryRequestMiddleware`
- `/opt/web/pca/core/models.py` — docstring do `Usuario` sobre `simple_history.register` para user model customizado

### Documentos do projeto
- `IDEIA.md` — visão, invariantes herdadas da PCA
- `.planning/PROJECT.md` — restrições (stack fechada, zero menção a domínio) e invariantes
- `.planning/REQUIREMENTS.md` — CORE-03, CORE-04, CORE-05, CORE-06
- `.planning/phases/01-funda-o-django/01-CONTEXT.md` — decisões D-01..D-08 da Fase 1 (carregadas adiante)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/templates/base.html` — já carrega Tailwind/HTMX/Alpine e o listener `htmx:configRequest` de CSRF; o shell da Fase 2 estende este base (o `<body>` centrado da tela de login precisará de ajuste de layout para acomodar o shell).
- `core/templates/core/shell.html` — casca mínima da Fase 1 a ser substituída pelo shell completo (o comentário no arquivo já anuncia isso).
- `core/context_processors.py` (`usuario_atual`) — padrão a seguir para o novo context processor de identidade.
- `core/middleware.py` (`HtmxRedirectMiddleware`) — já resolve expiração de sessão em requisições HTMX; nada a mudar.
- `tailwind.config.js` — piso mínimo da Fase 1; o comentário no próprio arquivo já reserva a paleta de marca para esta fase.

### Established Patterns
- Comentários em pt-BR explicando o *porquê* (estilo da casa — manter nos arquivos novos).
- CSRF do HTMX via `htmx:configRequest`, nunca `hx-headers` (invariante).
- Valores parametrizáveis concentrados em settings/`.env` (preparação da Fase 4 — D-16/D-17 reforçam).
- Classes utilitárias semânticas já em uso (`bg-page`, `text-ink`, `bg-surface`) — a paleta de marca deve estender esse vocabulário.

### Integration Points
- `core/urls.py` ganha rotas `manifest.json` e `sw.js` na raiz do app.
- `core/apps.py` ganha o `AdminConfig` custom; `config/settings/base.py` ganha `simple_history` + middleware + settings de identidade; `.env.example` ganha `SISTEMA_NOME`/`SISTEMA_SIGLA`/`COR_PRIMARIA`.
- A Fase 3 (`apps/exemplo`) consumirá: blocos do shell (D-11), contrato `trilha` (D-12), partial `_nav.html` (D-10) e o padrão `HistoricalRecords` (D-23) — esses contratos são a interface pública desta fase.

</code_context>

<specifics>
## Specific Ideas

- Zero menção a "PCA" ou a qualquer domínio no código novo — "Sistema Base" como placeholder que virará variável Copier na Fase 4.
- Critério operacional: usuário logado navega no shell com navegação e breadcrumbs; admin exibe nome e cor do sistema; Chrome/Edge oferece instalação como PWA; `simple_history` documentado e exercitável.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope (modo auto, sem novas capacidades sugeridas).

</deferred>

---

*Phase: 2-Shell Visual e Kernel*
*Context gathered: 2026-08-18*
