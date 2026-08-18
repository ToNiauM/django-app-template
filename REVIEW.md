---
status: no_go_for_multiplication
review_type: business_product_architecture_scalability
reviewed_at: "2026-08-18"
baseline_commit: e9ff67c
scope:
  tracked_files: 91
  planning_artifacts: 36
  automated_tests: 46
verdict:
  continue_development: true
  create_production_derivatives: false
  production_ready: false
---

# Auditoria consultiva — Sistema Base / Template CFC

## Veredito executivo

O projeto tem uma fundação técnica boa e uma tese de produto coerente, mas ainda
não é um template operacional nem deve ser multiplicado em produção.

O **GO** é para continuar o desenvolvimento. O **NO-GO** é para gerar sistemas
reais a partir do repositório atual.

O principal risco não é a capacidade do Django de atender requisições. Para os
quatro sistemas hoje previstos, a stack é compatível com um uso institucional de
porte moderado. O gargalo dominante é a **escala de portfólio**: cada clone cria
outro conjunto de usuários, banco, deploy, backup, monitoramento, suporte e
aplicação de patches. Sem uma operação central de plataforma e sem separar
arquivos controlados pelo template dos arquivos controlados pelo sistema derivado,
o custo e o risco crescem praticamente de forma linear a cada novo sistema.

Quatro bloqueadores precisam ser resolvidos antes do primeiro derivado de
produção:

1. a proposta de valor ainda não foi provada ponta a ponta — não existem Copier,
   app de exemplo, backup, README raiz nem teste real de atualização;
2. a fronteira de propriedade dos arquivos contradiz a promessa de
   `copier update` sem atrito;
3. não existe modelo operacional para governar versões, patches, suporte e
   inventário dos derivados;
4. o caminho de produção e recuperação de desastre ainda não é fail-safe nem foi
   exercitado.

## Base da auditoria

Foram confrontados a visão original em [IDEIA.md](IDEIA.md), os documentos de
produto e roadmap em [.planning/PROJECT.md](.planning/PROJECT.md),
[.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) e
[.planning/ROADMAP.md](.planning/ROADMAP.md), os planos, pesquisas, revisões e
verificações das Fases 1 e 2, o contexto/UI da Fase 3, os 55 arquivos rastreados
fora de `.planning/` e a stack Compose em execução.

Evidências verificadas em 2026-08-18:

- 46/46 testes Django passaram;
- `check --deploy` passou com dois checks HSTS deliberadamente silenciados;
- `makemigrations --check --dry-run` não detectou mudanças;
- `pip check` não encontrou dependências quebradas;
- `docker compose config --quiet` passou;
- `web` e `db` estavam saudáveis;
- o processo web rodava como usuário não-root;
- a imagem web media cerca de 69,5 MB;
- em repouso, o container web usava aproximadamente 137,3 MiB e o PostgreSQL
  38,5 MiB, sem limites de recursos configurados.

Esses números são uma fotografia do ambiente de desenvolvimento, não uma
capacidade garantida de produção. Não foi possível testar `copier copy`,
`copier update`, restauração de backup, comportamento sob carga ou um sistema
derivado porque essas capacidades ainda não existem.

## Leitura do modelo de negócio

### Natureza do produto

O Sistema Base não é um SaaS nem um sistema final. Seu modelo correto é o de uma
**plataforma interna de engenharia**, ou “golden path”, que reduz o tempo e o
risco para criar sistemas de apoio à decisão no CFC.

Não há receita direta a maximizar. A captura de valor ocorre por:

- redução do lead time de criação de um novo sistema;
- redução de horas de engenharia repetidas em autenticação, layout e operação;
- menor incidência de falhas de segurança e configuração;
- experiência consistente para usuários e operadores;
- aplicação mais rápida de correções em toda a família;
- menor custo de treinamento, suporte e troca de equipe.

### Canvas recomendado

| Elemento | Leitura atual | Recomendação |
|---|---|---|
| Patrocinador/cliente | Presidência e gestão do CFC | Nomear patrocinador responsável pelo resultado e pelo orçamento da plataforma |
| Usuários finais | Gestores, analistas e áreas de negócio dos sistemas derivados | Validar fluxos com usuários reais antes de congelar o app de referência |
| Consumidores técnicos | Desenvolvedores, operadores e mantenedores | Tratar documentação, extensão e atualização como parte central do produto |
| Proposta de valor | Novo sistema funcional em minutos, restando o domínio | Medir o ciclo completo, não apenas o `copier copy`: geração, configuração, deploy, acesso e primeira alteração de domínio |
| Canal de entrega | Repositório Copier independente por sistema | Acrescentar catálogo de serviço, pipeline e registro central de derivados |
| Custos principais | Evolução do kernel, operação por sistema, bancos, backups, patches e suporte | Medir TCO por sistema e custo central da plataforma |
| Captura de valor | Economia interna e redução de risco | Publicar scorecard trimestral com tempo, conflitos, incidentes, versões e adoção |
| Relação com consumidores | Hoje implícita | Definir owner do template, owner de cada derivado, suporte e janela de versões suportadas |

### Hipóteses de negócio ainda não validadas

Não há evidência no repositório para responder:

- quantos sistemas e equipes usarão o template em três anos;
- quantos usuários, registros e requisições cada domínio terá;
- quais decisões reais serão tomadas com os dashboards;
- qual é o lead time e custo atuais, usados como baseline;
- quais RPO, RTO e níveis de disponibilidade cada sistema exige;
- quais classes de dados pessoais, financeiros ou sigilosos serão processadas;
- qual equipe terá capacidade permanente para manter e atualizar os derivados;
- qual taxa de conflito em `copier update` é aceitável.

Sem essas respostas, “em minutos” é uma intenção, e não um benefício comprovado.

## O que está bem resolvido

### Arquitetura simples e apropriada ao estágio

A separação conceitual entre `config/` + `core/` e `apps/` é adequada. Django
server-rendered, HTMX, Alpine, Tailwind, Gunicorn e PostgreSQL formam uma stack
pequena, conhecida e suficiente. Não há justificativa atual para introduzir
microserviços, Kubernetes, Redis ou filas apenas por antecipação.

### Segurança básica acima da média para um esqueleto

- usuário customizado existe desde a primeira migração;
- Argon2 é o hasher prioritário;
- django-axes aplica lockout por usuário + IP;
- redirects pós-login validam `next`;
- logout exige POST;
- CSRF do HTMX lê o cookie a cada requisição;
- cookies seguros estão configurados na base;
- container web roda como usuário não-root;
- bind do host assume `127.0.0.1` quando a variável é omitida;
- o service worker não grava HTML autenticado;
- hashes de senha e `last_login` não são copiados para o histórico.

As revisões anteriores encontraram problemas reais no fallback sem JavaScript,
no histórico de senha e na visibilidade da navegação; o estado atual contém as
correções e testes correspondentes.

### Qualidade e rastreabilidade

As Fases 1 e 2 possuem planos, sumários, revisões e verificações detalhadas. A
suíte de 46 testes cobre autenticação, CSRF, lockout, admin, auditoria, identidade,
shell e PWA. Isso é uma base confiável para continuar, embora ainda não exista CI
que execute essas garantias automaticamente.

## Bloqueadores de produto e operação

### BL-01 — A proposta de valor ainda não é utilizável

**Evidência:** o roadmap está em 2 de 5 fases. Não existem `copier.yml`,
`apps/exemplo/`, backup de banco, vhost, README raiz nem testes de geração e
atualização. O único README atual documenta convenções internas do `core`.

**Impacto:** não é possível demonstrar que um operador cria um sistema navegável
sem editar código, nem que uma equipe consegue evoluí-lo sem perder atualizações
do núcleo.

**Recomendação:** tratar o primeiro sistema Orçamento como piloto controlado, não
como rollout. O gate mínimo deve provar em ambiente limpo:

1. geração por Copier;
2. build, migração e suíte verde;
3. customização somente em arquivos destinados ao derivado;
4. atualização da versão N para N+1 sem conflito manual;
5. backup e restauração em outro host;
6. deploy com settings de produção;
7. tempo e esforço humano registrados.

### BL-02 — A fronteira de propriedade torna `copier update` frágil

**Evidência:** o contexto da Fase 3, decisão D-34, manda cada app integrar-se
editando `config/settings/base.py`, `config/urls.py` e
`core/templates/core/_nav.html`. Esses mesmos territórios são mantidos pelo
template. O ECharts ainda é planejado em `core/static/vendor/`, criando um quarto
ponto de integração que contradiz a lista de três pontos e a afirmação de app
“100% autocontido”.

**Impacto:** quanto mais um derivado cresce, mais provável é que o Copier e a
equipe alterem as mesmas linhas. O custo de atualização passa a ser proporcional a
`número de derivados × divergência acumulada`. Correções críticas podem ficar
presas em conflitos e versões antigas.

**Recomendação:** antes de implementar o app de exemplo, definir dois territórios:

- **upstream-owned:** kernel, infraestrutura e arquivos substituíveis pelo Copier;
- **derivative-owned:** apps de domínio, navegação adicional, URLs, settings
  locais e assets do domínio.

Criar extension points estáveis, por exemplo um include de navegação do projeto,
um módulo de URLs do projeto, um módulo de settings locais e assets dentro do app.
O teste obrigatório é: gerar na versão N, adicionar domínio sem editar arquivos
upstream-owned, atualizar para N+1 e obter zero conflitos.

### BL-03 — Falta um modelo operacional para a família de sistemas

**Evidência:** não há owner formal, política de versão, changelog, janela de
suporte, SLA de patch, inventário de derivados, matriz de compatibilidade ou
pipeline central.

**Impacto:** o template pode acelerar o nascimento e simultaneamente criar um
passivo invisível. Ninguém saberá com segurança quais sistemas usam uma versão
vulnerável, quem aprova uma atualização ou até quando uma versão antiga é
suportada.

**Recomendação:** operar o repositório como produto de plataforma:

- time/owner central do kernel;
- versionamento semântico e changelog orientado à migração;
- suporte, por exemplo, à versão atual e à anterior;
- SLA proposto de até 48 horas para propagar correção crítica;
- registro central com sistema, owner, versão do template, domínio, ambiente,
  classificação dos dados, RPO/RTO e data do último restore;
- automação que abra PRs de atualização em todos os derivados;
- dashboard de drift e exceções aprovadas.

### BL-04 — Produção e recuperação ainda não são fail-safe

**Evidência:** o Compose principal atualmente inicia com
`config.settings.dev`; a stack observada estava com `DEBUG=True` e
`ALLOWED_HOSTS=['*']`. `.env.example` também escolhe desenvolvimento e o fallback
de [config/wsgi.py](config/wsgi.py#L6) é `dev`. Backup/restauração, proxy e runbook
são trabalho futuro. O volume PostgreSQL local pode ser removido com `down -v`.

**Impacto:** o operador pode publicar acidentalmente o modo de desenvolvimento ou
acreditar que um volume local equivale a uma estratégia de recuperação. Falha do
host pode atingir aplicação, banco e backup ao mesmo tempo.

**Recomendação:** desenvolvimento deve ser explicitamente opt-in. O caminho de
produção precisa iniciar em `prod` ou falhar ao detectar `DEBUG=True`, host
irrestrito, segredo placeholder ou origem CSRF ausente. O backup deve ser
criptografado, versionado, enviado para destino externo e testado por restauração.
RPO/RTO precisam ser definidos por sistema antes do go-live.

## Gargalos de escalabilidade

### SC-01 — Custo operacional cresce linearmente por clone

Banco, autenticação, deploy, monitoramento, backup e suporte independentes são uma
boa fronteira de falha para quatro domínios, mas cobram operação por sistema. Na
fotografia atual, uma stack ociosa usa aproximadamente 176 MiB somando web e banco;
quatro stacks semelhantes partiriam de cerca de 700 MiB antes de carga, caches,
proxy, monitoramento e backups. A memória não é hoje o problema; a ausência de
automação e governança é.

**Melhoria:** padronizar provisioning, CI/CD, observabilidade, backup, inventário e
patch fan-out antes de aumentar a quantidade de sistemas.

### SC-02 — Identidade independente multiplica offboarding e revisão de acesso

Autenticação separada por sistema é uma decisão explícita, mas cria contas,
políticas e desligamentos repetidos. O template atual cobre autenticação e o gate
do admin; não define RBAC de domínio, recuperação de senha, MFA, revisão periódica
de acesso nem auditoria de leitura/exportação.

**Melhoria:** mesmo mantendo SSO fora da v1, definir um contrato de autorização por
papéis, owner de concessões, offboarding cross-system e trilha para exportações.
Preservar identificador externo imutável no modelo para uma federação futura. SSO
deve ser priorizado quando o custo de identidade duplicada superar a simplicidade
atual, e não apenas por calendário.

### SC-03 — Escrita de sessão e churn de conexão em toda requisição

[config/settings/base.py](config/settings/base.py#L97) usa
`SESSION_SAVE_EVERY_REQUEST=True`; `CONN_MAX_AGE` e `CONN_HEALTH_CHECKS` não estão
configurados. Cada requisição autenticada pode escrever sessão, e cada processo
abre/fecha conexões sem reutilização. Telas HTMX intensificam esse padrão.

**Melhoria:** desativar o save a cada request, atualizar timeout de inatividade de
forma limitada quando realmente necessário, habilitar conexões persistentes e
health checks, dimensionando o pool pelo total de workers de todos os sistemas.

### SC-04 — Migração no boot impede escala horizontal segura

[entrypoint.sh](entrypoint.sh#L4) executa `migrate` em todo processo web. Réplicas
iniciadas juntas competirão pelas migrações. O Gunicorn usa três workers fixos, sem
configuração de timeout, jitter, reciclagem ou graceful shutdown.

**Melhoria:** separar uma etapa única de release/migração do processo web e expor
configurações de concorrência. Calibrar por carga representativa, não por fórmula
genérica.

### SC-05 — Não há envelope de capacidade nem isolamento de recursos

Não existem limites de CPU/memória/PIDs no Compose, metas de latência, volume de
dados, concorrência, orçamento de queries ou teste de carga. Em host compartilhado,
um sistema pode virar noisy neighbor dos demais.

**Melhoria:** definir três perfis de capacidade (pequeno, médio e grande), com
usuários concorrentes, tamanho de tabela, p95/p99, queries por request, conexões e
memória. Aplicar limites por serviço e alertas antes de consolidar vários derivados
no mesmo host.

### SC-06 — Observabilidade é insuficiente para operar uma família

Não há logging estruturado, request ID, métricas, tracing, access log configurado,
alertas ou separação de liveness/readiness. [core/views.py](core/views.py#L22)
suprime a exceção do banco no `healthz` sem registrá-la.

**Melhoria:** logs estruturados em stdout, correlation ID, access log, métricas de
latência/erro/DB, `/livez` sem dependência e `/readyz` com banco. Centralizar painéis
e alertas com rótulo por sistema/ambiente/versão do template.

### SC-07 — Tabelas operacionais e históricas não têm retenção

Sessões, tentativas do Axes e tabelas do simple-history crescerão sem limite. O
histórico de usuário ainda recebe uma linha em logins, embora os campos sensíveis
tenham sido removidos. Não há rotina de `clearsessions`, retenção, arquivamento nem
monitoramento de tamanho.

**Melhoria:** políticas por classe de dado, limpeza agendada, arquivamento quando
necessário e teste de que escritas em massa não contornam a auditoria.

### SC-08 — O app de exemplo está prestes a ensinar padrões que degradam em dados grandes

O desenho da Fase 3 prevê `icontains` em título/descrição, paginação por `OFFSET` e
agregações completas a cada dashboard. Isso é correto para volume pequeno, mas pode
ensinar um padrão ruim sem declarar seu limite.

**Melhoria:** definir o envelope didático e demonstrar:

- índices para filtros e ordenações reais;
- `select_related` para autor e orçamento máximo de queries;
- trigram/full-text search quando o volume justificar;
- paginação por cursor para páginas profundas;
- cache, tabela resumida ou materialized view para agregações caras;
- teste com massa de dados suficiente para medir p95 e plano de consulta.

## Riscos imediatos da Fase 3

### P3-01 — Tailwind não examina templates dos apps

[tailwind.config.js](tailwind.config.js#L23) varre apenas
`core/templates/**/*.html` e o estágio de assets do
[Dockerfile](Dockerfile#L13) copia somente templates do `core`. Classes usadas
apenas em `apps/exemplo` serão eliminadas silenciosamente pelo build.

**Ação antes de implementar UI:** incluir templates de apps no conteúdo e no
estágio de build, com teste que procura no CSS uma classe exclusiva do app.

### P3-02 — O contrato de erro HTTP 422 está incompleto

O contexto/UI da Fase 3 afirma que formulário inválido retorna 422 e troca o modal.
O HTMX 1.9.12 vendorizado não faz swap de 4xx por padrão; o próprio login atual usa
HTTP 200 no erro por essa razão. Não há extensão ou handler `beforeSwap` planejado.

**Ação:** escolher e documentar um padrão único: erro de formulário em 200, ou 422
com handler testado que define `shouldSwap`. Sem isso, o modal parece não responder.

### P3-03 — “Autocontido e removível” contradiz os pontos de integração

ECharts em `core/static/vendor/` e edições diretas em settings, URLs e navegação
fazem o exemplo transbordar para o kernel. Removê-lo exigirá mudanças coordenadas e
deixará asset órfão.

**Ação:** manter assets do exemplo dentro do app ou declarar ECharts formalmente
como capacidade do kernel; automatizar um teste que remove o app e roda checks,
migrações e suíte.

### P3-04 — Decisões de UX e domínio foram auto-selecionadas

O contexto registra escolhas em modo `--auto` e o UI-SPEC ainda está em status
`draft`. Não há evidência de entrevista, teste de usabilidade ou validação com
operadores dos futuros sistemas.

**Ação:** validar com pelo menos um usuário de negócio e um mantenedor. O app de
exemplo deve ensinar problemas reais recorrentes — filtros, permissões, auditoria,
exportação e acessibilidade — e não apenas demonstrar componentes visualmente.

## Outros achados atuais

### Segurança e dados

- O `.env` local está com permissão `664`; em host multiusuário isso permite leitura
  de segredos pelo grupo. Padronizar `600` e verificar no runbook/deploy.
- A unicidade de e-mail é sensível a caixa. `normalize_email()` normaliza o domínio,
  não necessariamente o endereço inteiro. Definir canonicalização e constraint
  case-insensitive antes de haver bases reais.
- `AXES_IPWARE_PROXY_COUNT=2` está hard-coded. Parametrizar e testar a topologia
  real de proxies, incluindo spoofing de `X-Forwarded-For`.
- A auditoria cobre mudanças de modelo via `save`, mas não prova leitura,
  exportação, SQL bruto ou todas as operações em massa. O contrato precisa seguir
  a classificação dos dados de cada sistema.

### Entrega e cadeia de suprimentos

- Não há CI versionado no repositório; as 46 garantias dependem de execução manual.
- Dependências diretas Python estão pinadas, mas transitivas não têm lock/hashes.
- Tailwind é baixado por `npx` sem lockfile; imagens base usam tags mutáveis.
- Assets HTMX/Alpine vendorizados não possuem manifesto de versão, origem, licença
  e SHA-256 no repositório.
- Não há SBOM, scan automatizado da imagem ou rotina automatizada de atualização.

### Manutenção e operação

- `STATICFILES_DIRS` aponta para `core/static` embora o app finder já descubra esse
  diretório, gerando descoberta duplicada e ruído no `collectstatic`.
- O cache `static-v1` do service worker depende de bump manual; assets hasheados
  antigos podem acumular no navegador.
- `/app` inteiro pertence ao usuário de runtime. Manter fontes read-only e conceder
  escrita apenas a diretórios necessários melhora contenção.
- O container não possui limites e não há política para backups durante alteração
  de schema, rollback ou migração destrutiva.

## Modelo operacional proposto

### Papéis mínimos

| Papel | Responsabilidade |
|---|---|
| Sponsor da plataforma | Prioridade, orçamento e resultado institucional |
| Owner do template | Roadmap, versões, segurança e compatibilidade |
| Owner do sistema derivado | Requisitos, dados, acessos e aceite do domínio |
| Operação/SRE | Deploy, observabilidade, backup, restore e capacidade |
| Segurança/privacidade | Classificação de dados, threat model, acesso e retenção |

### Ciclo de vida

```text
Solicitação
  -> classificação de dados e SLA
  -> geração em versão suportada
  -> implementação somente em extension points
  -> CI + revisão + teste de carga proporcional
  -> restore drill
  -> go-live
  -> inventário e patch automatizado
  -> atualização periódica
  -> desativação e descarte controlado
```

### Scorecard de valor proposto

| Métrica | Meta inicial sugerida |
|---|---|
| Geração limpa + suíte | 100% em CI |
| Tempo até sistema navegável | medir baseline; alvo de até 1 dia útil para o ciclo completo |
| Atualização N→N+1 sem conflito | ≥ 95%; ideal 100% em arquivos do kernel |
| Derivados em versão suportada | 100% |
| Propagação de patch crítico | ≤ 48 horas |
| Restore testado | trimestral e antes do primeiro go-live |
| Sistemas com owner/RPO/RTO/classificação registrados | 100% |
| Incidentes causados por drift do template | 0 |
| p95 de listagem/dashboard | definir após massa e fluxo reais; medir continuamente |

As metas são propostas para discussão; RPO, RTO, disponibilidade e latência devem
ser aprovados pelos responsáveis de negócio e operação.

## Ordem recomendada de execução

### P0 — antes de multiplicar

1. Reclassificar o Sistema Base formalmente como produto de plataforma interna.
2. Nomear owners e criar o inventário de derivados.
3. Definir fronteira upstream-owned versus derivative-owned.
4. Corrigir o contrato da Fase 3: Tailwind, 422 e localização do ECharts.
5. Definir RBAC, classificação de dados, auditoria e política de retenção mínimas.

### P1 — antes do primeiro go-live

1. Criar o template Copier e o teste N→N+1 sem conflito.
2. Tornar produção fail-safe e desenvolvimento opt-in.
3. Implantar CI, locks/hashes, scan e manifesto de assets.
4. Implementar backup externo e provar restauração.
5. Adicionar logs, métricas, request ID, readiness e alertas.
6. Separar migração do boot do web e parametrizar Gunicorn.
7. Criar README/runbook completo.

### P2 — piloto do Orçamento

1. Gerar a partir de checkout limpo.
2. Registrar tempo, passos manuais e conflitos.
3. Exercitar massa representativa e teste de carga.
4. Validar UX com usuários e operação com mantenedores.
5. Executar restore em host separado.
6. Atualizar o piloto para uma nova versão do template antes de autorizar os demais.

### P3 — escala da família

1. Automatizar PRs de atualização e dashboard de drift.
2. Aplicar perfis de capacidade e limites por stack.
3. Centralizar observabilidade e gestão de incidentes.
4. Reavaliar SSO quando offboarding e suporte duplicado virarem custo dominante.
5. Somente então considerar componentes compartilhados adicionais.

## Critérios de liberação

O projeto pode ser considerado apto a gerar o primeiro sistema de produção quando:

- o fluxo `copier copy` completo passa em CI a partir de ambiente limpo;
- a atualização N→N+1 foi provada sem conflito em customização real;
- nenhum desenvolvimento de domínio exige editar arquivos upstream-owned;
- settings de produção são o caminho seguro e validado;
- backup externo e restore foram executados com RPO/RTO medidos;
- há RBAC, owner de acesso, retenção e classificação de dados definidos;
- observabilidade e alertas estão ativos;
- a suíte, o check de deploy e o teste de carga do perfil escolhido passam;
- o sistema está registrado com owner e versão do template;
- o piloto foi aceito por usuário de negócio e operador.

## Conclusão

A engenharia entregue nas Fases 1 e 2 é consistente e merece ser preservada. O
projeto não precisa de uma arquitetura mais sofisticada; precisa transformar um
bom repositório-modelo em um **produto de plataforma operável**.

O melhor investimento agora é proteger a atualização dos clones, automatizar o
ciclo de vida e provar o valor no primeiro derivado. Se esses pontos forem
resolvidos antes da multiplicação, o Sistema Base pode reduzir custo e risco de
forma real. Se forem adiados, ele tende a criar quatro sistemas visualmente
consistentes, mas operacionalmente divergentes.
