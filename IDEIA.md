# Sistema Base — template para sistemas de apoio à decisão do CFC

## Visão

O Conselho Federal de Contabilidade terá uma família de sistemas web de apoio à
tomada de decisão do presidente e da gestão, todos com a mesma cara, a mesma
stack e a mesma operação. Quatro sistemas principais, cada um em seu subdomínio:

| Sistema      | Subdomínio            | Situação                                   |
| ------------ | --------------------- | ------------------------------------------ |
| PCA          | `pca.dominio`         | **Em produção** (`/opt/web/pca`) — intocado |
| Orçamento    | `orcamento.dominio`   | Futuro — primeiro derivado do template     |
| Financeiro   | `financeiro.dominio`  | Futuro                                     |
| Dívida Ativa | `dividaativa.dominio` | Futuro                                     |

Este projeto — **sistema_base**, em `/opt/sistema_base` — é o **template
clonável** do qual os novos sistemas nascem. Não é um sistema que vai ao ar: é
um repositório-modelo que gera sistemas. Cada sistema gerado é um projeto
Django completo, autocontido e portátil: repo próprio, banco próprio, deploy
próprio.

**Core value:** criar um sistema novo funcional (login, layout, CRUD de
exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time
apenas modelar o domínio em `apps/`.

## Decisões já tomadas (não reabrir)

1. **Mecanismo: template clonável via Copier** (`copier copy` gera o sistema;
   `copier update` permite puxar evoluções do núcleo depois). Não é pacote pip,
   não é monorepo.
2. **A PCA não será alterada.** Ela é a fonte da extração — o que ela provou em
   produção vira o template — mas segue vivendo em `/opt/web/pca` como está.
   Migrá-la para o template é decisão futura, fora deste escopo.
3. **Autenticação independente por sistema.** Cada sistema tem seus usuários e
   login próprios, herdados do modelo de auth do template. SSO entre
   subdomínios é evolução futura; o template não deve criar acoplamento que a
   inviabilize (ex.: manter usuário customizado desde a primeira migração).
4. **Stack fechada, idêntica à da PCA:** Python 3.12+ · Django 5.2 LTS ·
   PostgreSQL 17 · Django Templates + HTMX + Alpine.js + Tailwind · ECharts ·
   Gunicorn · Docker Compose · django-environ · django-simple-history ·
   django-axes · Argon2 · WhiteNoise.

## O que o template contém (extraído e generalizado da PCA)

A PCA já separa boilerplate de domínio — `config/` + `core/` + `compose.yml` +
`Dockerfile` + `entrypoint.sh` + `ops/` são replicáveis; o domínio vive só em
`apps/`. O template formaliza essa fronteira:

- **`config/`** — settings por ambiente (`django-environ`, tudo via `.env`),
  urls, wsgi.
- **`core/`** — app kernel, agnóstico de domínio:
  - `Usuario` customizado (AbstractUser) com manager próprio;
  - admin site customizado com identidade visual;
  - layout base: `base.html`, `shell.html`, login, navegação, breadcrumbs,
    template tags, context processors, middleware;
  - PWA (manifest, ícones, service worker) parametrizado pelo nome do sistema.
- **`apps/exemplo/`** — um app de demonstração com o padrão de referência da
  casa: um CRUD completo (tabela paginada server-side, ordenação, filtros
  multi-seleção, edição via modal HTMX) + um dashboard ECharts com agregações
  via ORM. Serve de documentação viva; quem gera um sistema novo o estuda,
  copia o padrão para seus apps de domínio e o remove.
- **Infra:** `Dockerfile`, `compose.yml` (app + PostgreSQL 17), `entrypoint.sh`,
  `ops/` (backup do banco, exemplo de vhost nginx), `.env.example` completo.
- **Variáveis do template (Copier):** nome do sistema, slug, subdomínio, porta
  interna, nome do banco, cor primária — tudo que difere entre sistemas vira
  pergunta do `copier copy`; nada fica hard-coded.

## Invariantes herdadas da PCA (valem para todo sistema gerado)

- **Portabilidade:** nenhuma dependência do host. Migração completa = dump +
  `.env` + `docker compose up -d` + `migrate` + proxy/DNS. Qualquer passo
  extra é acoplamento indevido.
- **Segurança:** Argon2 no topo de `PASSWORD_HASHERS`; `django-axes`; cookies
  `Secure`/`HttpOnly`/`SameSite=Lax`; HSTS e `SECURE_PROXY_SSL_HEADER` atrás
  do proxy; `DEBUG=False` e `ALLOWED_HOSTS` restrito em produção; app escuta
  só em `127.0.0.1`.
- **CSRF do HTMX via `htmx:configRequest`, nunca `hx-headers`** (o token
  rotaciona no login/logout e precisa ser lido do cookie a cada requisição);
  consequência: `CSRF_COOKIE_HTTPONLY = False`.
- **Localização:** `pt-br`, `America/Sao_Paulo`, `USE_TZ = True`, datas
  `DD/MM/AAAA`, moeda `R$` pt-BR.
- **Desempenho:** agregações de dashboard via ORM (`annotate`/`aggregate`),
  nunca em Python; listagens paginadas server-side.
- **Auditoria:** `django-simple-history` disponível no template como padrão
  para modelos de domínio.

## O que NÃO é escopo

- Nenhum conteúdo de domínio (nada de PCA, orçamento, financeiro, dívida
  ativa) dentro do template — só o app `exemplo`, descartável.
- SSO / identidade centralizada.
- Integrações externas.
- Alterações em `/opt/web/pca`.
- Construir o sistema Orçamento (ele será o primeiro uso real do template, em
  projeto próprio).

## Critérios de sucesso

1. `copier copy` + preencher `.env` + `docker compose up -d` + `migrate` +
   `createsuperuser` produz um sistema novo navegável — login, shell com
   navegação, CRUD e dashboard de exemplo funcionando — sem editar código.
2. O sistema gerado passa sua suíte de testes (o template inclui testes do
   core e do app exemplo).
3. Zero menção a "PCA" ou a qualquer domínio no código gerado.
4. Documentação de nascimento de sistema (`README` do template): do
   `copier copy` ao proxy/DNS.
