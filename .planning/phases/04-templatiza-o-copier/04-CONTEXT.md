# Phase 4: Templatização Copier - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning

<domain>
## Phase Boundary

O sistema-modelo executável vira template Copier: tudo que difere entre sistemas (nome, sigla, slug, hostname/subdomínio, porta interna, nome do banco, cor primária) vira variável de template; `copier copy` gera um sistema novo autocontido e `copier update` puxa evoluções do núcleo em sistemas já gerados; `ops/` entrega backup containerizado, retenção, ensaio de restore, vhost nginx de exemplo e runbook de migração — tudo extraído da PCA e generalizado.

Requisitos cobertos: TPL-01, TPL-02, TPL-03, TPL-04, INF-03, INF-04.

Fora desta fase: verificação ponta a ponta do fluxo de nascimento e README completo com suíte passando no sistema gerado (Fase 5 — QA-01, QA-02, DOC-01); construção do sistema Orçamento (primeiro uso real, projeto próprio); SSO e integrações externas.

</domain>

<decisions>
## Implementation Decisions

*(Discussão interativa: 4 áreas, 28 decisões. Numeração continua de D-36 da Fase 3.)*

### Estrutura do repositório do template (TPL-01)
- **D-37:** Templatização **in-place na raiz**: `copier.yml` na raiz do repo, sufixo `.jinja` apenas nos arquivos que precisam de interpolação. O repo deixa de rodar diretamente — a partir desta fase, a validação do sistema é sempre via `copier copy` (exatamente o que a Fase 5/QA-02 exercitará). Coerente com D-01 (templatização como transformação mecânica final).
- **D-38:** Artefatos de desenvolvimento do template (`.planning/`, `CLAUDE.md`, `IDEIA.md`, `REVIEW.md`, `__pycache__` e afins) entram no `_exclude` do `copier.yml` — ficam no repo do template e nunca chegam ao sistema gerado.
- **D-39:** **Dois READMEs**: `README.md` na raiz é a documentação do template (nascimento de um sistema, do `copier copy` ao proxy/DNS — base do DOC-01; entra no `_exclude`); `README.md.jinja` gera o README do sistema (operação, convenções, remoção do app exemplo) com o nome do sistema interpolado.
- **D-40:** Pós-geração **sem automatismo**: nenhum `_tasks` no `copier.yml`. O README do template documenta os passos manuais do nascimento: `git init` + primeiro commit (incluindo `.copier-answers.yml`, pré-requisito do `copier update`).

### Variáveis, defaults e validação (TPL-02)
- **D-41:** Perguntas **mínimas com defaults derivados**: o `copier copy` pergunta tudo, mas com defaults inteligentes — slug derivado do nome, banco = slug, hostname default `{slug}.exemplo.gov.br`, porta com default, sigla derivada das iniciais do nome. Operador aceita Enter no caso comum e sobrescreve quando quiser.
- **D-42:** **Validators no `copier.yml`** para cada resposta: cor primária `#RRGGBB` (regex), slug no formato permitido, porta 1024–65535. Erro aparece no `copier copy`, antes de existir código; a validação de boot da Fase 2 (`ImproperlyConfigured`) permanece como segunda barreira.
- **D-43:** Slug restrito a **`[a-z0-9]` sem separadores** (ex.: `orcamento`, `financeiro`, `dividaativa`) — válido simultaneamente como nome de banco PostgreSQL, rótulo DNS e nome de diretório, sem conversões. É o padrão real da família.
- **D-44:** Subdomínio perguntado como **hostname completo** em uma única variável (ex.: `orcamento.cfc.org.br`) — alimenta o `server_name` do vhost nginx e os defaults de produção do `.env.example`. O template não assume domínio-base fixo.
- **D-45:** Porta interna: pergunta com default 8000 + **tabela de alocação da família mantida no README do template** (ex.: PCA 8001, Orçamento 8002...) como convenção documentada, não imposta.
- **D-46:** `SISTEMA_SIGLA` vira variável Copier com default derivado das iniciais do nome.
- **D-47:** Cor primária: pergunta aberta em hex `#RRGGBB` com validator, default `#1e40af` (azul atual).
- **D-48:** **Segredos nunca passam pelo Copier** (o `.copier-answers.yml` é commitado no repo gerado): `SECRET_KEY` e senha do banco continuam placeholders no `.env.example`; o README documenta o comando de geração (`python -c "import secrets; ..."`) como passo do preenchimento do `.env`.
- **D-49:** `.env.example` gerado **pré-preenchido** via `.env.example.jinja`: `POSTGRES_DB`/`POSTGRES_USER`/`DATABASE_URL` com o slug, `WEB_PORT` com a porta, `SISTEMA_NOME`/`SISTEMA_SIGLA`/`COR_PRIMARIA` com as respostas, e `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` com o hostname real de produção indicado em comentário. Preencher o `.env` vira essencialmente só segredos.
- **D-50:** Princípio **".env primeiro, .jinja mínimo"**: valor consumido em runtime vem do `.env` (o arquivo de código fica idêntico para todos os sistemas); só vira `.jinja` o que o `.env` não alcança — `tailwind.config.js` (cor resolvida em build, D-17), `.env.example` (defaults), READMEs, vhost nginx, `copier.yml`. Menos arquivos templatizados = menos conflitos no `copier update`. Ocorrências literais de `sistema_base`/porta em `config/settings/base.py`, `entrypoint.sh` e `seed_exemplo.py` são resolvidas preferencialmente via `.env`/neutralização, não via jinja.
- **D-51:** `compose.yml` gerado fixa **`name: {slug}`** — isolamento de containers/rede/volume garantido pela identidade do sistema, independente do nome do diretório de destino escolhido no `copier copy`.
- **D-52:** Ícones PWA: o gerado herda os placeholders neutros (D-20) e o README lista rodar `ops/gerar_icones_pwa.py` (que lê sigla/cor do `.env`) como passo opcional do nascimento — coerente com D-40 (zero automatismo pós-geração).

### Estratégia copier update (TPL-03)
- **D-53:** Versionamento do template por **tags semver** (`v0.1.0`, `v0.2.0`...): `copier copy`/`update` ancoram na última tag estável; evoluções do núcleo só chegam aos sistemas quando conscientemente tageadas. O ritual de release é documentado no README do template.
- **D-54:** Variável booleana **`incluir_app_exemplo`** (default: sim) gera condicionalmente `apps/exemplo/` e seus 3 pontos de acoplamento (D-34: settings, urls, `_nav.html`). Ao remover o exemplo, o operador troca a resposta para "não" no update e o app removido nunca é ressuscitado por updates futuros.
- **D-55:** Conflitos de update apresentados como **marcadores inline** estilo git (`<<<<<<<`/`>>>>>>>`) — modo padrão do Copier moderno; fluxo de resolução documentado.
- **D-56:** O `copier update` é **provado dentro da Fase 4** com ensaio roteirizado: `copier copy` na tag A → mudança no núcleo → tag B → `copier update` → verificar que a mudança chegou e que o exemplo removido não voltou. O roteiro fica registrado no README do template; a Fase 5 repete apenas o fluxo de nascimento.

### ops/ — backup, nginx e migração (INF-03, INF-04)
- **D-57:** Backup no **padrão PCA completo**, extraído de `/opt/web/pca/ops/backup/` e generalizado: backup containerizado (Dockerfile + `backup.sh`), retenção (`retencao.sh`) e ensaio de restore local.
- **D-58:** Backup entra como **serviço no `compose.yml`** do sistema gerado (padrão PCA): sobe junto com o sistema, agenda própria, zero dependência do host — preserva a invariante de portabilidade (migração = dump + `.env` + `compose up`).
- **D-59:** Destino dos dumps e política de retenção **iguais aos da PCA** (defaults generalizados do `retencao.sh`); armazenamento offsite fica a cargo de cada sistema.
- **D-60:** Horário e knobs do backup **configuráveis via `.env`** com defaults iguais aos da PCA (aplica D-50) — ajustar agenda não exige editar script (nem gera conflito de update).
- **D-61:** Vhost nginx gerado **interpolado e pronto para copiar**: `ops/nginx/{slug}.conf` com `server_name` (hostname real) e `proxy_pass http://127.0.0.1:{porta}` preenchidos, extraído do `pca.conf` generalizado.
- **D-62:** O vhost **espelha o `pca.conf` de produção incluindo TLS**: HTTPS na 443, redirect HTTP→HTTPS, caminhos de certificado generalizados — operador só aponta o certificado do seu domínio.
- **D-63:** `MIGRACAO.md` da PCA **generalizado e incluído em `ops/`** do sistema gerado — runbook de migração de host e prova documental do INF-04.
- **D-64:** Ensaio de restore: script generalizado **+ rotina documentada** recomendando execução periódica (após mudanças grandes e em cadência regular) — o gerado nasce com a disciplina, não só com a ferramenta.

### Claude's Discretion
- Nomes exatos das variáveis no `copier.yml` (em pt-BR, coerentes com o vocabulário do projeto) e textos das perguntas.
- Lista exata do `_exclude` além dos artefatos citados em D-38 (ex.: `.git`, caches, artefatos de build).
- Detalhes da derivação jinja dos defaults (filtros para slug/sigla) e mensagens de erro dos validators.
- Recorte fino do `ops/backup/` da PCA (quais scripts auxiliares de teste entram) e generalização dos textos.
- `_min_copier_version` e demais chaves técnicas do `copier.yml`.
- Como marcar a condicional `incluir_app_exemplo` nos 3 pontos de acoplamento (jinja `{% if %}` por bloco vs arquivos condicionais).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fonte de extração (somente leitura — NUNCA modificar)
- `/opt/web/pca/ops/backup/` — `Dockerfile`, `backup.sh`, `retencao.sh`, `ensaio_restore_local.sh`, `testar_retencao.sh`: padrão de backup containerizado, retenção e ensaio de restore a generalizar (D-57..D-60, D-64)
- `/opt/web/pca/ops/nginx/pca.conf` — vhost de produção com TLS a generalizar para `ops/nginx/{slug}.conf.jinja` (D-61, D-62)
- `/opt/web/pca/ops/MIGRACAO.md` — runbook de migração de host a generalizar (D-63)
- `/opt/web/pca/compose.yml` — como o serviço de backup se integra ao compose em produção (D-58)

### Arquivos do template a templatizar/tocar (Fase 4)
- `.env.example` — vira `.env.example.jinja` com defaults interpolados (D-49); comentários existentes já anunciam "virará variável Copier na Fase 4"
- `tailwind.config.js` — vira `.jinja`; único hex de marca na linha `const COR_PRIMARIA` (D-17/D-50)
- `compose.yml` — ganha `name: {slug}` (D-51) e o serviço de backup (D-58)
- `config/settings/base.py`, `entrypoint.sh`, `apps/exemplo/management/commands/seed_exemplo.py` — ocorrências literais de `sistema_base`/`Sistema Base`/porta a resolver via princípio D-50
- `config/settings/base.py`, `config/urls.py`, `core/templates/core/_nav.html` — 3 pontos de acoplamento do `apps/exemplo` que recebem a condicional `incluir_app_exemplo` (D-34/D-54)
- `ops/gerar_icones_pwa.py` — script existente referenciado no passo opcional de ícones (D-52)
- `apps/exemplo/README.md` — protocolo de remoção em 4 passos, a reconciliar com a condicional D-54

### Documentos do projeto
- `.planning/PROJECT.md` — invariantes (portabilidade, segurança, zero menção a PCA/domínio) e restrições (stack fechada, mecanismo Copier)
- `.planning/REQUIREMENTS.md` — TPL-01..TPL-04, INF-03, INF-04
- `.planning/phases/03-app-exemplo/03-CONTEXT.md` — D-33..D-35 (isolamento e pontos de acoplamento do exemplo)
- `.planning/phases/02-shell-visual-e-kernel/02-CONTEXT.md` — D-16/D-17 (dois touchpoints de identidade), D-20 (ícones placeholder)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Valores de identidade já concentrados: `.env.example` (nome, sigla, cor, porta, banco) + um único hex em `tailwind.config.js` — o trabalho das Fases 1–2 deixou a superfície de templatização mínima por construção.
- `ops/gerar_icones_pwa.py` já existe no repo (regenera ícones a partir de sigla/cor).
- `compose.yml` já usa interpolação de env (`${POSTGRES_DB}`, `${WEB_BIND_ADDRESS:-127.0.0.1}`) — o serviço de backup segue o mesmo padrão.

### Established Patterns
- Comentários em pt-BR explicando o porquê (estilo da casa — manter no `copier.yml`, scripts de ops e READMEs).
- Valores parametrizáveis concentrados em settings/`.env` (D-16/D-17) — o princípio D-50 é a extensão natural.
- App escuta só em `127.0.0.1` com default seguro no compose (WR-02) — o vhost nginx gerado aponta para essa porta.

### Integration Points
- `copier.yml` na raiz é o novo ponto de entrada do repositório (o repo passa a ser template, não sistema executável).
- `compose.yml` ganha o serviço de backup (terceiro serviço, ao lado de `web`+`db`).
- Os 3 pontos de acoplamento do `apps/exemplo` (settings, urls, `_nav.html`) ganham a condicional `incluir_app_exemplo`.
- A Fase 5 consumirá: o fluxo `copier copy` → `.env` → `compose up` → `migrate` → `createsuperuser` e o README do template (DOC-01 é da Fase 5, mas o esqueleto do README nasce aqui).

</code_context>

<specifics>
## Specific Ideas

- O nascimento de um sistema deve ser transparente e sem mágica: nenhum `_tasks`, nenhum segredo gerado automaticamente — cada passo manual está no README, na ordem, do `copier copy` ao proxy/DNS.
- A família opera igual: mesmo backup, mesma retenção, mesmo runbook de migração da PCA, generalizados — quem sabe operar a PCA sabe operar qualquer sistema gerado.
- Critério operacional da fase: `copier copy` responde perguntas e gera projeto completo; ensaio de update (tag A → tag B) aplicado com sucesso sem ressuscitar o exemplo removido; nada que difira entre sistemas hard-coded no gerado; zero menção a PCA/domínio.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 4-Templatização Copier*
*Context gathered: 2026-08-18*
