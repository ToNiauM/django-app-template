# Requisitos: Sistema Base — Template CFC

**Definido em:** 2026-08-17
**Valor Central:** Criar um sistema novo funcional (login, layout, CRUD de exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time apenas modelar o domínio em `apps/`.

## Requisitos v1

Requisitos da entrega inicial. Cada um mapeia para fases do roadmap.

### Template Copier (TPL)

- [ ] **TPL-01**: Operador pode gerar um projeto Django completo com `copier copy`, respondendo às perguntas do template
- [ ] **TPL-02**: Template parametriza nome do sistema, slug, subdomínio, porta interna, nome do banco e cor primária — nada que difira entre sistemas fica hard-coded
- [ ] **TPL-03**: Operador pode puxar evoluções do núcleo em um sistema já gerado via `copier update`
- [ ] **TPL-04**: Código gerado não contém nenhuma menção a "PCA" ou a qualquer domínio de negócio

### Configuração (CFG)

- [ ] **CFG-01**: Sistema gerado tem `config/` com settings por ambiente via `django-environ` — toda configuração sensível vem do `.env`
- [ ] **CFG-02**: Settings de produção aplicam as invariantes de segurança: Argon2 no topo de `PASSWORD_HASHERS`, `django-axes`, cookies `Secure`/`HttpOnly`/`SameSite=Lax`, HSTS e `SECURE_PROXY_SSL_HEADER` atrás do proxy, `DEBUG=False`, `ALLOWED_HOSTS` restrito
- [ ] **CFG-03**: Settings aplicam a localização padrão: `pt-br`, `America/Sao_Paulo`, `USE_TZ = True`, datas `DD/MM/AAAA`, moeda `R$` pt-BR
- [ ] **CFG-04**: `CSRF_COOKIE_HTTPONLY = False` com CSRF do HTMX configurado via `htmx:configRequest` (nunca `hx-headers`)

### Núcleo (CORE)

- [ ] **CORE-01**: Sistema gerado tem `Usuario` customizado (AbstractUser) com manager próprio, presente desde a primeira migração
- [ ] **CORE-02**: Usuário pode fazer login e logout pela tela de login com a identidade visual do sistema
- [ ] **CORE-03**: Administrador acessa admin site customizado com a identidade visual do sistema
- [ ] **CORE-04**: Sistema gerado tem layout base (`base.html`, `shell.html`) com navegação, breadcrumbs, template tags, context processors e middleware do núcleo
- [ ] **CORE-05**: Sistema gerado funciona como PWA (manifest, ícones, service worker) parametrizado pelo nome do sistema
- [ ] **CORE-06**: `django-simple-history` está disponível e configurado como padrão de auditoria para modelos de domínio

### App Exemplo (EX)

- [ ] **EX-01**: Usuário pode operar um CRUD completo de exemplo: tabela paginada server-side, ordenação e filtros multi-seleção
- [ ] **EX-02**: Usuário pode criar/editar registros do exemplo via modal HTMX
- [ ] **EX-03**: Usuário pode ver dashboard ECharts de exemplo com agregações feitas via ORM (`annotate`/`aggregate`), nunca em Python
- [ ] **EX-04**: App `exemplo` é autocontido e removível — apagá-lo (e suas referências documentadas) não quebra o sistema

### Infraestrutura (INF)

- [ ] **INF-01**: Sistema gerado sobe com `docker compose up -d` (app + PostgreSQL 17) usando `Dockerfile`, `compose.yml` e `entrypoint.sh` do template
- [ ] **INF-02**: Sistema gerado inclui `.env.example` completo cobrindo todas as variáveis necessárias
- [ ] **INF-03**: Sistema gerado inclui `ops/` com script de backup do banco e exemplo de vhost nginx
- [ ] **INF-04**: App escuta só em `127.0.0.1` atrás do proxy; migração completa = dump + `.env` + `docker compose up -d` + `migrate` + proxy/DNS, sem nenhuma dependência do host

### Qualidade (QA)

- [ ] **QA-01**: Template inclui suíte de testes do core e do app exemplo, e o sistema gerado passa essa suíte
- [ ] **QA-02**: Fluxo de nascimento completo funciona sem editar código: `copier copy` + preencher `.env` + `docker compose up -d` + `migrate` + `createsuperuser` produz sistema navegável (login, shell com navegação, CRUD e dashboard de exemplo)

### Documentação (DOC)

- [ ] **DOC-01**: README do template documenta o nascimento de um sistema, do `copier copy` ao proxy/DNS

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
| (preenchido pelo roadmap) | | |

**Cobertura:**
- Requisitos v1: 21 no total
- Mapeados em fases: 0
- Não mapeados: 21 ⚠️

---
*Requisitos definidos em: 2026-08-17*
*Última atualização: 2026-08-17 após definição inicial*
