# Sistema Base — Template CFC

## O que é

Template clonável (via Copier) do qual nascem os sistemas web de apoio à decisão do Conselho Federal de Contabilidade (CFC). Não é um sistema que vai ao ar: é um repositório-modelo que gera sistemas Django completos, autocontidos e portáteis — cada sistema gerado tem repo próprio, banco próprio e deploy próprio. A família prevista: PCA (já em produção em `/opt/web/pca`, intocada), Orçamento, Financeiro e Dívida Ativa, cada um em seu subdomínio, todos com a mesma cara, a mesma stack e a mesma operação.

## Valor Central

Criar um sistema novo funcional (login, layout, CRUD de exemplo, dashboard de exemplo, Docker, backup) em minutos — restando ao time apenas modelar o domínio em `apps/`.

## Marco Atual: v0.3.0 — Guia de construção de sistemas

**Objetivo:** quem gera um sistema pelo template consegue, seguindo um guia em linguagem simples e acessível, construir seus próprios apps de domínio funcionais e escaláveis em Django — sem precisar decifrar o app exemplo sozinho.

**Entregas-alvo:**
- Guia em arquivo(s) próprio(s) (ex.: `GUIA.md` ou `docs/guia/`), com link no README
- O guia chega ao sistema gerado via `copier copy` e sobrevive ao `copier update` sem conflito
- 1 exemplo completo conduzido passo a passo (diárias e passagens) + 2 resumidos (orçamento, controle de materiais) mostrando só o que muda
- Código real testado: os trechos do guia são extraídos de um sistema realmente gerado e rodado durante o marco

## Requisitos

### Validados

<!-- Entregues e confirmados como valiosos. -->

- ✓ `config/` — settings por ambiente via `django-environ` (tudo via `.env`), urls, wsgi — Fase 1
- ✓ `core/` — `Usuario` customizado (AbstractUser, login por e-mail) com manager próprio, desde a migração 0001 — Fase 1
- ✓ Login/logout funcionais com convenções HTMX/CSRF/axes provadas por testes (13/13) — Fase 1
- ✓ Infra base: `Dockerfile` multi-stage (Tailwind + runtime não-root), `compose.yml` (app + PostgreSQL 17), `entrypoint.sh`, `.env.example` — Fase 1
- ✓ `core/` — admin site customizado (`SistemaAdminSite` isolado) com identidade visual via settings (`SISTEMA_NOME`/`COR_PRIMARIA`) — Fase 2
- ✓ `core/` — layout base completo: `base.html`, `shell.html` (aside + gaveta Alpine), `_nav.html`, `_breadcrumbs.html` (contrato `trilha`), context processors de identidade, zero template tags custom por decisão (D-12) — Fase 2
- ✓ `core/` — PWA (manifest e `sw.js` por views, ícones regeneráveis) parametrizada pelos settings — Fase 2
- ✓ `django-simple-history` instalado (`Usuario` registrado com `excluded_fields`) e convenção `HistoricalRecords()` documentada no `core/README.md` — Fase 2
- ✓ `apps/exemplo/` — CRUD de referência: tabela paginada server-side, ordenação com whitelist, filtros multi-seleção, criação e edição via modal HTMX com HTTP 422 e `HX-Trigger` — Fase 3
- ✓ `apps/exemplo/` — dashboard ECharts com agregações 100% via ORM no PostgreSQL (`annotate`/`aggregate`), serialização `json_script` e drill-down — Fase 3
- ✓ `apps/exemplo/` — app 100% autocontido e descartável com protocolo de remoção em 4 passos no `README.md` e testes de isolamento — Fase 3
- ✓ Template Copier in-place com variáveis validadas, defaults não secretos, `copier copy` e `copier update` provados em ensaio A→B→C — Fase 4
- ✓ Infra operacional portátil: Compose isolado, backup/retenção containerizados, ensaio de restore confinado, vhost TLS e runbook de migração — Fase 4
- ✓ Suíte de testes do core e do app exemplo passa no sistema gerado (tracer `.template-tests/test_05_nascimento.sh`, 72 testes na cópia) — Fase 5
- ✓ `README` do template documenta o nascimento completo, do `copier copy` ao proxy/DNS — Fase 5
- ✓ `copier copy` + `.env` + `docker compose up -d` + `migrate` + `createsuperuser` produz sistema navegável sem editar código (prova automatizada + inspeção humana 32/32 do UI-SPEC) — Fase 5
- ✓ Persistência do PostgreSQL por bind mount configurável (`PGDATA_DIR`, default `./dados/pg`), sobrevivendo a `docker compose down -v`, com `.gitignore` gerado e runbook de migração de named volume — Fase 6
- ✓ `core/` — pontos únicos de customização de marca por arquivo fixo: `logo-entidade.svg` e `logo-subsistema.svg` nos templates via `{% static %}`, favicon via ícone PWA, regressão de contrato em `test_logos.py` — Fase 6
- ✓ Seção única "Customização de marca" documentando os 5 pontos (logos, ícones/nome PWA, cor primária, nome/sigla) nos 4 documentos do template — Fase 6
- ✓ Design system do PCA inteiro no sistema gerado: 21 tokens de cor em variáveis CSS (`input.css` como fonte física), 18 overrides de tema escuro, 3 degraus de superfície com elevação mapeada, raio único de 2px, régua tipográfica de 6 degraus com teto em 20px e focus-ring único — Fase 7 (DS-01, DS-02, DS-03)
- ✓ Tema escuro real com controle de 3 estados (Automático/Claro/Escuro) na aside, zero flash no recarregamento e sobrevivência da escolha ao logout/login — Fase 7 (DS-04)
- ✓ Paleta de gráfico derivada de `COR_PRIMARIA` em runtime (`core/tema.py` → `familia_marca`), servida por `json_script` e reconstruída no evento `tema:alterado` sem recarregar a página; zero hex de cor em template ou JS de template — Fase 7 (DS-05, DS-06)
- ✓ Ponto de extensão da navegação: o derivado põe os próprios itens criando só `_nav_dominio.html`, com a inclusion tag `{% item_nav %}` entregando o tratamento visual por construção — provado por sha256 de toda a subárvore `core/` — Fase 7 (NAV-01, NAV-02, NAV-03)
- ✓ `copier update` de v0.1.0 para v0.2.0 sem resolução manual em arquivo não tocado: exit 0, zero marcador de conflito, zero `.rej` — Fase 7 (REL-01, QA-03)
- ✓ `.template-tests/fixtures/guia/apps/diarias/` — app de diárias e passagens completo como fixture, instalado e provado de ponta a ponta numa cópia Copier real (migração, testes in-container, smoke HTTP autenticado) — Fase 8 (PRV-01)
- ✓ Teste negativo estrutural de vazamento: cópia recém-gerada não contém `apps/diarias` nem bytes do fixture (sha256), nas duas variantes do template — Fase 8 (PRV-03)

### Ativos

<!-- Escopo atual. Construindo em direção a estes. -->

- Marco v0.3.0 em definição de requisitos: guia de construção de sistemas (formato, exemplos e distribuição descritos no Marco Atual acima). REQ-IDs serão definidos em `.planning/REQUIREMENTS.md`.

**Encaminhamentos conhecidos, ainda sem fase:**

- Nada pendente de release: a `v0.2.0` já está publicada em `origin` sobre `01ced83`, o commit posterior aos quatro consertos. Os derivados já podem puxá-la.
- Rodar o `copier update` desta versão no DividaAtiva; a Fase 8 de lá encolheu para "adaptar o que é do domínio da dívida", já que o design system chega pelo update
- Construir o Orçamento — primeiro uso real do template, em projeto próprio

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
- **Estado no fecho da v0.2.0 (2026-08-24):** ~7.100 linhas entre Python, templates, JS, CSS e shell; 282 commits; 7 fases, 38 planos. Regressão em três camadas: 13 suítes em `.template-tests/` mais os testes Django do core e do app exemplo, rodando dentro de uma cópia Copier real (`ensaio_django.sh`). A tag `v0.2.0` está publicada em `origin` sobre `01ced83` (objeto `6c7bc99`), o commit posterior aos quatro consertos da rodada de gap closure — o Copier lê a última tag, então é ela que entrega as Fases 6 e 7 aos derivados. Os commits de `main` posteriores a ela são só de `.planning/`, excluído pelo `copier.yml`.

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
| Template clonável via Copier (não pacote pip, não monorepo) | `copier copy` gera o sistema; `copier update` permite puxar evoluções do núcleo; cada sistema fica autocontido e portátil | Validado na Fase 4 |
| PCA não será alterada | É a fonte da extração, provada em produção; segue em `/opt/web/pca`; migração é decisão futura | — Pendente |
| Autenticação independente por sistema | Cada sistema tem seus usuários e login; SSO é evolução futura; usuário customizado desde a primeira migração evita acoplamento que inviabilize SSO | — Pendente |
| Stack fechada idêntica à da PCA | Mesma cara, mesma stack, mesma operação em toda a família de sistemas | — Pendente |
| Herdar o design system direto do PCA, não do DividaAtiva | O PCA é anterior ao template e é a fonte real do padrão; o DividaAtiva tem só um recorte dele. Herdar do filho implicaria implementar o mesmo sistema duas vezes e conflitar com o próprio trabalho dele no `copier update` seguinte | ✓ Bom — Fase 7 |
| `input.css` é a fonte física dos tokens; `tailwind.config.js` chega verbatim | Um único lugar para os valores, e o derivado nunca precisa editar o config do Tailwind. A marca é derivada em runtime por `core/tema.py` a partir de `COR_PRIMARIA` no `.env` | ✓ Bom — trocar a cor e recriar só o `web`, sem rebuild, muda a paleta nos 2 temas |
| Ponto de extensão da nav por `_nav_dominio.html` + `{% item_nav %}` | O `_nav.html` era o pior conflito aberto da família — 79 linhas reescritas pelo DividaAtiva dentro de arquivo upstream. Resolver antes da v0.2.0 é o que torna o `copier update` dos derivados viável | ✓ Bom — teste tira sha256 da subárvore `core/` inteira e exige que o único caminho divergente seja o arquivo do derivado |
| O item "Início" do núcleo permanece no `_nav.html` | Decisão do operador em 2026-08-24: o DividaAtiva aceita exibi-lo. Dar-lhe um jeito de escondê-lo reabriria, só para esse item, o conflito de upstream que a fase eliminou | — Pendente de uso real no primeiro `copier update` de derivado |
| Marco GSD alinhado ao esquema de tag do repositório (v0.2.0, não v1.0) | Duas numerações no mesmo repositório confundiriam quem for procurar a release; a tag é o que o Copier lê | ✓ Bom — marco e release passam a ser o mesmo nome |

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
*Última atualização: 2026-08-26 — Fase 8 (Exemplo provado) concluída: fixture do guia provado de ponta a ponta*
