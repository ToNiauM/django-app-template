# Fase 5: Verificação e Documentação — Pesquisa

**Pesquisado em:** 2026-08-18  
**Domínio:** validação de template Copier, inicialização Docker Compose e documentação operacional de Django  
**Confiança:** HIGH

<phase_requirements>
## Requisitos da Fase

| ID | Descrição | Suporte da pesquisa |
|---|---|---|
| QA-01 | Template inclui testes do core e do app exemplo, e o sistema gerado passa a suíte. | Executar a suíte Django na árvore renderizada que inclui o app exemplo; preservar os testes de contrato do template e adicionar um ensaio de cópia/boot. [VERIFIED: requirements.txt:1-10; core/tests/test_login_flow.py:22-214; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:14-231] |
| QA-02 | Cópia, `.env`, Compose, migração e superusuário geram sistema navegável sem editar código. | Um único script efêmero deve seguir essa sequência e verificar configuração Compose, disponibilidade HTTP e os fluxos já cobertos pela suíte. [VERIFIED: README.md.jinja:8-39; compose.yml.jinja:21-39; entrypoint.sh:1-7] |
| DOC-01 | README do template cobre o nascimento de um sistema até proxy/DNS. | Transformar o README-raiz no runbook canônico, com comandos e links para o README renderizado e `ops/MIGRACAO.md`; cobrir pré-requisitos, cópia, segredos, subida, migração, superusuário, health check, vhost/TLS e DNS. [VERIFIED: README.md:38-94; README.md.jinja:6-43] |
</phase_requirements>

## Resumo

A Fase 5 deve validar o produto na única fronteira que importa depois da Fase 4: uma cópia limpa do template. A raiz contém arquivos Jinja e é explicitamente declarada como template-fonte, portanto não se deve executar `manage.py test` nem Compose diretamente nela. [VERIFIED: README.md:1-6; copier.yml:1-5] O ensaio precisa gerar um diretório temporário com `incluir_app_exemplo=true`, preencher apenas segredos descartáveis num `.env` daquele diretório, subir `db` e `web`, executar migrações e criar um administrador de ensaio; em seguida, deve rodar a suíte Django e confirmar que o processo HTTP real responde. [VERIFIED: .template-tests/test_copier_copy.sh:25-46; .template-tests/test_copier_copy.sh:121-174; compose.yml.jinja:21-39]

O repositório já tem a base certa: a matriz Copier renderiza as variantes com e sem exemplo, valida Compose e scripts de operação, e os testes Django existentes cobrem login, shell, CRUD HTMX e dashboard. [VERIFIED: .template-tests/test_copier_copy.sh:121-192; core/tests/test_login_flow.py:22-214; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:14-231; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:14-143] Durante esta pesquisa, `test_copier_copy.sh`, `test_copier_update.sh` e os quatro testes Python de contrato da Fase 4 passaram; um ensaio isolado também passou por cópia, `docker compose`, `migrate`, criação não interativa de superusuário, `manage.py test core apps.exemplo`, `/healthz` e `/login/`. [VERIFIED: execução local de 2026-08-18]

O README-raiz hoje inicia a jornada, mas delega a subida, proxy e DNS ao README renderizado e ao runbook de migração. [VERIFIED: README.md:38-66; README.md.jinja:21-43] Para satisfazer DOC-01 de maneira inequívoca, ele deve expor a sequência completa e usar os arquivos gerados apenas como detalhes operacionais vinculados.

**Recomendação principal:** crie um ensaio de nascimento único, isolado e autocontido em `.template-tests/`, que prove QA-01 e QA-02 em uma cópia real, e reestruture o `README.md` de raiz como roteiro linear da mesma sequência até o proxy/DNS.

## Mapa de Responsabilidades Arquiteturais

| Capacidade | Camada primária | Camada secundária | Justificativa |
|---|---|---|---|
| Renderizar um sistema a partir do template | CLI / build local | Sistema de arquivos | Copier transforma a árvore fonte em um novo projeto e grava as respostas para rastreabilidade. [VERIFIED: copier.yml:1-5; .template-tests/test_copier_copy.sh:36-45] |
| Inicializar banco e aplicação | Orquestração Docker Compose | Banco de dados | Compose inicia `db` e `web`; o serviço web depende do health check do banco. [VERIFIED: compose.yml.jinja:3-39] |
| Executar migrações, criar administrador e testes | Backend Django | Banco de dados | São comandos do processo Django dentro do serviço web; o runner padrão cria e destrói bancos de teste. [CITED: https://docs.djangoproject.com/en/5.2/topics/testing/advanced/] |
| Provar navegação após o boot | Serviço HTTP | Cliente / navegador | `/healthz` prova alcance do processo; login, shell, CRUD e dashboard são as jornadas autenticadas a cobrir pela suíte e por smoke HTTP. [VERIFIED: config/urls.py.jinja:4-17; core/tests/test_login_flow.py:22-214; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:27-231; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:25-143] |
| Publicar atrás de TLS e DNS | Proxy / host | CDN / DNS | O gerado mantém a aplicação em loopback e entrega vhost e runbook de migração para a borda externa. [VERIFIED: .env.example.jinja:21-23; README.md.jinja:30-39] |

## Stack Padrão

### Núcleo

| Componente | Versão / contrato | Finalidade | Por que usar |
|---|---|---|---|
| Django | `Django==5.2.17` | Runner padrão, banco de teste e testes de comportamento do sistema gerado. | `manage.py test` descobre `test*.py`, cria bancos de teste, aplica migrações e executa checks antes dos testes. [VERIFIED: requirements.txt:1-10 — `Django==5.2.17`; CITED: https://docs.djangoproject.com/en/5.2/topics/testing/advanced/] |
| Copier | `9.17.1` | Materializar a árvore Jinja que é objeto da prova. | As respostas são persistidas no arquivo de respostas configurado, necessário para updates; a cópia é o contrato de entrada do template. [VERIFIED: copier.yml:1-5 — `_min_copier_version: "9.17.1"` e `_answers_file: .copier-answers.yml`; CITED: https://copier.readthedocs.io/en/latest/configuring/] |
| Docker Compose | CLI disponível nesta máquina: `29.5.2` | Subir os serviços que o usuário realmente receberá. | `up --detach` mantém os serviços em segundo plano; `exec -T` torna comandos de validação próprios para script; `config -q` valida a configuração resolvida. [VERIFIED: execução local de 2026-08-18; CITED: https://docs.docker.com/reference/cli/docker/compose/up/; CITED: https://docs.docker.com/reference/cli/docker/compose/exec/; CITED: https://docs.docker.com/reference/cli/docker/compose/config/] |
| curl | CLI disponível nesta máquina: `8.18.0` | Smoke HTTP de `/healthz` e da tela de login no serviço publicado em loopback. | Evita introduzir uma segunda framework de testes só para confirmar que o processo web responde. [VERIFIED: execução local de 2026-08-18; VERIFIED: compose.yml.jinja:31-39] |

### Suporte

| Componente | Finalidade | Quando usar |
|---|---|---|
| `.template-tests/test_copier_copy.sh` | Matriz de renderização, neutralidade e sanidade estática da árvore gerada. | Mantê-lo como regressão do template; não duplicar nele o boot completo de Fase 5. [VERIFIED: .template-tests/test_copier_copy.sh:1-23; .template-tests/test_copier_copy.sh:121-219] |
| Testes `core/tests/` e `apps/exemplo/tests/` | Comportamento autenticado de core e app exemplo. | Rodar dentro da cópia com exemplo habilitado, via `manage.py test`. [VERIFIED: core/tests/test_login_flow.py:22-214; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:14-231; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:14-143] |
| `ops/MIGRACAO.md` renderizado | Referência operacional detalhada para restauração, vhost, certificado e DNS. | Linkar a partir do roteiro raiz, sem duplicar procedimentos perigosos de recuperação. [VERIFIED: README.md.jinja:34-43] |

### Alternativas consideradas

| Em vez de | Poderia usar | Decisão e trade-off |
|---|---|---|
| Testes Django + smoke HTTP | Framework nova de automação de navegador | Não adicionar dependência nesta fase. A suíte existente já cobre os fluxos de login, shell, CRUD e dashboard; o smoke HTTP deve provar que a cópia realmente está escutando. Uma inspeção manual breve no navegador permanece uma evidência complementar de UX, não substituta da regressão. [VERIFIED: core/tests/test_login_flow.py:22-214; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:27-231; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:25-143] |
| Um script novo de nascimento | Executar testes na raiz do template | Usar a cópia: a raiz é fonte Jinja e o próprio README proíbe executá-la como sistema derivado. [VERIFIED: README.md:1-6; copier.yml:1-5] |

**Instalação:** nenhuma dependência de runtime nova deve ser instalada nesta fase. Reutilize as versões já fixadas no template e a instalação isolada de Copier. [VERIFIED: requirements.txt:1-10; README.md:8-21]

## Padrões de Arquitetura

### Diagrama do fluxo de prova

```text
checkout do template
      |
      v
copier copy (destino temporário, app exemplo=true)
      |
      +--> .env.example -> .env com segredos somente de ensaio
      |
      v
docker compose config -q -> docker compose up -d (db + web)
      |
      +--> PostgreSQL saudável -> web /healthz
      |
      v
migrate -> createsuperuser de ensaio -> manage.py test core apps.exemplo
      |
      +--> curl /healthz e /login/ -> evidência de HTTP publicado
      |
      v
README do template -> README renderizado -> ops/MIGRACAO.md -> nginx/TLS/DNS
```

O script deve ser o consumidor automatizado da documentação: se uma instrução crítica do README não for executável nesse roteiro, ela não está comprovada. [VERIFIED: README.md:38-66; README.md.jinja:8-43]

### Estrutura recomendada

```text
.template-tests/
├── test_copier_copy.sh          # matriz estática já existente
├── test_copier_update.sh        # ensaio de atualização já existente
└── test_05_nascimento.sh        # novo ensaio temporário de cópia + Compose + Django

README.md                        # runbook canônico do template, do copy ao proxy/DNS
README.md.jinja                  # operação do sistema específico renderizado
ops/MIGRACAO.md.jinja            # detalhe de migração, TLS e recuperação do gerado
```

### Padrão 1: ensaio efêmero, não uma nova aplicação de teste

**O que:** o script cria um diretório temporário e escolhe um slug/porta exclusivos; nenhuma modificação ocorre no checkout do template ou em um sistema real. A matriz atual já segue esse padrão com `mktemp -d` e trap de limpeza. [VERIFIED: .template-tests/test_copier_copy.sh:5-12]

**Quando usar:** a cada alteração no template, Dockerfile, Compose, `.env.example`, documentação de nascimento ou artefato que possa tornar o projeto recém-gerado inválido.

**Implementação prescrita:**

1. Invocar Copier com dados determinísticos e `incluir_app_exemplo=true`.
2. Copiar `.env.example` para `.env`, substituindo somente placeholders de ensaio; nunca registrar esses valores no Git nem em `.copier-answers.yml`.
3. Rodar `docker compose config -q`, `docker compose up -d`, esperar disponibilidade de `db`/`web`, e só então executar comandos no `web` com `docker compose exec -T`.
4. Executar explicitamente migração e criação não interativa de superusuário de ensaio. Embora o entrypoint já tenha `python manage.py migrate --noinput`, repetir `migrate --noinput` é idempotente e prova o passo que a documentação exige. [VERIFIED: entrypoint.sh:1-7 — `python manage.py migrate --noinput`; CITED: https://docs.docker.com/reference/cli/docker/compose/exec/]
5. Rodar `python manage.py test core apps.exemplo --noinput`, fazer smoke HTTP e desmontar apenas o projeto/recursos que o script criou.

### Padrão 2: uma documentação em camadas, com uma jornada canônica

**O que:** o `README.md` de raiz explica a jornada inteira e aponta aos detalhes contextuais: README renderizado para operação daquele sistema e `ops/MIGRACAO.md` para migração, TLS e recuperação. [VERIFIED: README.md:38-66; README.md.jinja:34-43]

**Quando usar:** sempre que a informação puder levar o operador a editar código, expor a aplicação diretamente, colocar segredos nas respostas Copier ou omitir uma etapa de publicação.

**Conteúdo obrigatório do README-raiz:** pré-requisitos; instalação isolada do Copier; `copier copy`; respostas; `cp .env.example .env`; geração e armazenamento local de segredos; `docker compose up -d`; logs e health check; `migrate`; `createsuperuser`; URLs de login, shell, CRUD e dashboard; arquivo do vhost gerado; certificado/TLS; DNS; referência ao runbook de migração; e comandos de regressão. O ponto de partida e os artefatos já existem, mas devem ficar na ordem de operação. [VERIFIED: README.md:8-94; README.md.jinja:8-43]

### Exemplo de sequência a documentar e automatizar

Os comandos abaixo são derivados das linhas que já publicam a operação do sistema gerado: `"docker compose up -d --build"`, `"docker compose exec web python manage.py migrate"` e `"docker compose exec web python manage.py createsuperuser"`. [VERIFIED: README.md.jinja:21-28]

```bash
copier copy /caminho/para/template /caminho/para/novo-sistema
cd /caminho/para/novo-sistema
cp .env.example .env
# preencher somente segredos locais no .env
docker compose up -d
docker compose exec -T web python manage.py migrate --noinput
docker compose exec web python manage.py createsuperuser
curl --fail http://127.0.0.1:<porta>/healthz
```

O `<porta>` é uma variável da resposta Copier, não um literal a fixar no teste. A configuração atualmente declara `"WEB_PORT={{ sistema_porta }}"` e publica `"${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000"`. [VERIFIED: .env.example.jinja:21-23; compose.yml.jinja:31-39]

### Anti-padrões a evitar

- **Rodar a suíte na raiz:** ela contém Jinja e não representa nenhum produto gerado. Gere antes uma árvore temporária. [VERIFIED: README.md:1-6; copier.yml:1-5]
- **Usar segredos reais ou editar arquivos do template para o ensaio:** `.env.example` reserva placeholders para os segredos; preencha valores descartáveis apenas na cópia. [VERIFIED: .env.example.jinja:1-4; .env.example.jinja:34-44]
- **Usar somente `docker compose up` como evidência:** processo iniciado não é evidência de migração, autenticação ou páginas navegáveis; combine runner Django e smoke HTTP. [CITED: https://docs.docker.com/reference/cli/docker/compose/up/; CITED: https://docs.djangoproject.com/en/5.2/topics/testing/advanced/]
- **Depender do serviço `backup` no ensaio de nascimento:** os placeholders de R2 não são credenciais operacionais; o caminho de QA deve subir explicitamente os serviços necessários para web/banco e manter os testes de backup como contrato próprio. [VERIFIED: compose.yml.jinja:41-69; .env.example.jinja:40-52; .template-tests/test_04_05_backup.py:46-173]

## Não Reimplementar

| Problema | Não construir | Usar | Motivo |
|---|---|---|---|
| Descoberta, banco de teste e isolamento de testes Django | Runner Python próprio ou cópia manual de banco | `manage.py test` padrão | O runner padrão descobre testes, prepara banco, aplica migrações, executa checks e desmonta o banco de teste. [CITED: https://docs.djangoproject.com/en/5.2/topics/testing/advanced/] |
| Renderização e validação de respostas | Script próprio de cópia Jinja | `copier copy` e a matriz existente | O template já possui validators e arquivo de respostas configurado. [VERIFIED: copier.yml:40-91; .template-tests/test_copier_copy.sh:25-46] |
| Validação do Compose | Parser YAML caseiro | `docker compose config -q` | O Compose resolve variáveis e valida o modelo efetivo. [CITED: https://docs.docker.com/reference/cli/docker/compose/config/] |
| Fluxos de CRUD/dashboard | Cenários duplicados em shell | Testes Django existentes | CRUD e dashboard já possuem coberturas de autenticação, criação/edição/exclusão, filtros e agregações. [VERIFIED: apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:27-231; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:25-143] |

**Insight-chave:** a nova peça deve orquestrar a prova entre ferramentas existentes, não recriar comportamento que Django, Copier e Compose já oferecem.

## Armadilhas Comuns

### Armadilha 1: confundir validação do template com boot do sistema

**O que falha:** `test_copier_copy.sh` valida renderização, compilação, Compose e scripts, mas não sobe web/banco, cria usuário ou executa a suíte no produto gerado. [VERIFIED: .template-tests/test_copier_copy.sh:121-150]

**Como evitar:** manter essa matriz e acrescentar o ensaio de nascimento; ambas são necessárias e têm escopos distintos.

### Armadilha 2: condição de corrida entre `up` e comandos Django

**O que falha:** executar `exec` antes de o banco e web estarem prontos causa falhas intermitentes.

**Como evitar:** validar configuração primeiro, iniciar os serviços, aguardar saúde/disponibilidade com timeout e imprimir `docker compose ps`/logs na falha. Compose documenta `up --detach` para processo em segundo plano e `exec -T` para automação. [CITED: https://docs.docker.com/reference/cli/docker/compose/up/; CITED: https://docs.docker.com/reference/cli/docker/compose/exec/]

### Armadilha 3: documentação que diverge do ensaio

**O que falha:** o template diz hoje para seguir o README renderizado; mudanças posteriores podem quebrar o primeiro uso sem alterar testes. [VERIFIED: README.md:64-66]

**Como evitar:** organizar o script seguindo os mesmos marcos e fazer o README-raiz referenciar o nome do script de regressão. Não alegar que comandos são testados se o script não os executa.

### Armadilha 4: superusuário automatizado vazar credencial

**O que falha:** uma senha usada no script pode acabar no README, logs persistidos ou controle de versão.

**Como evitar:** injetar credenciais de ensaio somente no ambiente do processo, não as ecoar, destruir a cópia ao final e manter o README de operador no comando interativo. O template reserva `.env` para segredos e instrui que eles não sejam perguntas Copier. [VERIFIED: README.md:68-79; .env.example.jinja:1-4; .env.example.jinja:34-44]

### Armadilha 5: considerar health check como prova de navegação

**O que falha:** `/healthz` confirma o processo, não login, sessão, shell, CRUD ou dashboard.

**Como evitar:** usar `/healthz` e `/login/` apenas como borda HTTP, e fazer QA-01 rodar os testes de comportamento já existentes para os fluxos autenticados. [VERIFIED: config/urls.py.jinja:4-17; core/tests/test_login_flow.py:22-214; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:27-231; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:25-143]

## Estado da Arte

| Abordagem anterior | Abordagem da Fase 5 | Impacto |
|---|---|---|
| Contratos de renderização e operação estática na Fase 4 | Cópia limpa, boot real, suíte Django e smoke HTTP da cópia | Fecha a lacuna entre “o arquivo renderiza” e “um sistema nasce navegável”. [VERIFIED: .template-tests/test_copier_copy.sh:121-174; execução local de 2026-08-18] |
| README-raiz encaminha etapas posteriores | README-raiz passa a ser roteiro completo, com referências aos detalhes renderizados | DOC-01 se torna verificável sem conhecimento implícito. [VERIFIED: README.md:38-66; README.md.jinja:34-43] |

## Log de Premissas

| # | Premissa | Seção | Risco se estiver errada |
|---|---|---|---|
| A1 | [RESOLVED] A Fase 5 não adiciona automação de navegador nem nova dependência frontend/browser; a inspeção manual é evidência complementar após o tracer determinístico. | Stack padrão; `05-UI-SPEC.md` | Resolvida pelo contrato UI verificado: a regressão obrigatória combina Copier, Compose, Django e HTTP antes do checkpoint manual. |

## Questões em Aberto (RESOLVED)

1. **[RESOLVED] A prova de navegação não inclui automação de navegador na Fase 5.**
   - Decisão: não adicionar automação de navegador nem qualquer dependência frontend/browser nesta fase.
   - Evidência determinística obrigatória: executar o tracer completo na cópia gerada — Copier, `.env`, Compose, migração, criação de superusuário, suíte Django e smoke HTTP de `/healthz` e `/login/`. [VERIFIED: execução local de 2026-08-18; core/tests/test_login_flow.py:22-214]
   - Evidência complementar: somente depois de o tracer passar, realizar o checkpoint manual no navegador para login, shell, CRUD e dashboard. [VERIFIED: `05-UI-SPEC.md`, Escopo visual da fase e Interação e evidência visual obrigatória]

## Disponibilidade do Ambiente

| Dependência | Necessária para | Disponível | Versão | Fallback |
|---|---|---|---|---|
| Python | Copier e scripts de teste | ✓ | `3.14.4` | — [VERIFIED: execução local de 2026-08-18] |
| Copier isolado | Gerar a cópia | ✓ | `9.17.1` | — [VERIFIED: execução local de 2026-08-18; README.md:13-17] |
| Docker Engine/Compose | Boot real de `db` e `web` | ✓ | Docker `29.5.2`; daemon disponível | sem fallback para QA-02 [VERIFIED: execução local de 2026-08-18] |
| curl | Smoke HTTP | ✓ | `8.18.0` | `python` HTTP client somente se curl estiver ausente [VERIFIED: execução local de 2026-08-18] |
| Git | Metadados Copier e documentação de primeiro commit | ✓ | `2.53.0` | — [VERIFIED: execução local de 2026-08-18] |

**Dependências ausentes sem fallback:** nenhuma nesta máquina de pesquisa. [VERIFIED: execução local de 2026-08-18]

## Domínio de Segurança

`security_enforcement` não está desativado em `.planning/config.json`; portanto esta seção é obrigatória. [VERIFIED: .planning/config.json:1-42]

### Categorias ASVS aplicáveis

| Categoria ASVS | Aplica? | Controle/checagem da Fase 5 |
|---|---|---|
| V2 Autenticação | Sim | Rodar testes de login e criar administrador apenas com credencial efêmera no ambiente do processo. [VERIFIED: core/tests/test_login_flow.py:22-214] |
| V3 Gestão de sessão | Sim | Preservar testes de ciclo login/logout/CSRF; não registrar cookies ou tokens no ensaio. [VERIFIED: core/tests/test_login_flow.py:83-172] |
| V4 Controle de acesso | Sim | Preservar testes de redirecionamento de anônimo em CRUD e dashboard. [VERIFIED: apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_crud.py:27-31; apps/{% if incluir_app_exemplo %}exemplo{% endif %}/tests/test_dashboard.py:25-29] |
| V5 Validação | Sim | Manter validação de respostas Copier e nunca passar dados de produção ao script. [VERIFIED: copier.yml:40-91; .template-tests/test_copier_copy.sh:195-214] |
| V6 Criptografia / segredos | Sim | Gerar/preencher chaves somente no `.env` efêmero; respostas Copier não contêm segredos. [VERIFIED: README.md:68-79; .template-tests/test_copier_copy.sh:160-171] |

As categorias são uma seleção de verificação, não uma declaração de conformidade ASVS completa. A OWASP lista autenticação, sessão, controle de acesso, validação e criptografia entre suas áreas de verificação. [CITED: https://devguide.owasp.org/en/03-requirements/05-asvs/]

### Ameaças relevantes

| Padrão | STRIDE | Mitigação padrão |
|---|---|---|
| Segredo de ensaio persistido em código, log ou answers | Information disclosure | Criar apenas na cópia temporária, não imprimir e preservar os checks que recusam segredo em `.copier-answers.yml`. [VERIFIED: README.md:68-79; .template-tests/test_copier_copy.sh:160-171] |
| Serviço acessível além do proxy | Elevation of privilege / Information disclosure | Smoke no bind loopback e documentação do vhost/TLS/DNS, sem publicar porta em todas as interfaces. [VERIFIED: .env.example.jinja:21-23; compose.yml.jinja:31-39; README.md.jinja:30-39] |
| Falso positivo de disponibilidade | Tampering / reliability | Combinar health check, comandos Django e testes autenticados; não aceitar `up` isoladamente. [CITED: https://docs.docker.com/reference/cli/docker/compose/up/; CITED: https://docs.djangoproject.com/en/5.2/topics/testing/advanced/] |

## Fontes

### Primárias

- [Django — Advanced testing topics](https://docs.djangoproject.com/en/5.2/topics/testing/advanced/) — runner padrão, descoberta e ciclo do banco de teste.
- [Copier — Configuring a template](https://copier.readthedocs.io/en/latest/configuring/) — arquivo de respostas e cópia do template.
- [Docker Compose — up](https://docs.docker.com/reference/cli/docker/compose/up/), [exec](https://docs.docker.com/reference/cli/docker/compose/exec/) e [config](https://docs.docker.com/reference/cli/docker/compose/config/) — semântica dos comandos de boot e validação.
- Código e documentação abertos nesta sessão: `README.md`, `README.md.jinja`, `copier.yml`, `compose.yml.jinja`, `entrypoint.sh`, `.template-tests/` e testes do core/app exemplo.

### Secundárias

- [OWASP ASVS — Developer Guide](https://devguide.owasp.org/en/03-requirements/05-asvs/) — categorias de verificação de segurança aplicáveis.

## Metadados

**Distribuição de confiança:**

- Stack padrão: HIGH — versões, ferramentas e fluxo observados na árvore e no ambiente; documentação oficial consultada.
- Arquitetura: HIGH — o ensaio real da cópia passou nesta sessão e os contratos da Fase 4 já estão automatizados.
- Armadilhas: HIGH — derivadas dos limites explícitos dos testes e do Compose atuais; A1 foi resolvida pelo contrato UI verificado sem automação de navegador ou nova dependência frontend/browser na Fase 5.

**Válido até:** 2026-09-17, salvo alteração de Django, Copier, Docker Compose ou do contrato do template.
