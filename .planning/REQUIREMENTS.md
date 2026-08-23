# Requisitos: Sistema Base — Template CFC

**Definido em:** 2026-08-17
**Valor Central:** Criar um sistema novo funcional (login, layout, CRUD de exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time apenas modelar o domínio em `apps/`.

## Requisitos v1

Requisitos da entrega inicial. Cada um mapeia para fases do roadmap.

### Template Copier (TPL)

- [x] **TPL-01**: Operador pode gerar um projeto Django completo com `copier copy`, respondendo às perguntas do template
- [x] **TPL-02**: Template parametriza nome do sistema, slug, subdomínio, porta interna, nome do banco e cor primária — nada que difira entre sistemas fica hard-coded
- [x] **TPL-03**: Operador pode puxar evoluções do núcleo em um sistema já gerado via `copier update`
- [x] **TPL-04**: Código gerado não contém nenhuma menção a "PCA" ou a qualquer domínio de negócio

### Configuração (CFG)

- [x] **CFG-01**: Sistema gerado tem `config/` com settings por ambiente via `django-environ` — toda configuração sensível vem do `.env`
- [x] **CFG-02**: Settings de produção aplicam as invariantes de segurança: Argon2 no topo de `PASSWORD_HASHERS`, `django-axes`, cookies `Secure`/`HttpOnly`/`SameSite=Lax`, HSTS e `SECURE_PROXY_SSL_HEADER` atrás do proxy, `DEBUG=False`, `ALLOWED_HOSTS` restrito
- [x] **CFG-03**: Settings aplicam a localização padrão: `pt-br`, `America/Sao_Paulo`, `USE_TZ = True`, datas `DD/MM/AAAA`, moeda `R$` pt-BR
- [x] **CFG-04**: `CSRF_COOKIE_HTTPONLY = False` com CSRF do HTMX configurado via `htmx:configRequest` (nunca `hx-headers`)

### Núcleo (CORE)

- [x] **CORE-01**: Sistema gerado tem `Usuario` customizado (AbstractUser) com manager próprio, presente desde a primeira migração
- [x] **CORE-02**: Usuário pode fazer login e logout pela tela de login com a identidade visual do sistema
- [x] **CORE-03**: Administrador acessa admin site customizado com a identidade visual do sistema
- [x] **CORE-04**: Sistema gerado tem layout base (`base.html`, `shell.html`) com navegação, breadcrumbs, template tags, context processors e middleware do núcleo
- [x] **CORE-05**: Sistema gerado funciona como PWA (manifest, ícones, service worker) parametrizado pelo nome do sistema
- [x] **CORE-06**: `django-simple-history` está disponível e configurado como padrão de auditoria para modelos de domínio

### App Exemplo (EX)

- [x] **EX-01**: Usuário pode operar um CRUD completo de exemplo: tabela paginada server-side, ordenação e filtros multi-seleção
- [x] **EX-02**: Usuário pode criar/editar registros do exemplo via modal HTMX
- [x] **EX-03**: Usuário pode ver dashboard ECharts de exemplo com agregações feitas via ORM (`annotate`/`aggregate`), nunca em Python
- [x] **EX-04**: App `exemplo` é autocontido e removível — apagá-lo (e suas referências documentadas) não quebra o sistema

### Infraestrutura (INF)

- [x] **INF-01**: Sistema gerado sobe com `docker compose up -d` (app + PostgreSQL 17) usando `Dockerfile`, `compose.yml` e `entrypoint.sh` do template
- [x] **INF-02**: Sistema gerado inclui `.env.example` completo cobrindo todas as variáveis necessárias
- [x] **INF-03**: Sistema gerado inclui `ops/` com script de backup do banco e exemplo de vhost nginx
- [x] **INF-04**: App escuta só em `127.0.0.1` atrás do proxy; migração completa = dump + `.env` + `docker compose up -d` + `migrate` + proxy/DNS, sem nenhuma dependência do host

### Design System (DS)

- [x] **DS-01**: Sistema gerado nasce com os tokens de cor em variáveis CSS em `core/static/src/input.css`, e `tailwind.config.js` só aponta para elas via `var(--cor-*)`
- [ ] **DS-02**: Sistema gerado tem tema escuro funcional por `[data-tema="escuro"]`, com escolha persistida em `localStorage` e sem flash de tema
- [x] **DS-03**: Régua física declarada: 3 degraus de superfície com elevação, raio único de 2px, 6 degraus tipográficos com teto de 20px, pilha `system-ui` e `:focus-visible` único em `@layer base`
- [x] **DS-04**: Vocabulário de componente `.results` `.module` `.form-row` `.btn` (+4 variantes) declarado em `@layer components` e protegido por `safelist`
- [ ] **DS-05**: Nenhum hex de cor em template ou em JS de template; a paleta do gráfico chega do servidor por `json_script` e o chrome é lido das variáveis CSS em runtime
- [x] **DS-06**: `cor_primaria` continua sendo pergunta do Copier e é a única entrada da família de marca nos dois temas; o derivado nunca edita `tailwind.config.js`

### Navegação (NAV)

- [x] **NAV-01**: `core/templates/core/_nav.html` fica intocado por qualquer derivado; itens de domínio entram apenas por `core/templates/core/_nav_dominio.html`, provado por teste de contrato
- [x] **NAV-02**: Item de navegação vira `{% item_nav %}` — uma linha por item, com o tratamento de estado ativo do padrão por construção
- [x] **NAV-03**: Itens do app exemplo saem do `_nav.html` base; gerar com `incluir_app_exemplo=true` e depois remover os itens não exige editar arquivo upstream

### Release (REL)

- [x] **REL-01**: `copier update` de um sistema na v0.1.0 para esta versão não exige resolução manual em arquivo que o derivado não tenha tocado; a fase fecha com a tag `v0.2.0`

### Qualidade (QA)

- [x] **QA-01**: Template inclui suíte de testes do core e do app exemplo, e o sistema gerado passa essa suíte
- [x] **QA-02**: Fluxo de nascimento completo funciona sem editar código: `copier copy` + preencher `.env` + `docker compose up -d` + `migrate` + `createsuperuser` produz sistema navegável (login, shell com navegação, CRUD e dashboard de exemplo)
- [x] **QA-03**: Os testes Django do `core` e do `apps.exemplo` e as 11 suítes de `.template-tests/` seguem verdes, incluindo o ensaio A→B→C de `copier update`

### Documentação (DOC)

- [x] **DOC-01**: README do template documenta o nascimento de um sistema, do `copier copy` ao proxy/DNS

## Requisitos v2

Adiados para entrega futura. Rastreados mas fora do roadmap atual.

### Evolução da família

- **FAM-01**: SSO / identidade centralizada entre subdomínios
- **FAM-02**: Migração da PCA para o template

## Fora de Escopo

Excluídos explicitamente. Documentado para evitar scope creep.

| Item | Motivo |
|------|--------|
| Conteúdo de domínio (PCA, orçamento, financeiro, dívida ativa) no template | Template é agnóstico de domínio; só o app `exemplo`, descartável |
| SSO / identidade centralizada | Evolução futura; template apenas não pode inviabilizá-la (usuário customizado desde a 1ª migração) |
| Integrações externas | Não fazem parte do núcleo replicável |
| Alterações em `/opt/web/pca` | PCA é fonte da extração e segue viva como está |
| Construir o sistema Orçamento | Será o primeiro uso real do template, em projeto próprio |

## Rastreabilidade

Quais fases cobrem quais requisitos. Preenchido na criação do roadmap.

| Requisito | Fase | Status |
|-----------|------|--------|
| CFG-01 | Phase 1 | Complete |
| CFG-02 | Phase 1 | Complete |
| CFG-03 | Phase 1 | Complete |
| CFG-04 | Phase 1 | Complete |
| CORE-01 | Phase 1 | Complete |
| CORE-02 | Phase 1 | Complete |
| INF-01 | Phase 1 | Complete |
| INF-02 | Phase 1 | Complete |
| CORE-03 | Phase 2 | Complete |
| CORE-04 | Phase 2 | Complete |
| CORE-05 | Phase 2 | Complete |
| CORE-06 | Phase 2 | Complete |
| EX-01 | Phase 3 | Complete |
| EX-02 | Phase 3 | Complete |
| EX-03 | Phase 3 | Complete |
| EX-04 | Phase 3 | Complete |
| TPL-01 | Phase 4 | Pending |
| TPL-02 | Phase 4 | Pending |
| TPL-03 | Phase 4 | Pending |
| TPL-04 | Phase 4 | Pending |
| INF-03 | Phase 4 | Pending |
| INF-04 | Phase 4 | Pending |
| QA-01 | Phase 5 | Complete |
| QA-02 | Phase 5 | Complete |
| DOC-01 | Phase 5 | Complete |
| DS-01 | Phase 7 | Complete |
| DS-02 | Phase 7 | Pending |
| DS-03 | Phase 7 | Complete |
| DS-04 | Phase 7 | Complete |
| DS-05 | Phase 7 | Pending |
| DS-06 | Phase 7 | Complete |
| NAV-01 | Phase 7 | Complete |
| NAV-02 | Phase 7 | Complete |
| NAV-03 | Phase 7 | Complete |
| REL-01 | Phase 7 | Complete |
| QA-03 | Phase 7 | Complete |

**Cobertura:**

- Requisitos v1: 36 no total (25 da entrega inicial + 11 da Fase 7)
- Mapeados em fases: 36
- Não mapeados: 0 ✓

---
*Requisitos definidos em: 2026-08-17*
*Última atualização: 2026-08-23 — famílias DS, NAV e REL acrescentadas no planejamento da Fase 7*
