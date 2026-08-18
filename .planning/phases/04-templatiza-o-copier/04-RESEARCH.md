# Fase 4: Templatização Copier — Pesquisa

**Pesquisado em:** 2026-08-18  
**Domínio:** Template de projeto Django com Copier, atualização por Git e operação containerizada  
**Confiança:** MÉDIA — o comportamento do Copier foi conferido na documentação oficial atual; a execução ponta a ponta ainda depende de instalar o CLI nesta máquina.

<user_constraints>
<!-- DATA_4RkP8aZx_START -->
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### the agent's Discretion
- Nomes exatos das variáveis no `copier.yml` (em pt-BR, coerentes com o vocabulário do projeto) e textos das perguntas.
- Lista exata do `_exclude` além dos artefatos citados em D-38 (ex.: `.git`, caches, artefatos de build).
- Detalhes da derivação jinja dos defaults (filtros para slug/sigla) e mensagens de erro dos validators.
- Recorte fino do `ops/backup/` da PCA (quais scripts auxiliares de teste entram) e generalização dos textos.
- `_min_copier_version` e demais chaves técnicas do `copier.yml`.
- Como marcar a condicional `incluir_app_exemplo` nos 3 pontos de acoplamento (jinja `{% if %}` por bloco vs arquivos condicionais).

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
<!-- DATA_4RkP8aZx_END -->
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Descrição | Suporte da pesquisa |
|---|---|---|
| TPL-01 | Gerar projeto Django com `copier copy` e perguntas | `copier.yml` in-place, perguntas tipadas/validadas, pares `.jinja` e exclusões explícitas. |
| TPL-02 | Parametrizar nome, slug, hostname, porta, banco e cor | `.env.example.jinja` é a fonte do runtime; somente Tailwind, README, nginx e configuração Copier interpolam. |
| TPL-03 | Atualizar núcleo com `copier update` | Arquivo de respostas, tags PEP 440, repositórios Git limpos e ensaio A→B obrigatório. |
| TPL-04 | Zero menção a PCA/domínio no gerado | Varredura do destino e generalização dos artefatos de ops e documentação. |
| INF-03 | `ops/` com backup e nginx | Serviço `backup` no Compose, scripts portáveis, retenção/restore e vhost TLS interpolado. |
| INF-04 | Loopback e migração portátil | Bind de host em `127.0.0.1`, vhost para loopback e runbook dump + `.env` + Compose + proxy/DNS. |
</phase_requirements>

## Resumo

Implemente o template na raiz atual, preservando arquivos sem interpolação e renomeando apenas os que precisam ser renderizados para `*.jinja`. O Copier usa `copier.yml` na raiz, recebe perguntas como respostas disponíveis durante a renderização e aceita `default`/`validator` Jinja; um validator deve não renderizar nada quando a resposta é válida. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

O contrato de atualização precisa nascer junto com o primeiro sistema: template Git com tags PEP 440, projeto gerado também versionado, e `.copier-answers.yml` commitado. O `copier update` gera versões temporárias antiga/nova, calcula e reaplica a diferença local; por isso valores que são configuração pertencem ao `.env`, não a muitos arquivos Jinja. [CITED: https://copier.readthedocs.io/en/stable/updating/]

**Recomendação principal:** criar primeiro um tracer de `copier copy` com todas as variáveis e exclusões, depois completar `ops/` e provar o update por tags, incluindo a desativação permanente do app exemplo.

## Mapa de Responsabilidades Arquiteturais

| Capacidade | Camada primária | Camada secundária | Justificativa |
|---|---|---|---|
| Perguntas, defaults, renderização e respostas | Ferramenta de desenvolvimento / template | Git | Copier produz arquivos; Git fornece a versão que o update compara. [CITED: https://copier.readthedocs.io/en/stable/updating/] |
| Identidade e conexão por sistema | Configuração do runtime | Build de assets | `.env` alimenta Django/Compose; Tailwind precisa da cor durante o build. [VERIFIED: .env.example:30-65; tailwind.config.js:3-6] |
| App exemplo opcional | Template / sistema de arquivos | Configuração Django | Diretório e três referências só existem quando a resposta booleana é verdadeira. [VERIFIED: config/settings/base.py:23-38; config/urls.py:7-15; core/templates/core/_nav.html:22-58] |
| Backup e retenção | Serviço Docker | Armazenamento remoto | O container agenda `pg_dump`; o armazenamento offsite é configurado por ambiente. [VERIFIED: /opt/web/pca/compose.yml:56-85; /opt/web/pca/ops/backup/backup.sh:1-28] |
| Entrada HTTPS | Nginx do host | Serviço web no loopback | Nginx termina TLS e encaminha somente para a porta ligada a `127.0.0.1`. [VERIFIED: /opt/web/pca/ops/nginx/pca.conf:18-50] |

## Stack Padrão

### Núcleo

| Ferramenta | Versão | Uso | Motivo |
|---|---:|---|---|
| `copier` | 9.17.1 disponível no índice PyPI | Renderizar e atualizar o template | É o mecanismo travado do projeto; a documentação oficial cobre perguntas, respostas e atualização. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| Git | 2.53.0 disponível | Versionar template e derivados; tags de release | O fluxo de update recomendado requer template e destino versionados; as tags são comparadas como PEP 440. [CITED: https://copier.readthedocs.io/en/stable/updating/] |
| Docker Compose | v5.1.4 disponível | Executar web, PostgreSQL e backup | Mantém o backup agendado dentro da stack e a operação sem cron do host. [VERIFIED: compose.yml:1-51; /opt/web/pca/compose.yml:56-85] |

### Sem novas dependências de aplicação

Não alterar `requirements.txt`: a fase adiciona um CLI de desenvolvimento, não uma biblioteca de runtime Django. A retenção e a leitura de `.env` do gerador de ícones devem usar shell/Python padrão ou dependências já presentes; não introduzir extensão Jinja. Extensões Jinja tornam o template potencialmente inseguro e exigem instalação adicional no mesmo ambiente do Copier. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

## Auditoria de Legitimidade de Pacotes

| Pacote | Registro | Versão conferida | Veredito | Disposição |
|---|---|---:|---|---|
| `copier` | PyPI | 9.17.1 | SUS — a consulta de legitimidade marcou publicação recente/sem metadados de repositório | Obrigatório por decisão do projeto, mas instalar somente após checkpoint humano; preferir ambiente isolado e versão explicitamente pinada. [VERIFIED: PyPI via `pip index versions copier`, 2026-08-18] |

**Pacotes removidos por SLOP:** nenhum.  
**Pacotes suspeitos:** `copier`; o planejador deve inserir `checkpoint:human-verify` antes de qualquer instalação. A máquina atual não tem `copier`, `pipx` nem `uv` no `PATH`; Docker, Git, Nginx e rclone estão disponíveis. [VERIFIED: auditoria de ambiente, 2026-08-18]

## Padrões de Arquitetura

### Fluxo de geração e atualização

```text
template Git (tag v0.x.y)
  └─ copier.yml + arquivos .jinja + arquivos estáticos
       └─ copier copy
            ├─ perguntas/validators → .copier-answers.yml
            └─ projeto gerado + .env.example + ops/
                 └─ git init + primeiro commit
                      └─ copier update (tag posterior)
                           ├─ aplica diff do núcleo
                           └─ conflitos inline → revisar → testar → commit
```

O arquivo de respostas deve existir como `.copier-answers.yml.jinja` na raiz do template e renderizar `_copier_answers`; ele guarda a referência `_commit` automaticamente. Não o edite manualmente. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

### `copier.yml` prescritivo

Use `_min_copier_version: "9.17.1"`, `_envops.undefined: jinja2.StrictUndefined`, `_templates_suffix: .jinja` e um `_exclude` completo. `StrictUndefined` transforma variável esquecida em erro de renderização; ao declarar `_exclude`, inclua também as exclusões padrão que ainda são necessárias, pois uma lista própria substitui o default do Copier. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

Perguntas recomendadas: `sistema_nome`, `sistema_slug`, `sistema_hostname`, `sistema_porta`, `sistema_banco`, `sistema_sigla`, `cor_primaria` e `incluir_app_exemplo`. Aplique `type: int` à porta; para slug use regex que aceite apenas `[a-z0-9]+`; para cor use `^#[0-9a-fA-F]{6}$`; para hostname aceite somente nome DNS sem esquema, caminho ou porta. O default de banco é `{{ sistema_slug }}`, hostname `{{ sistema_slug }}.exemplo.gov.br`, sigla derivada do nome e cor `#1e40af`. Validators são templates Jinja que devem produzir a mensagem de erro somente quando inválidos. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

O `_exclude` precisa conter, no mínimo, `copier.yml`, `.git`, `.planning`, `CLAUDE.md`, `IDEIA.md`, `REVIEW.md`, `README.md` (o do template), `__pycache__`, `*.py[co]`, `.env`, `staticfiles`, `core/static/dist`, `.venv`, caches e artefatos de editor. Os padrões são avaliados contra o destino; não depender das exclusões default após declarar a chave. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

### Arquivos que precisam mudar

| Arquivo atual | Resultado de Fase 4 | Decisão de implementação |
|---|---|---|
| `copier.yml` | novo | Perguntas, validators, exclusões, resposta pós-copy/update; não declarar `_tasks` ou migrations. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| `.copier-answers.yml.jinja` | novo | Persistir `_copier_answers` e metadados de update. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| `.env.example` | `.env.example.jinja` | Preencher identidade, banco, hostname e porta; manter somente placeholders para segredos. [VERIFIED: .env.example:1-65] |
| `tailwind.config.js` | `tailwind.config.js.jinja` | Interpolar somente a constante de cor necessária no build. [VERIFIED: tailwind.config.js:3-6] |
| `compose.yml` | `compose.yml.jinja` | Fixar `name: {{ sistema_slug }}` e adicionar backup; manter o bind seguro de host. [VERIFIED: compose.yml:19-51] |
| `config/settings/base.py` | `*.jinja` somente pelos blocos condicionais | Remover defaults de identidade do código e condicionar a entrada de exemplo. [VERIFIED: config/settings/base.py:23-38; config/settings/base.py:145-161] |
| `config/urls.py` | `config/urls.py.jinja` | Condicionar apenas o include de exemplo. [VERIFIED: config/urls.py:7-15] |
| `_nav.html` | `_nav.html.jinja` | Condicionar as duas URLs e os dois links de exemplo. [VERIFIED: core/templates/core/_nav.html:22-58] |
| `apps/exemplo/` | diretório condicional | Renderizar o diretório somente quando `incluir_app_exemplo` for verdadeiro. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| `README.md` e `README.md.jinja` | novos | Separar instrução do template da documentação do sistema gerado. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| `ops/` | expandido | Gerar backup, nginx e migração sem texto/identificador de domínio. |

Os três acoplamentos existentes são, literalmente: `"apps.exemplo.apps.ExemploConfig",`, `path("exemplo/", include("apps.exemplo.urls")),`, e as URLs `{% url 'exemplo:dashboard' as url_exemplo_dash %}` / `{% url 'exemplo:item_listar' as url_exemplo_crud %}`. [VERIFIED: config/settings/base.py:23-38; config/urls.py:7-15; core/templates/core/_nav.html:22-58]

**Escolha para a condicional:** use um diretório com nome Jinja condicional para `apps/exemplo/` e blocos `{% if incluir_app_exemplo %}` nos três arquivos de acoplamento, todos com sufixo `.jinja`. O sufixo deve ficar fora da expressão do nome do arquivo condicional; caso contrário o Copier o copia literalmente sem renderizar. [CITED: https://copier.readthedocs.io/en/latest/configuring/]

### Neutralização obrigatória de valores atuais

Hoje o settings contém literalmente `SISTEMA_NOME = env("SISTEMA_NOME", default="Sistema Base")`, `SISTEMA_SIGLA = env("SISTEMA_SIGLA", default="SB")` e `COR_PRIMARIA = env("COR_PRIMARIA", default="#1e40af")`. [VERIFIED: config/settings/base.py:145-151]

Converta-os em leituras obrigatórias do `.env`, mantendo a validação `re.fullmatch(r"#[0-9a-fA-F]{6}", COR_PRIMARIA)`. Troque também os defaults de cor/sigla de `ops/gerar_icones_pwa.py` por leitura explícita de `.env`, e o fallback `default:'#1e40af'` do dashboard por `cor_primaria` já obrigatório. Assim o único default de identidade fica no `copier.yml`/`.env.example.jinja`, nunca no código gerado. [VERIFIED: ops/gerar_icones_pwa.py:8-13; ops/gerar_icones_pwa.py:60-72; apps/exemplo/templates/exemplo/dashboard.html:106]

O `entrypoint.sh` atualmente executa `gunicorn ... --bind 0.0.0.0:8000`; o isolamento de host já é garantido pela publicação Compose `"${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000"`. Mantenha o processo interno separado do bind do host e documente que `sistema_porta` preenche `WEB_PORT` e o `proxy_pass`; não introduza uma segunda porta sem necessidade. [VERIFIED: entrypoint.sh:1-5; compose.yml:29-36]

### `copier update` e arquivos opcionais

O update ideal requer `.copier-answers.yml`, tags Git no template, Git no destino e `git status` limpo. Tags são ordenadas por PEP 440; logo `v0.1.0`, `v0.1.1` e `v0.2.0` são a convenção adequada. O padrão de conflito é inline; documentar busca de `<<<<<<<`, `=======`, `>>>>>>>`, resolução, teste e commit. [CITED: https://copier.readthedocs.io/en/stable/updating/]

Não usar `_skip_if_exists` para `apps/exemplo`: caminhos removidos pelo usuário de um projeto gerado são excluídos automaticamente dos updates, mas `_skip_if_exists` tenta garantir a presença do caminho e quebraria D-54. A confirmação deve ser uma prova automatizável com `copier update --defaults --data incluir_app_exemplo=false`, seguida por outro update de núcleo verificando que `apps/exemplo/` e seus três acoplamentos continuam ausentes. [CITED: https://copier.readthedocs.io/en/stable/updating/]

## Operação: backup, Nginx e migração

### Backup generalizado

Traga `Dockerfile`, `backup.sh`, `retencao.sh`, `testar_retencao.sh` e um **novo** `ensaio_restore_local.sh` genérico. O Dockerfile PCA usa `postgres:17-alpine`, instala `curl unzip dcron tzdata`, baixa rclone pinado com checksum e executa cron em foreground. [VERIFIED: /opt/web/pca/ops/backup/Dockerfile:1-48]

O script de backup deve preservar `pg_dump --format=custom`, envio para `daily/`, cópia semanal no domingo e retenção padrão 7 diários/4 semanais. Generalize o prefixo do dump de `pca` para a variável de slug e exponha horário, retenções e dia semanal via `.env`; implemente um entrypoint do backup que valida os valores numéricos/horário antes de escrever o crontab, evitando que uma variável de ambiente vire código shell. [VERIFIED: /opt/web/pca/ops/backup/backup.sh:1-28; /opt/web/pca/ops/backup/retencao.sh:1-27]

Inclua no `compose.yml.jinja` o serviço `backup` com `init: true`, dependência do healthcheck de `db`, conexão interna `DB_HOST=db` e credenciais/R2 vindas do `.env`. O `init: true` é necessário no padrão PCA para o `dcron` não entrar em crash loop por `setpgid`. [VERIFIED: /opt/web/pca/compose.yml:56-85]

Não copie o ensaio PCA literalmente: ele contém imagem, prefixos Docker e modelos de domínio específicos. O ensaio novo deve usar recursos descartáveis com o slug do sistema, restaurar um dump customizado em banco isolado, executar `migrate --plan`, `migrate --noinput` e `manage.py check`, e limpar somente recursos que ele próprio criou. [VERIFIED: /opt/web/pca/ops/backup/ensaio_restore_local.sh:20-129]

**Conflito resolvido:** o PCA usa volume externo e exige `docker volume create` antes do Compose, mas isso viola o fluxo explícito de INF-04, que não admite passo adicional de host. Para o template, mantenha o volume gerenciado pelo Compose e deixe `name: {{ sistema_slug }}` isolar o volume/nome da stack; backup completo não exige volume externo. [VERIFIED: /opt/web/pca/compose.yml:87-106; VERIFIED: compose.yml:45-51]

### Nginx e runbook

Crie `ops/nginx/{{ sistema_slug }}.conf.jinja` com `server_name {{ sistema_hostname }}`, `proxy_pass http://127.0.0.1:{{ sistema_porta }}`, bloco TLS 443, certificados Let's Encrypt do hostname e redirect HTTP→HTTPS. Preserve `Host`, `X-Real-IP`, `X-Forwarded-For` e `X-Forwarded-Proto` definidos pelo Nginx, nunca repassados do cliente. [VERIFIED: /opt/web/pca/ops/nginx/pca.conf:18-50]

Generalize `ops/MIGRACAO.md.jinja`: instalar Docker/Compose, Nginx, Certbot e rclone; copiar `.env.example`; preencher novos segredos; restaurar dump com `pg_restore --clean --if-exists --no-owner`; subir Compose; conferir `/healthz`; instalar vhost; validar `nginx -t`; obter certificado e configurar DNS. Remova todas as referências a projetos, imagens, modelos, buckets, volumes e incidentes específicos da PCA. [VERIFIED: /opt/web/pca/ops/MIGRACAO.md:9-145; /opt/web/pca/ops/MIGRACAO.md:298-333]

## Não Construir Manualmente

| Problema | Não construir | Usar | Motivo |
|---|---|---|---|
| Merge de evolução do template | Script próprio que copia/sobrescreve arquivos | `copier update` + Git | O algoritmo compara projeto gerado, versão antiga e versão nova; tratar conflitos manualmente é parte do contrato. [CITED: https://copier.readthedocs.io/en/stable/updating/] |
| Persistência das respostas | YAML escrito à mão | `.copier-answers.yml.jinja` com `_copier_answers` | Alterar o arquivo manualmente invalida as premissas do diff inteligente. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| Backup PostgreSQL | Dump SQL textual ou cron do host | `pg_dump --format=custom` no serviço backup | Permite restore via `pg_restore` e preserva portabilidade. [VERIFIED: /opt/web/pca/ops/backup/backup.sh:10-28; /opt/web/pca/ops/MIGRACAO.md:104-120] |
| Retenção | Lógica duplicada em backup/teste | `retencao.sh` carregado pelos dois scripts | A mesma função ordena objetos por data real e poda excedentes. [VERIFIED: /opt/web/pca/ops/backup/retencao.sh:1-27] |

## Armadilhas Comuns

1. **Sobrescrever exclusões default.** Declarar `_exclude` sem repetir `.git`, `__pycache__` e `copier.yml` faz esses artefatos escaparem para o destino. [CITED: https://copier.readthedocs.io/en/latest/configuring/]
2. **Usar `.jinja` errado em caminho condicional.** O sufixo precisa estar fora do `{% if %}` no nome de arquivo; diretórios não terminam com o sufixo. [CITED: https://copier.readthedocs.io/en/latest/configuring/]
3. **Editar respostas.** Alterar `.copier-answers.yml` manualmente torna o update imprevisível; mudar uma resposta pelo próprio `copier update --data`. [CITED: https://copier.readthedocs.io/en/stable/updating/]
4. **Criar `_tasks` ou extensões.** Além de contrariar D-40, tasks/migrations/extensões são recursos inseguros que exigem confiança explícita no Copier. [CITED: https://copier.readthedocs.io/en/latest/configuring/]
5. **Ressuscitar o exemplo.** Não usar `_skip_if_exists`; provar a sequência false → atualização posterior. [CITED: https://copier.readthedocs.io/en/stable/updating/]
6. **Copiar o restore PCA.** Ele contém identificadores e consultas de domínio; o template só pode validar banco, migrations, checks e limpeza isolada. [VERIFIED: /opt/web/pca/ops/backup/ensaio_restore_local.sh:36-193]
7. **Quebrar o bind seguro.** O único publish de host deve continuar com fallback `127.0.0.1`; o Nginx é o único acesso externo. [VERIFIED: compose.yml:29-36]
8. **Misturar defaults de identidade no runtime.** Defaults em settings, dashboard ou gerador de ícones deixam marca antiga no gerado; deixá-los apenas em `copier.yml`/`.env.example.jinja`. [VERIFIED: config/settings/base.py:145-161; ops/gerar_icones_pwa.py:60-72; apps/exemplo/templates/exemplo/dashboard.html:106]

## Sequência de Planejamento Recomendada

1. **Tracer Copier:** criar configuração, arquivo de respostas, exclusões, pares Jinja e neutralizações; executar `copier copy` para destino temporário e conferir variáveis, arquivos excluídos e ausência de PCA.
2. **Opcionalidade e atualização:** condicionar app/integrações, criar README duplo e ensaiar tags `v0.1.0 → v0.1.1`; desligar o exemplo por update e repetir atualização posterior.
3. **Operação:** acrescentar backup/retencão/restore, Compose, nginx e `MIGRACAO.md`; validar renderização, shell, Compose e varreduras antes de qualquer ensaio de host.

Essa ordem entrega primeiro a capacidade que torna o repositório um template e reduz o risco de construir `ops/` em arquivos que não chegarão corretamente ao sistema derivado.

## Validação da Fase

Como `workflow.nyquist_validation` está explicitamente `false`, não criar a seção de arquitetura de testes Nyquist nesta pesquisa. Ainda assim, o plano deve executar estas verificações:

```bash
# em diretório temporário e após o checkpoint de instalação do Copier
copier copy --vcs-ref v0.1.0 <repo-template> <destino>
git -C <destino> init
git -C <destino> add . && git -C <destino> commit -m 'chore: sistema gerado'

# depois de uma mudança pequena no núcleo e tag v0.1.1
copier update --defaults
git grep -inE 'pca|sistema_base' -- . ':!*.lock'
test ! -e apps/exemplo  # após update com incluir_app_exemplo=false
docker compose --env-file .env config
sh -n ops/backup/backup.sh ops/backup/retencao.sh ops/backup/ensaio_restore_local.sh
```

No ensaio A→B, verificar também: `_commit` avança no arquivo de respostas, a mudança do núcleo chega ao destino, não restam marcadores `<<<<<<<|=======|>>>>>>>`, e um segundo update não recria `apps/exemplo`. A documentação oficial confirma que caminhos templateados apagados no subprojeto são automaticamente excluídos de updates posteriores, exceto padrões `skip_if_exists`; esta propriedade deve ser comprovada no ensaio, não apenas assumida. [CITED: https://copier.readthedocs.io/en/stable/updating/]

## Domínio de Segurança

O ASVS atual organiza controles de autenticação, sessão, autorização, validação, criptografia, comunicação e configuração; a fase não cria um novo endpoint, mas não pode degradar os controles já herdados. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

| Categoria ASVS | Aplica? | Controle da fase |
|---|---|---|
| Autenticação e sessão | Sim, herdado | Não alterar o núcleo Django; `.env.example` não contém segredo real. [VERIFIED: .env.example:1-24] |
| Autorização | Sim, herdado | Nenhuma alteração funcional no gate/admin; só condicional de app exemplo. [VERIFIED: config/settings/base.py:23-38] |
| Validação e configuração | Sim | Validators Copier bloqueiam slug/cor/porta inválidos antes de renderizar; manter validação runtime de cor. [CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| Criptografia e segredos | Sim | Não registrar `SECRET_KEY`, senhas PostgreSQL ou credenciais R2 em respostas/Copier; apenas placeholders em `.env.example.jinja`. [VERIFIED: .env.example:1-8; .env.example:56-65] |
| Comunicação | Sim | Vhost TLS e proxy loopback; manter header forwarding controlado pelo Nginx. [VERIFIED: /opt/web/pca/ops/nginx/pca.conf:21-40] |

## Perguntas em Aberto

Nenhuma decisão de produto bloqueia o plano. Há somente um checkpoint operacional: confirmar e instalar a distribuição PyPI `copier` antes de executar a prova real de copy/update, pois o CLI não está instalado nesta máquina.

## Ambiente Disponível

| Dependência | Necessária para | Disponível | Versão | Fallback |
|---|---|---:|---|---|
| Copier | copy/update e ensaio TPL-03 | Não | — | Instalar versão aprovada em ambiente isolado após checkpoint humano. |
| Git | tags e projeto derivado | Sim | 2.53.0 | — |
| Docker / Compose | render/validação operacional | Sim | 29.5.2 / v5.1.4 | — |
| Nginx | sintaxe/instalação do vhost | Sim | 1.28.3 | — |
| rclone | backup e restore real | Sim | v1.60.1-DEV | A imagem do backup baixa versão pinada com checksum. |
| Python do host | gerar ícones / CLI | Sim | 3.14.4 | Docker usa Python 3.12 no runtime da aplicação. [VERIFIED: Dockerfile:27-47] |

## Fontes

### Primárias

- [Copier — Configuring a template](https://copier.readthedocs.io/en/latest/configuring/) — perguntas, validators, exclusões, sufixo, respostas, condições e recursos inseguros.
- [Copier — Updating a project](https://copier.readthedocs.io/en/stable/updating/) — pré-requisitos, tags, conflitos, diffs e caminhos removidos.
- `/opt/web/pca/ops/backup/`, `/opt/web/pca/ops/nginx/pca.conf`, `/opt/web/pca/ops/MIGRACAO.md`, `/opt/web/pca/compose.yml` — fonte canônica local, lida somente para extração.

### Secundárias

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — categorias de verificação aplicáveis à configuração e operação.

## Metadados

**Confiança:**

- Copier e atualização: MÉDIA — documentação oficial atual, sem execução local porque o CLI está ausente.
- Pontos de integração e operação PCA: ALTA — fontes de código/artefatos abertas nesta sessão.
- Backup generalizado: MÉDIA — a extração é verificável; o ensaio real de R2 depende de credenciais deliberadamente fora do template.

**Válido até:** 2026-09-17, salvo nova versão major do Copier ou alteração na operação PCA.
