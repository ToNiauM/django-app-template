# Roadmap: Sistema Base — Template CFC

## Overview

Do zero a um template Copier que gera sistemas Django completos para o CFC. Primeiro nasce a fundação: um projeto Django rodando em Docker com autenticação, usuário customizado e settings seguros por ambiente. Depois vem o shell visual (layout, admin, PWA, auditoria), então o app exemplo que serve de documentação viva (CRUD de referência + dashboard ECharts). Com o sistema-modelo pronto, ele é templatizado via Copier (variáveis, `copier copy`/`copier update`, ops de produção) e, por fim, o fluxo completo de nascimento é verificado ponta a ponta e documentado no README.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Fundação Django** - Projeto Django em Docker com auth, usuário customizado e settings seguros por ambiente (completed 2006-08-18)
- [x] **Phase 2: Shell Visual e Kernel** - Layout base, admin customizado, PWA e auditoria no app `core` (completed 2006-08-18)
- [x] **Phase 3: App Exemplo** - CRUD de referência e dashboard ECharts como documentação viva (completed 2006-08-18)
- [x] **Phase 4: Templatização Copier** - Sistema-modelo vira template parametrizado com `copier copy`/`copier update` e ops de produção (completed 2006-08-18)
- [x] **Phase 5: Verificação e Documentação** - Fluxo de nascimento validado ponta a ponta e README completo (completed 2006-08-18)
- [ ] **Phase 6: Customização Visual e Persistência de Dados** - Pontos de customização de marca no `core` (logo da entidade, logo do subsistema, logo/nome do PWA) e dados do banco persistidos no host sobrevivendo a `docker compose down -v`

## Phase Details

### Phase 1: Fundação Django

**Goal**: Um projeto Django 5.2 rodando em Docker Compose (app + PostgreSQL 17), com `Usuario` customizado desde a primeira migração, login/logout funcionais e settings por ambiente que aplicam as invariantes de segurança e localização da PCA.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: CFG-01, CFG-02, CFG-03, CFG-04, CORE-01, CORE-02, INF-01, INF-02
**Success Criteria** (what must be TRUE):

  1. `docker compose up -d` + `migrate` + `createsuperuser` sobe o sistema com PostgreSQL 17 e permite login/logout pela tela de login
  2. O modelo `Usuario` customizado (AbstractUser, manager próprio) existe desde a migração 0001 do `core`
  3. Toda configuração sensível vem do `.env` (django-environ) e o `.env.example` cobre todas as variáveis
  4. Settings de produção aplicam Argon2, django-axes, cookies seguros, HSTS/proxy, `DEBUG=False` e `ALLOWED_HOSTS` restrito; localização pt-br/America/Sao_Paulo ativa
  5. Requisições HTMX passam CSRF via `htmx:configRequest` lendo o token do cookie (com `CSRF_COOKIE_HTTPONLY = False`)

**Plans**: 4 plans (4 waves)

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Settings por ambiente: `config/settings/{base,dev,prod}.py` via django-environ, requirements.txt, .env.example

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — Core kernel: `Usuario`/`UsuarioManager`, axes callable, middleware HTMX, healthz, base.html com CSRF/htmx

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03-PLAN.md — Docker infra + migração 0001 + subida real (build, up, migrate, createsuperuser)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 01-04-PLAN.md — Login/logout reais: views + templates + testes de comportamento + checkpoint de verificação via navegador

### Phase 2: Shell Visual e Kernel

**Goal**: O app `core` entrega a experiência visual completa e agnóstica de domínio: layout base com navegação e breadcrumbs, admin com identidade visual, PWA parametrizado e `django-simple-history` pronto para os modelos de domínio.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: CORE-03, CORE-04, CORE-05, CORE-06
**UI hint**: yes
**Success Criteria** (what must be TRUE):

  1. Usuário logado navega em shell com `base.html`/`shell.html`, navegação e breadcrumbs funcionais
  2. Admin site customizado exibe a identidade visual do sistema (nome e cor primária)
  3. O sistema instala como PWA com manifest, ícones e service worker parametrizados pelo nome do sistema
  4. `django-simple-history` está instalado e documentado como padrão de auditoria para modelos de domínio

**Plans**: 4 plans (4 waves — serializadas: a imagem `web` embute o código no build, então cada plan reconstrói/reutiliza a mesma stack Docker)

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — Identidade parametrizada: settings SISTEMA_NOME/SIGLA/COR_PRIMARIA + context processor + paleta Tailwind (fecha o Pitfall 6) + regra [x-cloak]

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02-PLAN.md — Shell completo: aside + gaveta Alpine, `_nav.html` (ponto de extensão), `_breadcrumbs.html` (contrato trilha), blocos de página, login ajustado

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-03-PLAN.md — Admin com identidade (AdminSite isolado + override extrastyle) + django-simple-history (register(Usuario), migração 0002, convenção no README)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 02-04-PLAN.md — PWA: manifest/sw por views, ícones + script de regeneração, offline.html, limpeza de cache no logout, test_pwa

### Phase 3: App Exemplo

**Goal**: `apps/exemplo/` demonstra o padrão de referência da casa — CRUD completo com tabela paginada server-side, filtros e modais HTMX, mais dashboard ECharts com agregações via ORM — e é removível sem quebrar o sistema.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: EX-01, EX-02, EX-03, EX-04
**UI hint**: yes
**Success Criteria** (what must be TRUE):

  1. Usuário opera CRUD de exemplo com tabela paginada server-side, ordenação e filtros multi-seleção
  2. Usuário cria e edita registros do exemplo via modal HTMX sem recarregar a página
  3. Dashboard ECharts exibe agregações calculadas via ORM (`annotate`/`aggregate`), nunca em Python
  4. Remover o app `exemplo` (seguindo os passos documentados) deixa o sistema íntegro

**Plans**: 3 plans (3 waves)

Plans:
**Wave 1**

- [x] 03-01-PLAN.md — Fundação: assets vendor ECharts, tags de formatação pt-BR, modelo `ItemExemplo` com auditoria simple-history, migrações e comando `seed_exemplo`

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 03-02-PLAN.md — CRUD de Referência: tabela paginada server-side, busca textual, filtros multi-seleção, ordenação com whitelist, modais HTMX (criar/editar/excluir com HTTP 422 e HX-Trigger)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 03-03-PLAN.md — Dashboard Analítico: KPIs agregados via ORM no PostgreSQL, gráficos ECharts (barras e donut), documentação de isolamento/remoção no README e testes de desacoplamento

### Phase 4: Templatização Copier

**Goal**: O sistema-modelo vira template Copier: tudo que difere entre sistemas (nome, slug, subdomínio, porta, banco, cor primária) vira variável de template, `copier copy` gera um sistema novo e `copier update` puxa evoluções do núcleo; `ops/` traz backup e vhost nginx de exemplo.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: TPL-01, TPL-02, TPL-03, TPL-04, INF-03, INF-04
**Success Criteria** (what must be TRUE):

  1. `copier copy` faz as perguntas do template e gera um projeto Django completo e autocontido
  2. Nenhum valor que difere entre sistemas fica hard-coded no código gerado — tudo vem das respostas do Copier
  3. `copier update` aplica evoluções do núcleo em um sistema já gerado
  4. O código gerado não contém nenhuma menção a "PCA" ou a qualquer domínio de negócio
  5. `ops/` inclui backup do banco e exemplo de vhost nginx; o app escuta só em `127.0.0.1` e a migração completa é dump + `.env` + `docker compose up -d` + `migrate` + proxy/DNS

**Plans**: 7/7 plans executed

Plans:
**Wave 1**

- [x] 04-01-PLAN.md — Gate humano obrigatório de procedência de `copier==9.17.1`

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 04-02-PLAN.md — Tracer `copier copy`: perguntas, answers, exclusões, `.env.example` e READMEs

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 04-03-PLAN.md — Identidade `.env`-first: settings, Tailwind, entrypoint, seed, ícones e auditoria do gerado

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 04-04-PLAN.md — App exemplo condicional nos quatro destinos exatos, sem `_skip_if_exists`

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 04-05-PLAN.md — Compose isolado e backup/retencão containerizados, configurados por `.env`

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 04-06-PLAN.md — Restore confinado, Nginx TLS e runbook portátil de migração

**Wave 7** *(blocked on Wave 6 completion)*

- [x] 04-07-PLAN.md — Matrizes de copy e prova Git/Copier A→B→C sem ressuscitar o app exemplo

### Phase 5: Verificação e Documentação

**Goal**: O fluxo de nascimento completo é provado ponta a ponta — sistema gerado passa a suíte de testes e fica navegável sem editar código — e o README documenta do `copier copy` ao proxy/DNS.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: QA-01, QA-02, DOC-01
**Success Criteria** (what must be TRUE):

  1. O sistema gerado passa a suíte de testes do core e do app exemplo
  2. `copier copy` + preencher `.env` + `docker compose up -d` + `migrate` + `createsuperuser` produz sistema navegável (login, shell, CRUD e dashboard) sem editar código
  3. README do template documenta o nascimento de um sistema, do `copier copy` ao proxy/DNS

**Plans**: 1/3 plans executed

Plans:
**Wave 1**

- [x] 05-01-PLAN.md — Tracer de nascimento real: cópia efêmera, Compose, migração, superusuário, suíte Django e smoke HTTP

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 05-02-PLAN.md — README canônico: nascimento local, navegação, regressão e publicação por proxy/TLS/DNS

**Wave 3** *(blocked on Waves 1–2 completion)*

- [x] 05-03-PLAN.md — Ambiente retido, checkpoint visual 32/32 e cleanup confinado

### Phase 6: Customização Visual e Persistência de Dados

**Goal**: Pontos de customização de marca claros e centralizados no app `core` — logo principal da entidade, logo do subsistema e logo/nome do PWA trocáveis em locais únicos e documentados — e dados do PostgreSQL persistidos no host (bind mount), sobrevivendo a `docker compose down -v`.
**Depends on**: Phase 5
**Requirements**: TBD
**Success Criteria** (what must be TRUE):

  1. Existe um local único e documentado no `core` para inserir/trocar o logo principal da entidade
  2. Existe um local único e documentado no `core` para inserir/trocar o logo do subsistema
  3. O logo e o nome do PWA são customizáveis a partir do `core`, refletindo no manifest e na instalação
  4. Os dados do banco ficam no host e sobrevivem a `docker compose down -v` (recriar os containers não perde dados)

**Plans**: 3 plans (3 waves)

Plans:
**Wave 1**

- [x] 06-01-PLAN.md — Persistência no host: bind mount `${PGDATA_DIR:-./dados/pg}` no compose, `.gitignore` do sistema gerado (fix do `_exclude`), testes de template e tracer com prova de `down -v`
**Wave 2** *(blocked on Wave 1 — o tracer corrigido é a verificação dos planos seguintes)*

- [ ] 06-02-PLAN.md — Logos de marca: placeholders SVG neutros em caminhos fixos, inserção via `{% static %}` no shell/login, favicon e regressão Django (test_logos.py)
**Wave 3** *(blocked on Waves 1–2 — os verifies pesados de 06-02 rodam com a árvore de docs intocada)*

- [ ] 06-03-PLAN.md — Documentação: seção "Customização de marca" no README gerado, etapa de logos no nascimento, notas de persistência e migração no runbook

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fundação Django | 4/4 | Complete    | 2006-08-18 |
| 2. Shell Visual e Kernel | 4/4 | Complete    | 2006-08-18 |
| 3. App Exemplo | 3/3 | Complete    | 2006-08-18 |
| 4. Templatização Copier | 7/7 | Complete    | 2006-08-18 |
| 5. Verificação e Documentação | 3/3 | Complete   | 2006-08-18 |
| 6. Customização Visual e Persistência de Dados | 1/3 | In Progress|  |
