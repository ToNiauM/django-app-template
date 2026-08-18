# Fase 2: Shell Visual e Kernel - Pesquisa

**Pesquisado em:** 2026-08-18
**Domínio:** Django 5.2 (admin custom, templates/HTMX/Alpine/Tailwind), PWA hand-rolled, django-simple-history
**Confiança:** ALTA — cada padrão desta fase tem contraparte em produção na PCA (`/opt/web/pca`, somente leitura), e as afirmações críticas foram verificadas contra fontes oficiais (PyPI, docs do django-simple-history, código-fonte do Django 5.2)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, ancoradas na PCA — fonte de extração declarada em PROJECT.md — e generalizadas: zero menção a PCA/domínio no código novo.)*

#### Shell e navegação (CORE-04)
- **D-09:** Layout do shell segue o padrão da PCA generalizado: `<aside>` lateral fixa no desktop, gaveta controlada por Alpine no mobile, com o empilhamento z-index provado na PCA (header < overlay < aside) para a gaveta cobrir o header ao abrir. Navegação por `<a href>` normal — **sem `hx-boost`** (decisão herdada da PCA; o CSRF via `htmx:configRequest` da Fase 1 permanece intacto).
- **D-10:** A navegação vive num partial editável `core/templates/core/_nav.html`, documentado como **ponto de extensão** onde os apps de domínio registram suas entradas (o `apps/exemplo` da Fase 3 será o exemplo vivo). Sem registry dinâmico/auto-descoberta — partial simples e explícito, como na PCA. Item ativo marcado com `aria-current="page"` + destaque visual comparando `request.path`.
- **D-11:** `shell.html` expõe blocos nomeados para as páginas (`cabecalho_pagina`, `titulo_pagina`, `conteudo_pagina`), espelhando a estrutura de blocos da PCA — é esse contrato que o `apps/exemplo` consumirá na Fase 3.

#### Breadcrumbs (CORE-04)
- **D-12:** Contrato D-308 da PCA replicado: partial `core/templates/core/_breadcrumbs.html` que recebe `trilha` — lista de dicts `{"rotulo": str, "url": str|None}` montada **pela view** a partir de dados já no contexto. Último item é sempre a página atual e nunca tem `url` (texto puro); o partial **nunca** faz consulta nem usa templatetag com ORM por trás. Incluído dentro do bloco `cabecalho_pagina` do shell.

#### Admin customizado (CORE-03)
- **D-13:** `AdminSite` próprio em **módulo isolado** `core/admin_site.py` que não registra nenhum ModelAdmin, ativado via `AdminConfig.default_site` em `core/apps.py` — `config/urls.py` não muda. O isolamento é obrigatório: a PCA documenta o bug de reentrância do `LazyObject._setup()` quando o site vive no mesmo módulo que faz `admin.site.register` (registros somem silenciosamente).
- **D-14:** Identidade visual do admin via override **cirúrgico** de `core/templates/admin/base_site.html`: só o bloco `extrastyle` recebe um `<style>` com os tokens de cor gerados em `each_context()` a partir dos settings. Nenhum outro aspecto do admin (layout, densidade, tabelas) é tocado. `site_header`/`site_title`/`index_title` derivam do nome do sistema nos settings.
- **D-15:** O agrupamento custom do índice do admin da PCA (`admin_grupo`/`get_app_list`) **não** entra no template — é acoplado ao domínio PCA. O template entrega só identidade visual + registro do `Usuario`.

#### Identidade parametrizada (transversal — prepara a Fase 4)
- **D-16:** Identidade concentrada em settings lidos do `.env`: `SISTEMA_NOME` (ex.: "Sistema Base"), `SISTEMA_SIGLA` (short name da PWA) e `COR_PRIMARIA` (hex). São a fonte de runtime para admin, manifest e templates. Um context processor em `core/context_processors.py` expõe a identidade a todos os templates (título, header do shell).
- **D-17:** Tokens de marca do Tailwind (`brand`, `brand-tint`, etc.) definidos em `tailwind.config.js` — segundo touchpoint da cor, resolvido em build. Documentar explicitamente que a Fase 4 parametrizará **exatamente dois pontos** (`.env` + `tailwind.config.js`); nenhum valor de identidade pode aparecer hard-coded em template ou CSS fora desses dois pontos.

#### PWA (CORE-05)
- **D-18:** `manifest.json` servido por **view** (`JsonResponse`, content-type `application/manifest+json`) na rota raiz — nunca arquivo estático puro: nome/short name/cores vêm dos settings e as URLs de ícones passam por `{% static %}`/`static()`, mantendo compatibilidade com hashing do WhiteNoise (Pitfall A da PCA).
- **D-19:** `sw.js` hand-rolled servido por view na **raiz do site** (`/sw.js`, nunca `/static/sw.js` — escopo do service worker), sem Workbox. Estratégia mínima da PCA: cacheia apenas `/static/`, pré-cacheia `offline.html` no `install` e usa fallback de navegação offline; HTML e fragmentos HTMX nunca são cacheados.
- **D-20:** Ícones PWA placeholder neutros (sem marca de domínio) em `core/static/img/`, referenciados pelo manifest e documentados como itens de substituição no nascimento de um sistema.

#### Auditoria (CORE-06)
- **D-21:** `simple_history` em `INSTALLED_APPS` + `simple_history.middleware.HistoryRequestMiddleware` (depois dos middlewares de auth), como na PCA.
- **D-22:** `Usuario` auditado via `simple_history.register(Usuario)` (a documentação do simple-history exige registro explícito para user model customizado — não declarar `HistoricalRecords` no modelo). Serve de exemplo vivo do padrão.
- **D-23:** Modelos de domínio optam por auditoria declarando `history = HistoricalRecords()` — padrão documentado no `core/README.md` como convenção do template (o `apps/exemplo` da Fase 3 o exercitará).

### Claude's Discretion
- Nomes exatos dos tokens Tailwind e paleta derivada da cor primária (tints/shades).
- Design dos ícones placeholder (podem ser gerados — SVG/PNG simples com a sigla).
- Estratégia de versionamento de cache do service worker (nome de cache, invalidação).
- Estilo visual dos breadcrumbs e microinterações da gaveta mobile.
- Se o `healthz` da PCA entra nesta fase ou fica para a Fase 4 (ops).

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope (modo auto, sem novas capacidades sugeridas).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Descrição | Suporte da pesquisa |
|----|-----------|---------------------|
| CORE-03 | Administrador acessa admin site customizado com a identidade visual do sistema | Padrões 2 e 3 (AdminSite isolado + override cirúrgico); variáveis CSS do admin verificadas no código-fonte do Django 5.2 (`--primary`, `--header-bg`, `--link-fg`); Pitfalls 1 e 2 |
| CORE-04 | Layout base (`base.html`, `shell.html`) com navegação, breadcrumbs, template tags, context processors e middleware do núcleo | Padrões 4, 5 e 6 (shell/gaveta Alpine, `_nav.html`, `_breadcrumbs.html`); Pitfall 6 (tokens Tailwind inexistentes — bug latente da Fase 1), Pitfall 7 (`[x-cloak]`), Pitfall 11 (body centrado da Fase 1) |
| CORE-05 | Sistema funciona como PWA (manifest, ícones, service worker) parametrizado pelo nome do sistema | Padrão 7 (manifest/sw por view, generalizados da PCA); Pitfalls 3, 4 e 5; testes de referência `test_pwa.py`; Pillow 12.1.1 disponível no host para gerar ícones |
| CORE-06 | `django-simple-history` disponível e configurado como padrão de auditoria | Stack (3.13.0 verificado no PyPI, classifiers Django 5.2/6.0); Padrão 8 (`register(Usuario)` — exigência citada da doc oficial); posição do middleware extraída da PCA; Pitfalls 9 e 10 |
</phase_requirements>

## Summary

Esta fase é 90% transplante dirigido: todos os artefatos têm contraparte em produção na PCA e os arquivos canônicos foram lidos integralmente nesta pesquisa. O trabalho real do planner é (1) generalizar sem vazar domínio, (2) integrar com o que a Fase 1 já criou (que diverge da PCA em pontos pequenos mas importantes — nomes de blocos, `INSTALLED_APPS` com `CoreConfig` explícito, `core/admin.py` inexistente) e (3) fechar a estratégia de tokens Tailwind para a cor primária parametrizável.

A única dependência nova, `django-simple-history==3.13.0`, foi verificada: é a versão mais recente no PyPI (publicada 2026-07-22), declara suporte oficial a Django 5.2 e 6.0, e passou no slopcheck (`[OK]`). O padrão `simple_history.register(Usuario)` para user model customizado é exigência documentada oficialmente (não só convenção da PCA). As três variáveis CSS que o admin da PCA sobrescreve (`--primary`, `--header-bg`, `--link-fg`) foram confirmadas no `base.css` do branch stable/5.2.x do Django.

**Descoberta importante desta pesquisa:** os templates da Fase 1 já usam `bg-page`, `bg-surface` e `text-ink`, mas nenhum desses tokens existe no `tailwind.config.js` atual (extend vazio) nem no `input.css` (só as três diretivas `@tailwind`). O JIT do Tailwind ignora classes desconhecidas em silêncio — a tela de login de hoje renderiza sem essas cores e ninguém percebeu porque não há erro de build. Definir a paleta semântica completa é pré-requisito funcional desta fase, não só estético.

**Primary recommendation:** transplantar os padrões da PCA arquivo a arquivo (admin_site, apps, base_site.html, shell, _nav, _breadcrumbs, manifest/sw views, offline.html, testes), generalizando nomes e concentrando identidade em `SISTEMA_NOME`/`SISTEMA_SIGLA`/`COR_PRIMARIA` (`.env`) + um único hex literal em `tailwind.config.js` com tints derivados por função JS no próprio config — exatamente os dois touchpoints da D-17.

## Project Constraints (from CLAUDE.md)

- Fluxo GSD obrigatório para qualquer edição (`/gsd-execute-phase` para trabalho de fase planejado) — nenhuma edição direta fora do workflow.
- Stack/convenções/arquitetura ainda não documentadas no CLAUDE.md — seguir os padrões existentes no código (estabelecidos na Fase 1: comentários pt-BR explicando o porquê, settings via django-environ, CSRF HTMX via `htmx:configRequest`).
- Sem skills de projeto instaladas.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Shell/navegação/breadcrumbs | Frontend Server (templates Django) | Browser (Alpine — gaveta mobile) | Renderização server-side; Alpine só controla estado visual local (D-09) |
| Trilha (`trilha`) | Frontend Server (views) | — | Montada pela view com dados já no contexto; partial nunca consulta (D-12) |
| Identidade visual runtime | Frontend Server (settings + context processor) | — | `.env` → settings → context processor → templates/admin/manifest (D-16) |
| Tokens de cor Tailwind | CDN/Static (build multi-stage) | — | Resolvidos em build no estágio node do Dockerfile; segundo touchpoint (D-17) |
| Admin customizado | Frontend Server (AdminSite + template override) | — | `each_context` injeta CSS; template override no bloco `extrastyle` (D-13/D-14) |
| Manifest PWA | API/Backend (view `JsonResponse`) | — | Precisa de `static()` resolvido em runtime — nunca arquivo estático (D-18) |
| Service worker | API/Backend (view na raiz) + Browser (execução) | CDN/Static (o que ele cacheia) | Servido por view por causa do escopo `/`; só cacheia `/static/` (D-19) |
| Auditoria de modelos | Database/Storage (tabelas `Historical*`) | Frontend Server (middleware captura o usuário) | `simple_history` cria tabelas paralelas; `HistoryRequestMiddleware` liga request→history_user (D-21/D-22) |

## Standard Stack

### Core (nenhuma mudança além de uma dependência nova)

| Biblioteca | Versão | Propósito | Por quê |
|------------|--------|-----------|---------|
| django-simple-history | 3.13.0 | Auditoria de modelos (tabelas históricas + rastreio de usuário) | Mesma versão pinada na PCA em produção; é a mais recente no PyPI (2026-07-22) com classifiers `Framework :: Django :: 5.2` e `:: 6.0`, `requires_python >=3.10` [VERIFIED: PyPI + slopcheck OK] |

Todo o resto já está no `requirements.txt` da Fase 1 (Django 5.2.17, WhiteNoise 6.12.0, django-htmx 1.29.0 etc.) — **stack fechada, nenhuma outra dependência entra** (restrição do PROJECT.md). Tailwind 3.4.17 já é o pino do estágio `assets` do Dockerfile da Fase 1 (funcionando — build validado em produção local).

### Alternatives Considered

| Em vez de | Poderia usar | Tradeoff |
|-----------|-------------|----------|
| sw.js hand-rolled | Workbox | Vetado por D-19 (locked); Workbox adiciona toolchain JS e generic caching que conflita com "nunca cachear HTML/HTMX" |
| simple-history | django-auditlog / triggers SQL | Vetado pela stack fechada; simple-history dá modelo consultável + admin + integração com user, provado na PCA |
| Hex literal no tailwind.config.js | CSS vars em `input.css` (padrão PCA) | CSS vars existem na PCA para servir o dark mode; sem dark mode nesta fase, vars criariam um TERCEIRO touchpoint de identidade, violando D-17 |

**Instalação:**
```bash
# requirements.txt ganha a linha (e rebuild da imagem web):
django-simple-history==3.13.0
```

**Verificação de versão executada nesta pesquisa:**
```
pip index versions django-simple-history  →  3.13.0 (mais recente)
PyPI JSON: requires_python >=3.10; classifiers Django 5.2, Django 6.0; upload 2026-07-22
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| django-simple-history | PyPI | ~12 anos (1.2.0 em 2013; 52 releases) | projeto maduro, mantido pelo jazzband | github.com/jazzband/django-simple-history | [OK] | Aprovado |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

O slopcheck rodou no host (`slopcheck install django-simple-history` → `[OK]`, 1 pacote escaneado). A instalação real acontece dentro do build Docker via `requirements.txt` com versão pinada.

## Architecture Patterns

### System Architecture Diagram

```
                        ┌─────────────────────────────────────────────┐
 .env ──► settings ─────┤ SISTEMA_NOME / SISTEMA_SIGLA / COR_PRIMARIA │ (touchpoint 1 — runtime)
                        └───────┬──────────────┬──────────────┬───────┘
                                │              │              │
                     context processor    AdminSite       manifest_view
                     (identidade em       each_context    (JsonResponse,
                      todo template)      (admin_tema_css) ícones via static())
                                │              │              │
Browser ── GET / ──► shell_view ──► shell.html ─┤              │
   │                    │            ├ _nav.html (aria-current, ponto de extensão)
   │                    │ trilha     ├ _breadcrumbs.html (contrato `trilha`)
   │                    └──────────► └ blocos: cabecalho_pagina/titulo_pagina/conteudo_pagina
   │
   ├─ GET /admin/ ──► SistemaAdminSite (core/admin_site.py, módulo isolado)
   │                    └ core/templates/admin/base_site.html (só extrastyle)
   │
   ├─ GET /manifest.json ──► manifest_view (@login_not_required)
   ├─ GET /sw.js ──► service_worker_view (@login_not_required, Service-Worker-Allowed: /)
   │                    └ SW no browser: cacheia só /static/, precacheia offline.html,
   │                      fallback de navegação offline; HTML/HTMX nunca
   │
   └─ POST (qualquer escrita) ──► HistoryRequestMiddleware ──► HistoricalUsuario /
                                  (request.user → history_user)  Historical<Modelo> (Postgres)

tailwind.config.js (touchpoint 2 — build): 1 hex literal → brand/brand-hover/
brand-ink/brand-tint derivados por função JS → estágio node do Dockerfile → dist/tailwind.css
```

### Recommended Project Structure (arquivos novos/alterados desta fase)

```
core/
├── admin.py                    # NOVO — simple_history.register(Usuario) + UsuarioAdmin (e-mail, sem username)
├── admin_site.py               # NOVO — SistemaAdminSite isolado (nenhum register aqui)
├── apps.py                     # ALTERADO — ganha AdminConfig custom (default_site)
├── context_processors.py       # ALTERADO — ganha identidade (SISTEMA_NOME/SIGLA/COR_PRIMARIA)
├── urls.py                     # ALTERADO — rotas manifest.json e sw.js
├── views.py                    # ALTERADO — manifest_view, service_worker_view, trilha no shell_view
├── README.md                   # NOVO — convenção de auditoria (D-23) e pontos de extensão
├── migrations/0002_*.py        # NOVO — HistoricalUsuario (makemigrations após register)
├── static/
│   ├── src/input.css           # ALTERADO — regra [x-cloak]
│   ├── offline.html            # NOVO — fallback offline autocontido (cores neutras)
│   └── img/icon-{192,512,512-maskable}.png   # NOVO — placeholders gerados
├── templates/
│   ├── base.html               # ALTERADO — manifest link, theme-color, registro do SW, body sem centering
│   ├── admin/base_site.html    # NOVO — override cirúrgico do bloco extrastyle
│   └── core/
│       ├── shell.html          # REESCRITO — aside + gaveta + blocos de página
│       ├── _nav.html           # NOVO — ponto de extensão de navegação
│       ├── _breadcrumbs.html   # NOVO — contrato trilha
│       └── login.html          # ALTERADO — centering movido do body para o wrapper
├── tests/
│   ├── test_pwa.py             # NOVO
│   ├── test_admin.py           # NOVO
│   ├── test_shell.py           # NOVO (nav/breadcrumbs/blocos)
│   └── test_auditoria.py       # NOVO (HistoricalUsuario + history_user via middleware)
config/settings/base.py         # ALTERADO — simple_history, middleware, identidade, ctx processor
tailwind.config.js              # ALTERADO — paleta semântica + tokens de marca derivados
.env.example                    # ALTERADO — SISTEMA_NOME/SISTEMA_SIGLA/COR_PRIMARIA
ops/gerar_icones_pwa.py         # NOVO (opcional, roda no host com Pillow) — ver Open Questions
```

### Pattern 1: Estratégia de tokens Tailwind para cor primária parametrizável (fecha a pergunta da pesquisa)

**O quê:** um único hex literal em `tailwind.config.js`; tints/shades derivados por funções JS no próprio config (o config é JS — pode computar). Sem CSS custom properties, sem dark mode nesta fase.

**Por quê:** (a) D-17 exige exatamente dois touchpoints — `.env` e `tailwind.config.js`; CSS vars em `input.css` (padrão PCA) criariam um terceiro; (b) a PCA só precisa de vars por causa do dark mode, que não é requisito desta fase; (c) com um único literal, a Fase 4 (Copier) substitui um valor só, sem precisar de matemática de cor em Jinja.

```javascript
// tailwind.config.js — Fonte: adaptação do padrão PCA (/opt/web/pca/tailwind.config.js),
// simplificado: sem var(--cor-*) porque não há dark mode nesta fase (D-17).
/** ÚNICO valor de identidade deste arquivo — a Fase 4 (Copier) parametriza
 *  exatamente esta linha + o .env (D-17). */
const COR_PRIMARIA = "#1e40af";

// Derivações em JS puro (sem dependência): mistura o hex com branco/preto.
function misturar(hex, alvo, fator) {
  const n = parseInt(hex.slice(1), 16);
  const canal = (desloc) => {
    const c = (n >> desloc) & 0xff;
    return Math.round(c + (alvo - c) * fator);
  };
  return "#" + [16, 8, 0].map((d) => canal(d).toString(16).padStart(2, "0")).join("");
}

module.exports = {
  content: ["./core/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        // Paleta semântica neutra (NÃO é identidade — fixa do template).
        // Os templates da Fase 1 JÁ usam bg-page/bg-surface/text-ink sem
        // que existam — o JIT os ignora em silêncio (Pitfall 6).
        page: "#f9f9f7",
        surface: "#fcfcfb",
        "surface-2": "#f3f2ef",
        ink: "#0b0b0b",
        "ink-2": "#52514e",
        muted: "#77756f",
        grid: "#e4e2dd",
        // Marca — todos derivados do único literal acima.
        brand: COR_PRIMARIA,
        "brand-hover": misturar(COR_PRIMARIA, 255, 0.12), // clareado 12%
        "brand-ink": misturar(COR_PRIMARIA, 0, 0.18),     // escurecido 18% (pressed)
        "brand-tint": misturar(COR_PRIMARIA, 255, 0.9),   // fundo tênue (item de nav ativo)
      },
    },
  },
  plugins: [],
};
```

Valores neutros (page/surface/ink/muted/grid) copiados da paleta clara validada da PCA (`input.css` linhas 121–136) — são neutros de template, não identidade, portanto podem ser literais fora dos dois touchpoints. Nomes exatos e fatores de derivação são discretion — os acima são a recomendação.

### Pattern 2: AdminSite isolado + AdminConfig (D-13)

**O quê:** `core/admin_site.py` contém APENAS a subclasse de `AdminSite` (zero `admin.site.register`); `core/apps.py` ganha uma subclasse de `AdminConfig` com `default_site`; em `INSTALLED_APPS`, a entrada `"django.contrib.admin"` é **substituída** pela config custom.

```python
# core/apps.py — Fonte: /opt/web/pca/core/apps.py (generalizado)
import django.contrib.admin.apps as _django_admin_apps  # nunca `from ... import AdminConfig`
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"


class SistemaAdminConfig(_django_admin_apps.AdminConfig):
    # Não redeclara `name` — herda "django.contrib.admin", obrigatório para o
    # Django reconhecer esta subclasse como a config do app admin.
    default_site = "core.admin_site.SistemaAdminSite"
    default = False
```

```python
# core/admin_site.py — Fonte: /opt/web/pca/core/admin_site.py (generalizado, sem get_app_list — D-15)
from django.conf import settings
from django.contrib import admin


class SistemaAdminSite(admin.AdminSite):
    def __init__(self, name="admin"):
        super().__init__(name)
        self.site_header = f"{settings.SISTEMA_NOME} — Administração"
        self.site_title = settings.SISTEMA_SIGLA
        self.index_title = "Painel do administrador"

    def each_context(self, request):
        contexto = super().each_context(request)
        cor = settings.COR_PRIMARIA
        # Os 3 tokens confirmados no base.css do Django 5.2 (stable/5.2.x):
        # --primary, --header-bg, --link-fg.
        contexto["admin_tema_css"] = (
            f":root {{ --primary: {cor}; --header-bg: {cor}; --link-fg: {cor}; }}"
        )
        return contexto
```

Mudança em `INSTALLED_APPS` (config/settings/base.py): trocar a linha `"django.contrib.admin"` por `"core.apps.SistemaAdminConfig"` (uma entrada só — duas geram `Application labels aren't unique: admin`).

**Nuance vs. PCA:** o sistema_base lista `"core.apps.CoreConfig"` explícito (a PCA usa `"core"` plain). Isso já evita o autodiscovery ambíguo, mas as duas salvaguardas (`import ... as _django_admin_apps` + `default = False`) devem ser mantidas mesmo assim — custam duas linhas e blindam contra regressão quando a Fase 4 mexer nos settings.

**Gate de acesso:** a PCA sobrescreve `has_permission` para exigir superuser (D-126 da PCA — política de domínio). As decisões D-13/D-14/D-15 desta fase NÃO travam isso. Recomendação: **não sobrescrever** `has_permission` — manter o padrão do Django (`is_active and is_staff`); um template genérico não deve mudar semântica de acesso silenciosamente. Ver Assumptions A1.

### Pattern 3: Override cirúrgico do template do admin (D-14)

```html
{# core/templates/admin/base_site.html — Fonte: /opt/web/pca/core/templates/admin/base_site.html #}
{% extends "admin/base_site.html" %}
{% block extrastyle %}
{{ block.super }}
<style>{{ admin_tema_css|safe }}</style>
{% endblock %}
```

Funciona apesar de estender o próprio nome: o `{% extends %}` do Django pula origens já usadas (extends recursivo, suportado desde o Django 1.9) — o loader `DIRS` (que aponta para `core/templates`) encontra este arquivo primeiro e o extends resolve para a versão do `django.contrib.admin` na sequência. Provado em produção na PCA. O arquivo DEVE se chamar exatamente `admin/base_site.html` e viver sob `core/templates/`.

### Pattern 4: Shell com aside fixa + gaveta Alpine (D-09/D-11)

Estrutura extraída de `/opt/web/pca/core/templates/core/shell.html` (lido integralmente), generalizando e REMOVENDO o que é domínio PCA (busca F7, tema claro/escuro, `hx-swap-oob` da nav, exercício):

- Raiz `x-data="{ desktop: window.matchMedia('(min-width: 768px)').matches, sidebarAberta: false }"` com `x-init` registrando listener de `change` do MediaQueryList — **obrigatório**: `x-show` só reavalia com dependência reativa; ler `window.matchMedia` direto congela a gaveta no breakpoint do load (comentário da PCA documenta o bug real).
- Empilhamento: header mobile `z-30` < overlay `z-40` < aside `z-50` (aside `fixed inset-y-0 left-0 w-[232px]`; gaveta aberta cobre o header — o botão de fechar dela substitui o hambúrguer).
- Overlay: `x-show="sidebarAberta && !desktop" x-cloak @click="sidebarAberta = false"`, `fixed inset-0 bg-black/40 md:hidden`.
- Aside: `x-show="sidebarAberta || desktop" x-cloak`.
- `<main class="flex-1 md:ml-[232px] px-6 pb-6 pt-20 md:py-6 min-w-0">` com os blocos `{% block cabecalho_pagina %}` (contendo `{% include "core/_breadcrumbs.html" with trilha=trilha %}` + `<h1>{% block titulo_pagina %}`) e `{% block conteudo_pagina %}`.
- Rodapé da aside: avatar com iniciais do e-mail (`usuario_atual.email|slice:":2"|upper`), e-mail truncado, botão Sair (`hx-post` para `core:logout` + `hx-on::before-request="limparCachePwa()"` — limpeza do Cache Storage ANTES do POST de logout).
- Identidade no topo da aside: `{{ sistema_nome }}` / `{{ sistema_sigla }}` do context processor (sem logo de domínio).

### Pattern 5: `_nav.html` como ponto de extensão (D-10)

Generalização de `/opt/web/pca/core/templates/core/_nav_visoes.html` SEM `hx-swap-oob` (específico do fluxo de filtros da PCA) e SEM querystring:

```html
{# core/templates/core/_nav.html — ponto de extensão: apps de domínio adicionam <a> aqui #}
{% url 'core:shell' as url_inicio %}
<nav aria-label="Navegação principal" class="flex flex-col gap-1">
  <a href="{{ url_inicio }}"
     @click="if (!desktop) sidebarAberta = false"
     {% if request.path == url_inicio %}aria-current="page"{% endif %}
     class="relative flex items-center gap-3 rounded px-3 py-2 font-semibold
            {% if request.path == url_inicio %}bg-brand-tint text-brand-ink{% else %}text-ink-2 hover:bg-surface-2{% endif %}">
    {% if request.path == url_inicio %}<span class="absolute inset-y-0 left-0 w-[2px] bg-brand" aria-hidden="true"></span>{% endif %}
    <span>Início</span>
  </a>
</nav>
```

O `@click` que fecha a gaveta no mobile depende do `x-data` do shell (o partial é incluído dentro dele). Comentário no arquivo deve documentar o contrato de item (classes ativo/inativo, `aria-current`, fechamento da gaveta) para o `apps/exemplo` da Fase 3 copiar.

### Pattern 6: `_breadcrumbs.html` — contrato `trilha` (D-12)

Transplante quase verbatim de `/opt/web/pca/core/templates/core/_breadcrumbs.html` (o partial já é 100% agnóstico de domínio — só o comentário precisa trocar os exemplos). Contrato: lista de dicts `{"rotulo", "url"}`, último item sem `url` vira `<span aria-current="page">`, separador `/` com `aria-hidden`, tipografia `text-xs font-medium uppercase text-ink-2`. `shell_view` passa `trilha = [{"rotulo": "Início", "url": None}]` como exemplo vivo.

### Pattern 7: PWA por views (D-18/D-19/D-20)

`manifest_view` e `service_worker_view` generalizados de `/opt/web/pca/core/views.py` (lidos integralmente — os pitfalls estão comentados inline lá). Pontos que mudam na generalização:

- `name`/`short_name` ← `settings.SISTEMA_NOME`/`settings.SISTEMA_SIGLA`; `theme_color` ← `settings.COR_PRIMARIA`; `background_color` ← literal `#f9f9f7` (mesmo hex do token `page` — neutro de template, não identidade; comentar a correspondência).
- Ambas as views com `@login_not_required` (Django 5.1+ `LoginRequiredMiddleware` bloqueia tudo por padrão — sem o decorator o browser recebe 302 e a PWA não instala).
- Rotas em `core/urls.py`: `path("manifest.json", ...)` e `path("sw.js", ...)` — como `core.urls` é incluído na raiz, ficam em `/manifest.json` e `/sw.js` (escopo `/` garantido).
- SW: cache name recomendado `"static-v1"` (discretion resolvida: nome fixo neutro — Cache Storage é escopado por origem, não há colisão entre sistemas; bump manual do sufixo documentado em comentário).
- `base.html` ganha: `<link rel="manifest" href="{% url 'core:manifest' %}">`, `<meta name="theme-color" content="{{ cor_primaria }}">`, script de registro `navigator.serviceWorker.register("{% url 'core:service_worker' %}", { scope: "/" })` e a função global `limparCachePwa()` (apaga Cache Storage + `htmx-history-cache` do localStorage) chamada pelo botão Sair. Adicionar também `hx-history="false"` no `<body>` (defesa contra snapshot de HTML autenticado no localStorage — presente na PCA).
- `offline.html` em `core/static/` (não em templates — precisa ser precacheável como estático): autocontido, zero rede, **cores neutras** (o botão azul `#003c71` da PCA violaria D-17 — usar cinza-escuro neutro).
- Ícones: 3 PNGs (192, 512, 512-maskable). Discretion resolvida: gerar no host com Pillow 12.1.1 (disponível — verificado; o container NÃO tem Pillow, igual à PCA) — quadrado chapado na cor primária com a sigla centrada em branco; maskable com padding de 20% (safe zone). Script `ops/gerar_icones_pwa.py` commitado junto dos PNGs e documentado como item de substituição no nascimento de um sistema (D-20).

### Pattern 8: simple-history (D-21/D-22/D-23)

- `INSTALLED_APPS`: `"simple_history"` (posição na PCA: depois de `django_htmx`, antes de `axes` — qualquer posição após os apps contrib funciona, espelhar a PCA).
- `MIDDLEWARE`: `"simple_history.middleware.HistoryRequestMiddleware"` imediatamente após `AuthenticationMiddleware` e antes de `HtmxMiddleware` (ordem exata da PCA; a doc oficial só exige "depois do auth" [CITED: django-simple-history quick_start]).
- `core/admin.py` (arquivo novo — não existe na Fase 1): no topo, `simple_history.register(Usuario)`; depois `UsuarioAdmin(UserAdmin)` adaptado para e-mail (sem username): `ordering = ("email",)`, `list_display` com email/nomes/flags, e os `fieldsets`/`add_fieldsets` reescritos sem `username` (obrigatório — o `UserAdmin` padrão referencia `username` e quebraria com o model da Fase 1).
- Depois do register: `makemigrations core` gera a migração de `HistoricalUsuario` (0002). Rodar dentro do container.
- `core/README.md` documenta a convenção D-23: modelos de domínio declaram `history = HistoricalRecords()`; o user model é exceção via `register()`; alertar que `queryset.update()` NÃO gera histórico (usar `bulk_update_with_history`).

### Anti-Patterns to Avoid

- **`AdminSite` no mesmo módulo que registra ModelAdmin:** reentrância do `LazyObject._setup()` apaga registros em silêncio (docstring completa em `/opt/web/pca/core/admin_site.py`) — D-13 existe por causa disso.
- **manifest.json como arquivo estático:** o hashing do `CompressedManifestStaticFilesStorage` renomeia os ícones no `collectstatic`; um JSON estático com caminhos literais 404aria em produção (Pitfall A da PCA).
- **`sw.js` sob `/static/`:** escopo do service worker fica limitado a `/static/` — a PWA não instala ("erro nº 1" documentado na PCA).
- **Cachear HTML/fragmentos HTMX no SW:** conteúdo autenticado ficaria no Cache Storage após logout; a estratégia só toca GET same-origin sob `/static/` + fallback de navegação.
- **`hx-boost` na navegação:** vetado por D-09; quebraria a premissa de "componente Alpine montado uma vez por página" do shell.
- **`HistoricalRecords()` direto no `Usuario`:** não funciona em user model swappable — a FK de `history_user` cria dependência circular [CITED: doc oficial, ver Pattern 8 / Sources].
- **Templatetag de breadcrumbs com ORM por trás:** vetado por D-12 — a trilha vem pronta da view.
- **Valores de identidade fora dos dois touchpoints:** nenhum hex da cor primária nem nome do sistema literal em template/CSS (D-16/D-17) — inclusive no `offline.html` e nos ícones commitados (os PNGs são regeneráveis pelo script, que lê... ver Assumptions A2).

## Don't Hand-Roll

| Problema | Não construir | Usar | Por quê |
|----------|---------------|------|---------|
| Auditoria de modelos | Tabelas de log manuais / triggers | django-simple-history 3.13.0 | Migrações automáticas, `history_user`, admin integrado, `bulk_update_with_history` — tudo provado na PCA |
| Tema do admin | Fork de templates do admin | 3 CSS vars nativas (`--primary`, `--header-bg`, `--link-fg`) via `extrastyle` | Variáveis confirmadas no base.css do Django 5.2; sobrevivem a upgrades do Django |
| Substituição do `admin.site` | Mexer em `config/urls.py` / monkeypatch | `AdminConfig.default_site` | Mecanismo oficial; urls.py intocado (D-13) |
| Detecção de breakpoint no Alpine | Ler `window.innerWidth` em expressões | `matchMedia` + listener de `change` alimentando estado reativo | `x-show` não reavalia sem dependência reativa (bug real documentado na PCA) |
| Serviço de estáticos | Cabeçalhos/hashing manuais | WhiteNoise (já configurado na Fase 1) | O manifest/sw só precisam respeitá-lo via `static()` |

**Exceção deliberada (locked):** o service worker É hand-rolled (D-19) — a estratégia mínima de ~50 linhas da PCA é auditável e o Workbox traria toolchain e caching genérico indesejado.

## Common Pitfalls

### Pitfall 1: Reentrância do `LazyObject` apaga registros do admin
**O que acontece:** `Usuario`/`Group` somem do admin sem erro algum.
**Por quê:** `admin.site` é resolvido preguiçosamente; se o módulo do `AdminSite` custom também registra ModelAdmins, o import reentrante durante `_setup()` instancia sites duplicados e o último sobrescreve `_wrapped` com `_registry` vazio.
**Como evitar:** D-13 — `core/admin_site.py` sem nenhum `register`; registros só em `core/admin.py`.
**Sinal de alerta:** admin index vazio ou faltando modelos, sem traceback.

### Pitfall 2: Duas entradas do app admin em `INSTALLED_APPS`
**O que acontece:** `ImproperlyConfigured: Application labels aren't unique, duplicates: admin`.
**Como evitar:** `"core.apps.SistemaAdminConfig"` SUBSTITUI `"django.contrib.admin"` (não coexiste). Manter `default = False` e o import aliased em `core/apps.py` (Pattern 2).

### Pitfall 3: Manifest com caminhos de ícone estáticos literais
**O que acontece:** ícones 404 só em produção (após `collectstatic` com hashing do WhiteNoise); dev funciona e mascara o bug.
**Como evitar:** D-18 — view com `static()`. O teste compara `corpo["icons"][*]["src"]` com `static(...)` resolvido (test_pwa.py da PCA).

### Pitfall 4: Escopo do service worker
**O que acontece:** SW registra mas não controla `/` — Chrome/Edge não oferecem instalação.
**Como evitar:** D-19 — rota `/sw.js` na raiz + header `Service-Worker-Allowed: /` + `register(..., { scope: "/" })`.

### Pitfall 5: `LoginRequiredMiddleware` bloqueia manifest/sw
**O que acontece:** GET `/manifest.json` devolve 302 para `/login/`; instalação e registro do SW falham silenciosamente.
**Por quê:** Django 5.1+ com `LoginRequiredMiddleware` (já ativo desde a Fase 1) exige `@login_not_required` explícito em rotas públicas.
**Como evitar:** decorator nas duas views (a PCA faz exatamente isso). `offline.html` não é afetado — o `WhiteNoiseMiddleware` responde antes do auth na pilha.

### Pitfall 6: Tokens Tailwind inexistentes são ignorados em silêncio (bug latente da Fase 1)
**O que acontece:** `bg-page`, `bg-surface`, `text-ink` já estão nos templates da Fase 1, mas não existem no config atual — o JIT simplesmente não emite as classes; a página renderiza com fundo branco default e o guard de bytes do Dockerfile não pega (o CSS passa de 5000 bytes com as demais classes).
**Como evitar:** definir a paleta semântica completa (Pattern 1) NESTA fase.
**Verificação:** após o build, `grep -c "bg-page\|bg-brand" core/static/dist/tailwind.css` (ou inspecionar o CSS no container) deve encontrar as classes.

### Pitfall 7: `[x-cloak]` sem regra CSS é inerte
**O que acontece:** flash da gaveta/overlay abertos no primeiro paint (antes do Alpine iniciar).
**Por quê:** `x-cloak` é só um atributo; a regra `[x-cloak] { display: none !important; }` precisa existir no CSS — e não é classe utilitária, então precisa ser escrita à mão no `input.css` (a PCA descobriu isso tarde — linha 338 do input.css dela).
**Como evitar:** adicionar a regra ao `core/static/src/input.css` junto com esta fase (primeiro uso de `x-cloak` no projeto).

### Pitfall 8: `x-show` congelado no breakpoint do load
**O que acontece:** girar o aparelho/redimensionar deixa gaveta e overlay no estado errado.
**Como evitar:** estado `desktop` reativo alimentado por listener de `change` do `MediaQueryList` (Pattern 4 — comentário da PCA documenta o bug de produção).

### Pitfall 9: `queryset.update()` não gera histórico
**O que acontece:** alterações em massa invisíveis na auditoria.
**Como evitar:** documentar no `core/README.md` (D-23): usar `bulk_update_with_history` (exemplo real em `/opt/web/pca/core/admin.py`). Se o `UsuarioAdmin` do template incluir ações em massa, elas DEVEM usar esse utilitário — recomendação: não incluir ações em massa nesta fase (D-15 pede admin mínimo).

### Pitfall 10: Esquecer a migração do `HistoricalUsuario`
**O que acontece:** `simple_history.register(Usuario)` sem `makemigrations` → `ProgrammingError` (tabela `core_historicalusuario` inexistente) no primeiro save.
**Como evitar:** tarefa explícita de `makemigrations core` + `migrate` no container após o register; teste que salva um `Usuario` e verifica `Usuario.history.count()`.

### Pitfall 11: `<body>` centrado da Fase 1 quebra o shell
**O que acontece:** o `base.html` atual tem `flex flex-col items-center justify-center` no `<body>` (feito para o card de login) — o shell com aside fixa ficaria espremido no centro.
**Como evitar:** mover o centering do body para um wrapper em `login.html`; o body fica `min-h-screen bg-page text-ink font-sans text-base`. O CONTEXT.md já anuncia este ajuste.

### Pitfall 12: Renomear o override do admin ou movê-lo de lugar
**O que acontece:** `TemplateDoesNotExist` ou recursão infinita se o extends recursivo não resolver na ordem certa.
**Como evitar:** exatamente `core/templates/admin/base_site.html` estendendo `"admin/base_site.html"` — a ordem loader `DIRS` (core/templates) → `APP_DIRS` (contrib.admin) faz o extends recursivo funcionar (Pattern 3).

## Code Examples

Além dos patterns acima, os arquivos canônicos a transplantar (todos lidos nesta pesquisa):

| Artefato desta fase | Fonte canônica (somente leitura) | O que muda na generalização |
|---------------------|----------------------------------|------------------------------|
| `core/admin_site.py` | `/opt/web/pca/core/admin_site.py` | Remove `ORDEM_GRUPOS_ADMIN`/`get_app_list`/`_slug_ascii` (D-15); identidade via settings; sem `has_permission` custom (A1) |
| `core/apps.py` | `/opt/web/pca/core/apps.py` | Renomeia `PcaAdminConfig` → `SistemaAdminConfig`; docstrings generalizadas |
| `core/templates/admin/base_site.html` | idem PCA | Verbatim (já agnóstico) |
| `core/templates/core/shell.html` | `/opt/web/pca/core/templates/core/shell.html` | Remove F7/tema/exercício/logo CFC; mantém x-data desktop+sidebar, z-30/40/50, blocos de página, rodapé com usuário+Sair |
| `core/templates/core/_breadcrumbs.html` | `/opt/web/pca/core/templates/core/_breadcrumbs.html` | Verbatim menos exemplos do comentário |
| `core/templates/core/_nav.html` | `/opt/web/pca/core/templates/core/_nav_visoes.html` | Remove `hx-swap-oob` e querystring; 1 item "Início" + comentário de extensão |
| `manifest_view` / `service_worker_view` | `/opt/web/pca/core/views.py` | Identidade via settings; cache name neutro; `OFFLINE_URL` via `static("offline.html")` igual |
| `core/static/offline.html` | `/opt/web/pca/core/static/offline.html` | Título/cores neutros (botão sem hex de marca — D-17) |
| `core/tests/test_pwa.py` | `/opt/web/pca/core/tests/test_pwa.py` | Asserts de nome vêm de `settings.SISTEMA_NOME`; truque IHDR (struct, sem Pillow) mantido |
| `core/tests/test_admin.py` | `/opt/web/pca/core/tests/test_admin.py` | Só os testes de identidade/registro (sem grupos/ações — D-15); manter `@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)` |
| settings (simple_history) | `/opt/web/pca/config/settings/base.py` | Mesmas posições em `INSTALLED_APPS` e `MIDDLEWARE` |
| `simple_history.register(Usuario)` | `/opt/web/pca/core/admin.py` topo | Verbatim; `UsuarioAdmin` sem `admin_grupo` e sem ações em massa |

Registro do user model (exigência oficial, não só padrão da casa):

```python
# core/admin.py — Fonte: doc oficial (common_issues, "Tracking Custom Users") +
# /opt/web/pca/core/admin.py
import simple_history
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import Usuario

# User model swappable NÃO pode declarar HistoricalRecords no próprio modelo —
# a FK de history_user cria dependência circular. register() é a forma oficial.
simple_history.register(Usuario)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "last_login")
    search_fields = ("email", "first_name", "last_name")
    # fieldsets/add_fieldsets precisam ser redeclarados sem "username" —
    # o UserAdmin padrão referencia o campo que o Usuario da Fase 1 não tem.
```

## State of the Art

| Abordagem antiga | Abordagem atual | Quando mudou | Impacto |
|------------------|-----------------|--------------|---------|
| `STATICFILES_STORAGE` string | dict `STORAGES` | Django 5.1 removeu a antiga | Fase 1 já usa `STORAGES` — nada a fazer |
| Rotas públicas por omissão | `LoginRequiredMiddleware` global + `@login_not_required` | Django 5.1 | manifest/sw/healthz precisam do decorator (Pitfall 5) |
| Tema do admin via fork de CSS | CSS custom properties nativas | Django 4.x+ (confirmadas em 5.2) | Override de 1 linha no `extrastyle` |
| simple-history 3.x série | 3.13.0 (jul/2026) suporta Django 5.2 e 6.0 | 2026-07-22 | Pino idêntico ao da PCA é também o mais atual — sem dívida |
| Tailwind 3.x (projeto) | Tailwind 4.x existe, mas o projeto pina 3.4.17 | — | Stack fechada: NÃO migrar; a sintaxe de config JS desta pesquisa é a do 3.4 |

**Deprecated/outdated:** nada relevante ao escopo — todas as APIs usadas (AdminSite.each_context, AdminConfig.default_site, HistoryRequestMiddleware, JsonResponse) estão estáveis no Django 5.2.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | O admin do template mantém o `has_permission` padrão do Django (`is_staff`), sem o gate superuser da PCA (D-126 é política de domínio, não travada em D-13..D-15) | Pattern 2 | Baixo — inverter depois é 4 linhas + 1 teste; mas muda quem acessa `/admin/` no sistema gerado [ASSUMED] |
| A2 | Os PNGs de ícone são commitados como binários gerados uma vez pelo script do host (que embute a cor/sigla no momento da geração); a regeneração no nascimento de um sistema é passo documentado, não automático — os bytes do PNG não contam como "hard-code de identidade" para D-17 | Pattern 7 | Baixo — se a Fase 4 exigir regeneração automática, o script já existe [ASSUMED] |
| A3 | `background_color` do manifest e as cores do `offline.html` são "neutros de template" (como page/surface), fora da regra dos dois touchpoints de D-16/D-17 que cobre identidade (nome/sigla/cor primária) | Pattern 7 | Baixo — trocar literais depois é trivial [ASSUMED] |
| A4 | Dark mode/controle de tema da PCA fica fora desta fase (não aparece em CORE-03..06 nem nas decisões D-09..D-23) | Pattern 1 | Médio se o usuário esperava tema escuro — reintroduzir depois exige voltar a CSS vars (mudança na estratégia de tokens) [ASSUMED] |
| A5 | Nomes de blocos da Fase 1 (`titulo`, `content`, `scripts` no base.html) são mantidos; o contrato D-11 (`cabecalho_pagina`/`titulo_pagina`/`conteudo_pagina`) vale só para os blocos internos do shell.html | Pattern 4 | Baixo — renomear tocaria login.html sem ganho [ASSUMED] |

## Open Questions

1. **`healthz` entra nesta fase?** (item de discretion do CONTEXT.md)
   - O que sabemos: **já existe** — a Fase 1 implementou `core.views.healthz` e o roteou em `config/urls.py` (`path("healthz", ...)`), com `@login_not_required` e SELECT 1 no banco.
   - Recomendação: nada a fazer nesta fase — discretion resolvida por fato consumado; registrar no plano como "já entregue na Fase 1".
2. **Cor primária default do placeholder "Sistema Base".**
   - Recomendação: `#1e40af` (azul neutro, contraste ~8.7:1 sobre branco — AA para texto). Qualquer hex serve; vira variável Copier na Fase 4. Decisão de discretion do planner.
3. **Onde exercitar `HistoricalRecords()` de domínio (D-23)?**
   - O que sabemos: nenhum modelo de domínio existe até a Fase 3; nesta fase o padrão só pode ser documentado (`core/README.md`) + exemplificado pelo `Usuario` via `register()`.
   - Recomendação: critério de sucesso 4 se verifica por: pacote instalado, middleware ativo, `HistoricalUsuario` migrando e gravando, README documentando a convenção.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker + Compose | build/execução, testes no container | ✓ | 29.5.2 / v5.1.4 | — |
| Stack `sistema_base` (web+db) | migrações, testes, verificação manual | ✓ (rodando, healthy) | Postgres 17, web healthy | `docker compose up -d` |
| PyPI (acesso de rede no build) | instalar simple-history no rebuild | ✓ (verificado via curl ao PyPI) | — | — |
| Pillow (host) | gerar ícones PWA placeholder | ✓ | 12.1.1 | PNG sólido via zlib/struct puro (sem texto da sigla) |
| Pillow (container web) | — (testes leem IHDR na mão, como na PCA) | ✗ | — | não necessário — não instalar |
| node no host | — | não necessário | — | Tailwind roda no estágio Docker (D-07 da Fase 1) |
| PCA `/opt/web/pca` | fonte de extração (somente leitura) | ✓ | Django 5.2.16, simple-history 3.13.0 | — |

**Missing dependencies with no fallback:** nenhuma.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | não (nada novo) | Já coberto na Fase 1 (axes, Argon2) |
| V3 Session Management | sim | Logout limpa Cache Storage + `htmx-history-cache` ANTES do POST; `hx-history="false"` no body evita snapshot de HTML autenticado no localStorage |
| V4 Access Control | sim | Admin: gate padrão do Django (`is_staff`) — ver A1; `LoginRequiredMiddleware` continua bloqueando tudo por padrão; só manifest/sw ganham `@login_not_required` (conteúdo não sensível) |
| V5 Input Validation | mínimo | Nenhum form novo; `trilha` é montada pela view (sem input do usuário); `admin_tema_css` é interpolado de settings (operador), com `|safe` — a COR_PRIMARIA vem do `.env`, não de usuário |
| V6 Cryptography | não | Nada novo |
| V12/V14 (cache/config) | sim | SW nunca cacheia HTML/HTMX/JSON (só GET same-origin `/static/`); manifest não expõe dados de sessão |

### Known Threat Patterns for este stack

| Pattern | STRIDE | Mitigação padrão |
|---------|--------|------------------|
| HTML autenticado persistido no cliente (Cache Storage / htmx history) | Information Disclosure | Estratégia do SW (só `/static/`), limpeza no logout, `hx-history="false"` |
| SW malicioso/escopo indevido | Elevation of Privilege | SW servido por view própria same-origin, escopo explícito, sem imports remotos |
| CSS injection via `admin_tema_css|safe` | Tampering | Valor vem de settings/.env (confiança de operador); se o planner quiser endurecer, validar formato `#RRGGBB` da COR_PRIMARIA no settings |
| Clickjacking do admin | Tampering | `XFrameOptionsMiddleware` DENY já ativo (Fase 1) |

## Sources

### Primary (HIGH confidence)
- `/opt/web/pca/` — arquivos canônicos lidos integralmente nesta sessão: `core/admin_site.py`, `core/apps.py`, `core/admin.py`, `core/views.py`, `core/models.py`, `core/urls.py`, `core/templates/{admin/base_site,core/shell,core/_breadcrumbs,core/_nav_visoes}.html`, `core/templates/base.html`, `core/static/offline.html`, `core/static/src/input.css`, `core/tests/{test_pwa,test_admin}.py`, `config/settings/{base,dev}.py`, `tailwind.config.js`, `requirements.txt` — produção viva, padrão comprovado
- PyPI (`pypi.org/pypi/django-simple-history/json`) — versão 3.13.0, classifiers Django 5.2/6.0, requires_python >=3.10, upload 2026-07-22 [VERIFIED]
- Código-fonte do Django stable/5.2.x (`django/contrib/admin/static/admin/css/base.css` via raw.githubusercontent.com) — variáveis `--primary`, `--secondary`, `--header-bg`, `--link-fg` confirmadas [VERIFIED]
- django-simple-history docs — `quick_start.html` (INSTALLED_APPS, middleware, register) e `common_issues.html` ("Tracking Custom Users": *"Use register() to track changes to the custom user model instead of setting HistoricalRecords on the model directly"*) [CITED: django-simple-history.readthedocs.io/en/latest/common_issues.html]
- slopcheck — `django-simple-history` → `[OK]` [VERIFIED]
- Código atual do sistema_base (Fase 1) — lido integralmente: settings, base.html, shell.html, login.html, context_processors, urls, apps, Dockerfile, tailwind.config.js, .env.example

### Secondary (MEDIUM confidence)
- Comportamento do `{% extends %}` recursivo (mesmo nome de template): suportado desde Django 1.9 e provado em produção pela PCA — não re-verificado na doc nesta sessão

### Tertiary (LOW confidence)
- Nenhuma — não houve claims baseados só em WebSearch

## Metadata

**Confidence breakdown:**
- Standard stack: ALTA — única dependência nova verificada em registry oficial + slopcheck + produção PCA
- Arquitetura: ALTA — todos os padrões lidos da fonte canônica em produção
- Pitfalls: ALTA — maioria documentada inline na PCA como bugs reais de execução; Pitfall 6 (tokens ausentes) descoberto e confirmado nesta sessão por inspeção direta do repo
- Tokens Tailwind (Pattern 1): MÉDIA-ALTA — a estratégia (1 literal + derivação JS) é derivação lógica das restrições D-17, não transplante; hexes neutros copiados da paleta validada da PCA

**Research date:** 2026-08-18
**Valid until:** 2026-09-18 (stack pinada e estável; revalidar versão do simple-history se o plano atrasar)
