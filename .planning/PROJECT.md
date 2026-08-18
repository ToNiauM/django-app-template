# Sistema Base — Template CFC

## O que é

Template clonável (via Copier) do qual nascem os sistemas web de apoio à decisão do Conselho Federal de Contabilidade (CFC). Não é um sistema que vai ao ar: é um repositório-modelo que gera sistemas Django completos, autocontidos e portáteis — cada sistema gerado tem repo próprio, banco próprio e deploy próprio. A família prevista: PCA (já em produção em `/opt/web/pca`, intocada), Orçamento, Financeiro e Dívida Ativa, cada um em seu subdomínio, todos com a mesma cara, a mesma stack e a mesma operação.

## Valor Central

Criar um sistema novo funcional (login, layout, CRUD de exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time apenas modelar o domínio em `apps/`.

## Requisitos

### Validados

<!-- Entregues e confirmados como valiosos. -->

- ✓ `config/` — settings por ambiente via `django-environ` (tudo via `.env`), urls, wsgi — Fase 1
- ✓ `core/` — `Usuario` customizado (AbstractUser, login por e-mail) com manager próprio, desde a migração 0001 — Fase 1
- ✓ Login/logout funcionais com convenções HTMX/CSRF/axes provadas por testes (13/13) — Fase 1
- ✓ Infra base: `Dockerfile` multi-stage (Tailwind + runtime não-root), `compose.yml` (app + PostgreSQL 17), `entrypoint.sh`, `.env.example` — Fase 1

### Ativos

<!-- Escopo atual. Construindo em direção a estes. -->

- [ ] Estrutura de template Copier com variáveis (nome do sistema, slug, subdomínio, porta interna, nome do banco, cor primária) — nada hard-coded
- [ ] `core/` — admin site customizado com identidade visual do sistema
- [ ] `core/` — layout base: `base.html`, `shell.html`, login, navegação, breadcrumbs, template tags, context processors, middleware
- [ ] `core/` — PWA (manifest, ícones, service worker) parametrizado pelo nome do sistema
- [ ] `apps/exemplo/` — CRUD de referência: tabela paginada server-side, ordenação, filtros multi-seleção, edição via modal HTMX
- [ ] `apps/exemplo/` — dashboard ECharts com agregações via ORM (`annotate`/`aggregate`)
- [ ] Infra restante: `ops/` (backup do banco, exemplo de vhost nginx)
- [ ] Suíte de testes do core e do app exemplo, que passa no sistema gerado
- [ ] `README` do template: documentação de nascimento de sistema, do `copier copy` ao proxy/DNS
- [ ] `copier copy` + `.env` + `docker compose up -d` + `migrate` + `createsuperuser` produz sistema navegável sem editar código

### Fora de Escopo

<!-- Fronteiras explícitas. Inclui o porquê para evitar re-inclusão. -->

- Conteúdo de domínio (PCA, orçamento, financeiro, dívida ativa) dentro do template — só o app `exemplo`, descartável; o template deve ser agnóstico de domínio
- SSO / identidade centralizada — evolução futura; cada sistema tem auth própria, mas o template não deve criar acoplamento que inviabilize SSO depois
- Integrações externas — não fazem parte do núcleo replicável
- Alterações em `/opt/web/pca` — a PCA é fonte da extração, segue viva como está; migrá-la para o template é decisão futura
- Construir o sistema Orçamento — será o primeiro uso real do template, em projeto próprio

## Contexto

- O CFC terá uma família de sistemas web de apoio à tomada de decisão do presidente e da gestão. Quatro sistemas principais, cada um em seu subdomínio: PCA (`pca.dominio`, em produção), Orçamento (`orcamento.dominio`, primeiro derivado do template), Financeiro (`financeiro.dominio`), Dívida Ativa (`dividaativa.dominio`).
- A PCA já separa boilerplate de domínio: `config/` + `core/` + `compose.yml` + `Dockerfile` + `entrypoint.sh` + `ops/` são replicáveis; o domínio vive só em `apps/`. O template formaliza essa fronteira — o que a PCA provou em produção vira o template.
- O app `exemplo` serve de documentação viva: quem gera um sistema novo o estuda, copia o padrão para seus apps de domínio e o remove.

### Invariantes herdadas da PCA (valem para todo sistema gerado)

- **Portabilidade:** nenhuma dependência do host. Migração completa = dump + `.env` + `docker compose up -d` + `migrate` + proxy/DNS. Qualquer passo extra é acoplamento indevido.
- **Segurança:** Argon2 no topo de `PASSWORD_HASHERS`; `django-axes`; cookies `Secure`/`HttpOnly`/`SameSite=Lax`; HSTS e `SECURE_PROXY_SSL_HEADER` atrás do proxy; `DEBUG=False` e `ALLOWED_HOSTS` restrito em produção; app escuta só em `127.0.0.1`.
- **CSRF do HTMX via `htmx:configRequest`, nunca `hx-headers`** (o token rotaciona no login/logout e precisa ser lido do cookie a cada requisição); consequência: `CSRF_COOKIE_HTTPONLY = False`.
- **Localização:** `pt-br`, `America/Sao_Paulo`, `USE_TZ = True`, datas `DD/MM/AAAA`, moeda `R$` pt-BR.
- **Desempenho:** agregações de dashboard via ORM (`annotate`/`aggregate`), nunca em Python; listagens paginadas server-side.
- **Auditoria:** `django-simple-history` disponível no template como padrão para modelos de domínio.

## Restrições

- **Stack fechada** (idêntica à da PCA): Python 3.12+ · Django 5.2 LTS · PostgreSQL 17 · Django Templates + HTMX + Alpine.js + Tailwind · ECharts · Gunicorn · Docker Compose · django-environ · django-simple-history · django-axes · Argon2 · WhiteNoise — não reabrir
- **Mecanismo:** template clonável via Copier (`copier copy` gera; `copier update` puxa evoluções do núcleo) — não é pacote pip, não é monorepo
- **Compatibilidade:** zero menção a "PCA" ou a qualquer domínio no código gerado
- **Idioma:** toda a documentação e artefatos de planejamento em pt-BR

## Decisões-Chave

| Decisão | Justificativa | Resultado |
|---------|---------------|-----------|
| Template clonável via Copier (não pacote pip, não monorepo) | `copier copy` gera o sistema; `copier update` permite puxar evoluções do núcleo; cada sistema fica autocontido e portátil | — Pendente |
| PCA não será alterada | É a fonte da extração, provada em produção; segue em `/opt/web/pca`; migração é decisão futura | — Pendente |
| Autenticação independente por sistema | Cada sistema tem seus usuários e login; SSO é evolução futura; usuário customizado desde a primeira migração evita acoplamento que inviabilize SSO | — Pendente |
| Stack fechada idêntica à da PCA | Mesma cara, mesma stack, mesma operação em toda a família de sistemas | — Pendente |

## Evolução

Este documento evolui nas transições de fase e nos marcos do projeto.

**Após cada transição de fase** (via `/gsd-transition`):
1. Requisitos invalidados? → Mover para Fora de Escopo com o motivo
2. Requisitos validados? → Mover para Validados com referência à fase
3. Novos requisitos surgiram? → Adicionar aos Ativos
4. Decisões a registrar? → Adicionar às Decisões-Chave
5. "O que é" ainda está correto? → Atualizar se derivou

**Após cada marco** (via `/gsd:complete-milestone`):
1. Revisão completa de todas as seções
2. Checagem do Valor Central — ainda é a prioridade certa?
3. Auditar Fora de Escopo — motivos ainda valem?
4. Atualizar Contexto com o estado atual

---
*Última atualização: 2026-08-18 após conclusão da Fase 1 (Fundação Django)*
