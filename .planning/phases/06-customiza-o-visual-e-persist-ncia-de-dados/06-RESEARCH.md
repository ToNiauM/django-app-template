# Fase 6: Customização Visual e Persistência de Dados — Research

**Pesquisado em:** 2026-08-19
**Domínio:** Docker Compose (bind mount PostgreSQL 17) + Django static files (contrato de logos SVG) em template Copier
**Confiança:** HIGH

## Summary

A fase tem dois eixos independentes e de baixo risco técnico. **Eixo 1 (logos):** o mecanismo já existe por inteiro — `{% static %}` + WhiteNoise `CompressedManifestStaticFilesStorage` + context processor `identidade` — falta apenas criar dois SVGs placeholder neutros em `core/static/img/`, referenciá-los via `<img src="{% static ... %}">` nos pontos definidos (D-68/D-69) e documentar o contrato "substituir o arquivo mantendo nome e extensão". Nenhuma biblioteca nova, nenhuma variável Copier nova. **Eixo 2 (persistência):** trocar `pgdata:/var/lib/postgresql/data` por `${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data` no `compose.yml.jinja` e remover o bloco `volumes:` de topo. Verificado nas docs oficiais: `docker compose down -v` remove **apenas** named volumes e volumes anônimos — bind mounts sobrevivem por construção; o Compose (short syntax) cria o diretório host ausente automaticamente; o entrypoint do postgres:17 (que inicia como root) ajusta ownership para uid/gid 999.

Os riscos reais estão nas bordas: (1) o **tracer `.template-tests/test_05_nascimento.sh` quebra na limpeza** — `rm -rf ${TMP}` do usuário host falha em arquivos uid 999 criados pelo initdb; precisa de limpeza via container; (2) **sistemas gerados hoje não recebem `.gitignore` nenhum** (`.gitignore` está no `_exclude` do copier.yml) — D-74 exige que `dados/` seja ignorado no sistema gerado, o que força mexer no `_exclude` seguindo o precedente do `README.md.jinja`; (3) **`copier update` em sistema já nascido** troca o compose e o próximo `up` inicializaria um banco VAZIO no bind mount enquanto os dados reais ficam órfãos no named volume `<slug>_pgdata` — precisa de nota de migração explícita.

**Recomendação primária:** implementar em dois planos independentes — (a) persistência: compose + `.env.example` + `.gitignore`(s) + tracer + docs; (b) logos: SVGs + templates + testes + seção "Customização de marca". Nenhum pacote novo é instalado.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, ancoradas nas decisões D-16/D-17/D-20 da Fase 2 e D-50 da Fase 4. Numeração continua de D-64.)*

#### Mecanismo e local dos logos (entidade + subsistema)
- **D-65:** Logos são **arquivos estáticos em caminhos fixos e documentados** no core: `core/static/img/logo-entidade.svg` (logo principal da entidade, ex.: CFC) e `core/static/img/logo-subsistema.svg` (logo do sistema específico). Customizar = substituir o arquivo mantendo nome e extensão — nenhuma edição de código, nenhuma variável nova. Sem upload via admin (media storage é nova capacidade, fora do escopo) e sem caminho configurável via `.env` (indireção desnecessária; o nome fixo É o contrato).
- **D-66:** O template entrega **placeholders neutros em SVG** nos dois caminhos (sem marca de domínio — TPL-04), no espírito dos ícones PWA placeholder (D-20). Os templates sempre referenciam os arquivos via `{% static %}`; nunca há referência quebrada num sistema recém-nascido.
- **D-67:** Os placeholders SVG podem ser simples (ex.: monograma com a sigla/forma neutra) e devem renderizar bem em fundo claro do shell/login. Texto (`sistema_nome`/`sistema_sigla`) permanece ao lado/abaixo dos logos — o logo complementa a identidade textual (D-16), não a substitui (acessibilidade: `alt` sempre presente).

#### Posicionamento dos logos no UI
- **D-68:** **Logo do subsistema** aparece no cabeçalho da aside do shell (junto à sigla/nome, hoje texto puro em `shell.html`) e no header mobile da gaveta. É a identidade "deste sistema".
- **D-69:** **Logo da entidade** aparece na tela de login (acima do formulário, identidade institucional) e discretamente no rodapé da aside do shell. É a identidade "da casa" comum a toda a família.
- **D-70:** O **admin não ganha logo** — mantém a identidade por nome/cor via override cirúrgico existente (D-14). Qualquer mudança no admin além disso está fora.

#### PWA — logo e nome
- **D-71:** O **nome do PWA já é customizável** e permanece como está: `SISTEMA_NOME`/`SISTEMA_SIGLA` no `.env` → settings → `manifest_view` (D-16/D-18). Esta fase não muda o mecanismo — apenas o documenta como O local de customização do nome do PWA.
- **D-72:** O **logo do PWA** segue o contrato de arquivos fixos: `core/static/img/icon-192.png`, `icon-512.png`, `icon-512-maskable.png`. Customizar = substituir esses três arquivos pela arte oficial (derivada do logo do subsistema) **ou** regenerar os placeholders com `ops/gerar_icones_pwa.py` (lê sigla/cor do `.env`). Nomes de arquivo do manifest não mudam (compatibilidade com hashing do WhiteNoise via `static()` já resolvida).

#### Persistência do banco no host
- **D-73:** O serviço `db` troca o named volume `pgdata` por **bind mount para diretório no host**, com caminho configurável via `.env` (`PGDATA_DIR`, aplicando D-50) e **default relativo ao diretório do projeto** (ex.: `./dados/pg`). Bind mounts não são removidos por `docker compose down -v` — os dados sobrevivem por construção.
- **D-74:** O diretório de dados entra no `.gitignore` do sistema gerado (e do template). Documentar o requisito de permissões do PostgreSQL no container (o initdb ajusta ownership do diretório vazio; documentar uid/gid se necessário para troubleshooting).
- **D-75:** A **invariante de portabilidade é preservada e reforçada**: o runbook de migração (dump + `.env` + `compose up`) continua o caminho canônico; o bind mount adiciona a garantia de que operações rotineiras de compose (down -v, recriação) jamais destroem dados. `MIGRACAO.md` e README ganham nota sobre o novo layout de dados.
- **D-76:** Mudança aplicada no **`compose.yml.jinja`** (fonte do template) e refletida no `.env.example.jinja` (variável `PGDATA_DIR` com default comentado). Healthcheck e demais serviços (web, backup) permanecem intactos.

#### Documentação da customização
- **D-77:** Uma **seção única "Customização de marca"** no `README.md.jinja` (README do sistema gerado) lista TODOS os pontos de customização em um só lugar: logo da entidade (arquivo), logo do subsistema (arquivo), ícones/nome do PWA (arquivos + `.env`), cor primária (`.env` + `tailwind.config.js`), nome/sigla (`.env`). O `core/README.md` referencia os mesmos pontos como convenção do core.
- **D-78:** O `README.md` do template (raiz) atualiza o passo a passo do nascimento para incluir a etapa opcional "inserir logos oficiais" e a nota sobre persistência dos dados no host.

### Claude's Discretion
- Desenho exato dos placeholders SVG (monograma, forma geométrica neutra) e dimensões/classes Tailwind de exibição.
- Aceitar PNG como formato alternativo dos logos (e como documentar isso sem quebrar o contrato de nome fixo).
- Favicon derivado dos ícones existentes (se entrar, segue o mesmo contrato de arquivo fixo).
- Estender `ops/gerar_icones_pwa.py` para gerar ícones a partir do arquivo de logo do subsistema (opcional, não obrigatório).
- Nome exato da variável (`PGDATA_DIR` ou similar) e do diretório default de dados (`./dados/pg` ou similar), e se o `entrypoint`/README precisa de passo de criação do diretório.
- Testes: quais asserções entram (presença dos arquivos de logo nos templates renderizados, manifest, config do compose).

### Deferred Ideas (OUT OF SCOPE)
- Upload de logos via admin (media storage + formulário) — nova capacidade, fase própria se algum dia for desejada.
- Variantes de logo para dark mode — o template não tem dark mode (decisão da Fase 2).
</user_constraints>

<phase_requirements>
## Phase Requirements

Fase pós-v1 sem REQ IDs formais — os critérios de sucesso da fase são os requisitos:

| ID | Description | Research Support |
|----|-------------|------------------|
| C1 | Local único e documentado no `core` para o logo principal da entidade | Contrato de arquivo fixo `core/static/img/logo-entidade.svg` + `<img src="{% static %}">` em `login.html` e rodapé da aside (padrão em "Architecture Patterns"); seção "Customização de marca" (D-77) |
| C2 | Local único e documentado no `core` para o logo do subsistema | Idem, `core/static/img/logo-subsistema.svg` no cabeçalho da aside de `shell.html` e header mobile |
| C3 | Logo e nome do PWA customizáveis a partir do `core`, refletindo no manifest e na instalação | Mecanismo JÁ existe (`manifest_view` + `static()` + `SISTEMA_NOME/SIGLA` no `.env`) — trabalho é somente documentação (D-71/D-72); verificado em `core/views.py::manifest_view` |
| C4 | Dados do banco no host, sobrevivendo a `docker compose down -v` | Bind mount `${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data`; `down -v` remove só named/anonymous volumes [VERIFIED: docs.docker.com]; sintaxe e pitfalls em "Architecture Patterns"/"Common Pitfalls" |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Trabalho iniciado via comandos GSD (este research faz parte de `/gsd:plan-phase`); sem edições diretas fora do fluxo.
- Stack/convenções "not yet documented" no CLAUDE.md — as convenções reais vivem em `core/README.md`, nos comentários pt-BR do código e nas decisões do `.planning/` (respeitadas neste research).
- Constraints do orquestrador: docs/artefatos em pt-BR; comentários de código em pt-BR explicando "porquê"; mudanças nos ARQUIVOS-FONTE do template; D-50 (".env primeiro, .jinja mínimo"); D-40 (zero automatismo pós-geração); TPL-04 (zero menção a PCA/CFC/domínio no código gerado); `/opt/web/pca` é somente leitura.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Logo entidade/subsistema (arquivo) | Static assets (`core/static/img/`) | Templates Django (`shell.html`, `login.html`) | Contrato D-65: o arquivo É o ponto de customização; templates só referenciam via `{% static %}` |
| Hashing/serving dos logos | WhiteNoise (build da imagem: `collectstatic`) | — | `CompressedManifestStaticFilesStorage` já configurado; `{% static %}` resolve o nome hasheado |
| Nome/ícones do PWA | Backend Django (`manifest_view`) | `.env` → settings | Mecanismo pronto (D-18); fase só documenta |
| Persistência do PostgreSQL | Docker Compose (`compose.yml.jinja`, serviço `db`) | `.env` (`PGDATA_DIR`) + `.gitignore` | Bind mount é config de infraestrutura; nada muda no Django |
| Documentação de customização | `README.md.jinja` (sistema gerado) | `core/README.md`, `README.md` raiz, `ops/MIGRACAO.md.jinja` | D-77/D-78: um único lugar canônico no README gerado |
| Regressão do fluxo completo | `.template-tests/` (host) + `core/tests/` (container) | — | Tracer valida nascimento; suíte Django valida templates/manifest |

## Standard Stack

### Core (nenhuma dependência nova nesta fase)

| Library/Imagem | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| postgres (imagem oficial) | 17 (fixado no compose) | Banco com bind mount | Já em uso; uid/gid 999, `PGDATA=/var/lib/postgresql/data`, `VOLUME /var/lib/postgresql/data` [VERIFIED: Dockerfile oficial docker-library/postgres 17/bookworm] |
| Docker Compose | v2 (Docker 29.5.2 local) | Bind mount + interpolação `${VAR:-default}` | Padrão já usado no compose (`${WEB_BIND_ADDRESS:-127.0.0.1}`) |
| Django | 5.2 LTS | `{% static %}`, `static()` | Já em uso |
| WhiteNoise | (já em requirements) | `CompressedManifestStaticFilesStorage` hasheia e serve os SVGs | Já configurado em `config/settings/base.py.jinja` STORAGES |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Bind mount `./dados/pg` | Named volume `external: true` (padrão da PCA em produção — `/opt/web/pca/compose.yml` documenta o incidente de 2026-07-28) | Também sobrevive a `down -v`, mas exige `docker volume create` manual antes do primeiro `up` (quebra QA-02 "sobe sem editar nada") e os dados não ficam visíveis/copiáveis no diretório do projeto. **D-73 travou bind mount — não re-litigar.** |
| `<img src="{% static %}">` | SVG inline no template | Inline permitiria `currentColor`, mas quebraria o contrato D-65 (substituir arquivo sem editar código). `<img>` é obrigatório. |
| SVG placeholder | PNG placeholder | SVG escala sem serialização de tamanhos e é texto (diff legível, sem binário novo no git). D-66 travou SVG. |

**Instalação:** nenhuma — fase não adiciona pacotes.

## Package Legitimacy Audit

**Nenhum pacote externo é instalado nesta fase.** Não há mudança em `requirements.txt`, `package.json` ou imagens novas — a fase usa apenas Django/WhiteNoise/postgres:17 já presentes. slopcheck não é aplicável.

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram (fluxo dos dois eixos)

```
EIXO LOGOS (build/render):
  operador substitui core/static/img/logo-*.svg
        │
        ▼
  docker compose up -d --build ──► collectstatic (build da imagem, Dockerfile L44-50)
        │                                │
        ▼                                ▼
  {% static 'img/logo-*.svg' %}   staticfiles/ com nome hasheado (WhiteNoise manifest)
        │
        ├─► shell.html (aside header: logo-subsistema; aside footer: logo-entidade)
        └─► login.html (acima do form: logo-entidade)

EIXO PERSISTÊNCIA (runtime):
  .env (PGDATA_DIR opcional) ──► compose interpola ${PGDATA_DIR:-./dados/pg}
        │
        ▼
  docker compose up -d ──► engine cria ./dados/pg se ausente (short syntax)
        │
        ▼
  entrypoint postgres (root) ──► chown 999:999 + initdb (só se dir vazio)
        │
        ▼
  dados em ./dados/pg no HOST ──► docker compose down -v NÃO toca bind mounts
```

### Pattern 1: Bind mount configurável via .env com default (D-73/D-76)

**What:** trocar o named volume pelo bind mount interpolado, removendo o bloco `volumes:` de topo.
**When to use:** exatamente uma mudança no serviço `db` do `compose.yml.jinja`.

```yaml
# Fonte: compose.yml.jinja (diff conceitual)
services:
  db:
    image: postgres:17
    # ...environment/healthcheck intactos (D-76)...
    volumes:
      # Bind mount, não named volume: `docker compose down -v` remove apenas
      # named volumes e volumes anônimos — um diretório do host sobrevive por
      # construção (o incidente de perda de dados da PCA em 2026-07-28 é o
      # porquê desta linha). O caminho relativo resolve a partir do diretório
      # do compose.yml e DEVE começar com ./ — sem o prefixo, o Compose
      # interpretaria o valor como nome de volume.
      - ${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data

# REMOVER o bloco de topo:
# volumes:
#   pgdata:
```

Fatos verificados que sustentam o pattern:
- `docker compose down -v`: "Remove named volumes declared in the 'volumes' section of the Compose file and anonymous volumes attached to containers" — bind mounts não são mencionados nem afetados [VERIFIED: docs.docker.com/reference/cli/docker/compose/down].
- Short syntax cria o diretório host ausente: "the short syntax creates a directory at the source path on the host if it doesn't exist" [VERIFIED: docs.docker.com/reference/compose-file/services #volumes]. **Nenhum passo de `mkdir` é necessário** no README/entrypoint (responde a discretion "se precisa de passo de criação").
- Caminho relativo resolve a partir do diretório do compose file e deve começar com `.` ou `..` para não ser ambíguo com named volume [VERIFIED: docs.docker.com/reference/compose-file/services].
- postgres:17: `ENV PGDATA /var/lib/postgresql/data`, `VOLUME /var/lib/postgresql/data`, usuário `postgres` uid=999 gid=999 [VERIFIED: Dockerfile docker-library/postgres 17/bookworm].
- Montar em `/var/lib/postgresql/data` (não `/var/lib/postgresql`) é a orientação oficial para ≤17 [CITED: docker-library/docs postgres content.md].
- initdb roda só com diretório de dados vazio; banco pré-existente é deixado intacto [CITED: hub.docker.com/_/postgres].

### Pattern 2: `.env.example.jinja` com default comentado (D-50/D-76)

```bash
# Fonte: padrão existente do próprio .env.example.jinja
# Diretório do host onde o PostgreSQL grava os dados (bind mount).
# O default relativo vive no compose (${PGDATA_DIR:-./dados/pg}); descomente
# apenas para apontar outro caminho — sempre com ./ inicial ou absoluto.
# PGDATA_DIR=./dados/pg
```

### Pattern 3: Contrato de arquivo fixo para logos (D-65/D-66)

```html
{# Fonte: padrão do manifest_view (static() + hashing WhiteNoise já resolvido) #}
{# shell.html — cabeçalho da aside (D-68): logo do subsistema junto à sigla #}
<img src="{% static 'img/logo-subsistema.svg' %}"
     alt="Logo de {{ sistema_sigla }}" class="h-8 w-8 flex-none">

{# login.html — acima do formulário (D-69): logo da entidade #}
<img src="{% static 'img/logo-entidade.svg' %}"
     alt="Logo institucional" class="h-12 mx-auto mb-4">
```

Pontos verificados:
- `ManifestStaticFilesStorage` hasheia TODOS os arquivos coletados, SVG incluído; `{% static %}` resolve o nome hasheado automaticamente — mesmo mecanismo já provado pelos ícones PNG do manifest (Pitfall 3 da Fase 2) [VERIFIED: comportamento já exercitado no repo em `manifest_view` + `test_pwa.py`].
- SVG referenciado via `<img>` não executa scripts embutidos (contexto de imagem) — adequado para arquivo controlado pelo operador [CITED: comportamento padrão de navegadores; ver Security Domain].
- `alt` sempre presente (D-67) usando os valores do context processor `identidade`.

### Pattern 4: Placeholder SVG neutro (discretion — recomendação)

SVG estático não pode interpolar `sistema_sigla` (é arquivo, não template) — o placeholder deve ser **forma geométrica neutra sem texto de marca** (o texto identitário continua ao lado, D-67). Manter `viewBox` e nenhum `width/height` fixo (dimensionamento via classes Tailwind no `<img>`). Conteúdo 100% neutro: qualquer string de marca no SVG reprovaria no scan de identidade proibida do `test_04_03_identity.py` (que varre TODO arquivo do sistema gerado procurando "CFC", "Sistema Base", "PCA"...).

```xml
<!-- Ex.: logo-entidade.svg — círculo/escudo neutro em currentColor-like cinza -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img">
  <!-- Placeholder neutro (D-66): substitua este arquivo pela arte oficial
       mantendo o nome logo-entidade.svg — nenhuma edição de código. -->
  <circle cx="32" cy="32" r="30" fill="none" stroke="#9ca3af" stroke-width="4"/>
  <path d="M32 14v36M14 32h36" stroke="#9ca3af" stroke-width="4"/>
</svg>
```

(Desenho exato é discretion do planner/executor; o requisito duro é: neutro, renderiza em fundo claro, viewBox presente.)

### Anti-Patterns to Avoid

- **Variável `.env` para caminho de logo:** D-65 veta — o nome fixo é o contrato.
- **SVG inline nos templates:** quebraria "substituir arquivo sem editar código".
- **`volumes:` de topo com `external: true`:** é o padrão da PCA, mas D-73 travou bind mount; não misturar as duas abordagens.
- **PGDATA_DIR sem `./`:** valor `dados/pg` seria tratado como named volume — documentar o prefixo obrigatório no `.env.example`.
- **Automatizar migração de dados no `copier update`:** D-40 (zero automatismo) — a migração named volume → bind mount é nota de documentação, nunca script pós-geração.
- **Nova variável Copier para logos/dados:** expectativa explícita do CONTEXT: NENHUMA (conferir `copier.yml` só para o `_exclude` do `.gitignore`).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Criar diretório de dados no host | Passo de `mkdir -p` no entrypoint/README | Short syntax do Compose (cria automaticamente) | Verificado nas docs; menos um passo manual = preserva QA-02 |
| Ajustar permissões do diretório de dados | Script de `chown 999` | Entrypoint oficial do postgres (inicia como root, ajusta ownership e faz step-down via gosu) | Comportamento do entrypoint oficial; documentar uid 999 só como troubleshooting (D-74) |
| Rasterizar SVG → PNG para ícones PWA | Extensão do `gerar_icones_pwa.py` com cairosvg/rsvg | Manter o gerador atual (Pillow, sigla+cor) e documentar a substituição manual dos 3 PNGs | Rasterização de SVG exigiria dependência nova no host; discretion — recomendação: NÃO estender nesta fase |
| Cache busting dos logos | Sufixo de versão manual no nome do arquivo | WhiteNoise manifest hashing via `{% static %}` | Já resolvido no repo (mesmo padrão dos ícones) |

**Key insight:** os dois eixos da fase são configuração e convenção sobre mecanismos que o repo já provou — o valor está na documentação centralizada e nos testes de regressão, não em código novo.

## Runtime State Inventory

> Incluído porque a fase migra o layout de armazenamento (named volume → bind mount).

| Categoria | Itens encontrados | Ação requerida |
|----------|-------------------|----------------|
| Dados armazenados | Named volume `<slug>_pgdata` em sistemas já gerados/nascidos (e `nascimento<pid>_pgdata` se algum ensaio `--keep` da Fase 5 estiver retido) | Nota de migração documentada (ver Open Question 1 / Pitfall 6); template em si não tem banco |
| Config de serviço vivo | Nenhuma — verificado: compose é o único orquestrador; não há serviços externos referenciando `pgdata` | none |
| Estado registrado no SO | Nenhum — verificado: sem systemd/cron no host (backup roda em container) | none |
| Secrets/env vars | `PGDATA_DIR` é variável NOVA e opcional com default no compose — nenhum secret renomeado | Adicionar comentada ao `.env.example.jinja` |
| Artefatos de build | Imagem `web` embute os estáticos no build (`collectstatic` no Dockerfile) — logo trocado só aparece em produção após `up -d --build` | Documentar na seção "Customização de marca" |

## Common Pitfalls

### Pitfall 1: Limpeza do tracer falha em arquivos uid 999
**What goes wrong:** `test_05_nascimento.sh` faz `rm -rf "${TMP}"` no `limpar()`; com bind mount, `${DESTINO}/dados/pg` é criado pelo initdb com owner 999:999 e mode 700 — o usuário host não consegue remover, deixando lixo em `/tmp` a cada execução (o `rm -rf` falha silenciosamente porque o trap não checa).
**Why it happens:** bind mount expõe no host arquivos criados por outro uid dentro do container.
**How to avoid:** antes do `rm -rf`, remover o diretório de dados via container root: `docker run --rm -v "${DESTINO}:/alvo" postgres:17 rm -rf /alvo/dados` (a imagem já está no host — o tracer acabou de usá-la). Alternativa sem pull extra: `compose run --rm --user root --entrypoint sh db -c 'rm -rf /var/lib/postgresql/data/*'` antes do `down` — mas o `docker run` direto pós-`down` é mais simples e robusto.
**Warning signs:** diretórios `nascimento*` acumulando em `/tmp` após execuções do tracer.

### Pitfall 2: `PGDATA_DIR` sem prefixo `./` vira named volume
**What goes wrong:** operador põe `PGDATA_DIR=dados/pg` no `.env`; o Compose trata como nome de volume (inexistente) e falha — ou pior, cria volume com nome estranho.
**Why it happens:** short syntax distingue bind de named volume pelo prefixo `.`/`..`/`/` [VERIFIED: docs.docker.com].
**How to avoid:** comentário no `.env.example.jinja` exigindo `./` inicial ou caminho absoluto; teste de template pode assertar o default com `./`.

### Pitfall 3: Sistemas gerados NÃO recebem `.gitignore` hoje
**What goes wrong:** D-74 manda `dados/` para o `.gitignore` do sistema gerado — mas `.gitignore` está no `_exclude` do `copier.yml`, então o sistema gerado nasce sem `.gitignore` NENHUM. Sem correção, um `git add .` no sistema gerado commitaria o banco inteiro (e o `.env`!).
**Why it happens:** `_exclude` aplica ao caminho de DESTINO (comentário verificado no próprio `copier.yml`) — excluir `.gitignore` bloqueia qualquer arquivo que renderize para esse nome.
**How to avoid:** seguir o precedente documentado do `README.md.jinja`: remover `.gitignore` do `_exclude` e criar `.gitignore.jinja` (conteúdo para o sistema gerado, incluindo `.env`, `dados/`, `staticfiles/` etc.); o `.jinja` renderizado substitui o `.gitignore` verbatim do template durante a cópia — exatamente como o README. Adicionar `dados/` também ao `.gitignore` do template (D-74). **Atenção:** o scan do `test_04_03_identity.py` passa a varrer o `.gitignore` gerado — manter conteúdo neutro.
**Warning signs:** `copier copy` de teste sem `.gitignore` no destino; `git status` do sistema gerado listando `dados/`.

### Pitfall 4: `copier update` em sistema vivo abandona os dados no named volume
**What goes wrong:** sistema nascido antes da Fase 6 roda `copier update`; o compose novo aponta para `./dados/pg` vazio; o próximo `down && up -d` inicializa um banco NOVO e vazio — o app "perde" todos os dados (que continuam no volume `<slug>_pgdata`, órfão).
**Why it happens:** bind mount e named volume são armazenamentos distintos; nada copia dados entre eles.
**How to avoid:** nota obrigatória na seção "Atualizações do template" do `README.md.jinja` (e/ou MIGRACAO.md): ANTES do primeiro `up` pós-update, migrar com dump/restore (caminho canônico D-75) ou cópia direta: `docker run --rm -v <slug>_pgdata:/de -v "$(pwd)/dados/pg:/para" postgres:17 sh -c 'cp -a /de/. /para/'` com a stack parada. Depois, `docker volume rm <slug>_pgdata` opcional.
**Warning signs:** app subindo com banco vazio após update; `docker volume ls` mostrando `<slug>_pgdata` remanescente.

### Pitfall 5: Logo trocado "não aparece" em produção
**What goes wrong:** operador substitui `logo-entidade.svg` e recarrega a página — nada muda em produção.
**Why it happens:** `collectstatic` roda no BUILD da imagem (Dockerfile L44-50); o container serve os estáticos hasheados embutidos na imagem antiga. Em dev (`DEBUG` + finders) a troca é imediata — mascarando o passo.
**How to avoid:** documentar na seção "Customização de marca": em produção, trocar logo = substituir arquivo + `docker compose up -d --build`. (Mesma regra já vale para os ícones PWA.)
**Warning signs:** logo novo em dev, antigo em produção.

### Pitfall 6: PGDATA_DIR apontando para mountpoint de disco (lost+found)
**What goes wrong:** operador aponta `PGDATA_DIR` para a raiz de um disco montado; initdb recusa diretório não-vazio (contém `lost+found`).
**Why it happens:** initdb exige diretório vazio; `lost+found` conta como conteúdo. [ASSUMED — orientação clássica das docs oficiais do postgres; a versão atual das docs foca no caso ≥18]
**How to avoid:** nota de troubleshooting: usar SEMPRE um subdiretório (`/mnt/disco/pg`, nunca `/mnt/disco`). O default `./dados/pg` já é subdiretório — sem risco no caminho feliz. **Não** é preciso setar `PGDATA` env nem subdir interno no container para o default desta fase.
**Warning signs:** log do db: "initdb: error: directory ... exists but is not empty".

### Pitfall 7: SELinux nega acesso ao bind mount
**What goes wrong:** em hosts RHEL/Fedora com SELinux enforcing, o postgres recebe "Permission denied" no bind mount.
**Why it happens:** contexto SELinux do diretório host não permite acesso do container (exigiria flag `:z`/`:Z`). [ASSUMED — comportamento documentado do Docker em distros SELinux]
**How to avoid:** o alvo do template é Debian/Ubuntu (MIGRACAO.md exige VM Debian/Ubuntu) — não adicionar `:Z` no compose (relabel indevido em outros cenários); no máximo uma linha de troubleshooting.
**Warning signs:** erro de permissão mesmo com ownership 999 correto.

### Pitfall 8: postgres:18 muda o mount point
**What goes wrong:** um futuro bump para postgres:18 quebraria a persistência silenciosamente: em ≥18 o `VOLUME`/layout muda para `/var/lib/postgresql` (PGDATA `/var/lib/postgresql/18/docker`), e montar em `/var/lib/postgresql/data` deixa de ser o caminho certo.
**Why it happens:** mudança oficial da imagem em 18+ [CITED: docker-library/docs postgres].
**How to avoid:** comentário no compose fixando a relação "postgres:17 ↔ /var/lib/postgresql/data"; qualquer upgrade de major é migração deliberada (dump/restore), nunca troca de tag.

### Pitfall 9: `POSTGRES_INITDB_ARGS` (ICU pt-BR) só vale para diretório vazio
**What goes wrong:** expectativa de que trocar `PGDATA_DIR` "reconfigure" locale — não: initdb só roda em diretório vazio; dados existentes mantêm o locale original.
**How to avoid:** nenhuma ação — apenas não prometer reconfiguração na documentação. Comportamento igual ao do named volume atual.

## Code Examples

### Asserções de teste sugeridas — suíte Django (estilo test_pwa.py/test_shell.py: pt-BR, asserts contra settings/static(), nunca literais de identidade)

```python
# Fonte: padrão de core/tests/test_pwa.py (static() resolvido, hashing-safe)
from django.templatetags.static import static

def test_shell_referencia_logo_do_subsistema_via_static(self):
    client = Client()
    client.force_login(self.user)
    conteudo = client.get("/").content.decode("utf-8")
    # D-68: logo do subsistema no cabeçalho da aside — sempre via static(),
    # nunca caminho literal (hashing do WhiteNoise, Pitfall 3 da Fase 2).
    self.assertIn(static("img/logo-subsistema.svg"), conteudo)

def test_login_referencia_logo_da_entidade_via_static(self):
    conteudo = Client().get("/login/").content.decode("utf-8")
    self.assertIn(static("img/logo-entidade.svg"), conteudo)

# Existência/validade dos SVGs — espírito do IconesPWATests (sem lib nova):
def test_placeholders_svg_existem_e_sao_svg(self):
    for nome in ("logo-entidade.svg", "logo-subsistema.svg"):
        texto = (self.DIRETORIO_IMG / nome).read_text(encoding="utf-8")
        self.assertIn("<svg", texto)
        self.assertIn("viewBox", texto)
```

### Asserções de teste sugeridas — template-tests (host, unittest, estilo test_04_03_identity.py)

```python
# Fonte: padrão de leitura direta dos .jinja em .template-tests/
def test_compose_usa_bind_mount_com_default_relativo(self):
    compose = (ROOT / "compose.yml.jinja").read_text(encoding="utf-8")
    self.assertIn("${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data", compose)
    # O bloco de topo `volumes:` com pgdata não pode voltar:
    self.assertNotIn("pgdata:/var/lib/postgresql/data", compose)

def test_env_example_documenta_pgdata_dir(self):
    env = (ROOT / ".env.example.jinja").read_text(encoding="utf-8")
    self.assertIn("PGDATA_DIR", env)
```

### Atualização do tracer — limpeza e (opcional) prova do critério C4

```sh
# Fonte: limpar() de .template-tests/test_05_nascimento.sh — inserir ANTES do rm -rf:
# O initdb grava ./dados/pg como uid 999; o usuário host não consegue
# removê-lo — a limpeza precisa de um container root (a imagem postgres:17
# já está local, o próprio tracer acabou de usá-la).
if [ -d "${DESTINO}/dados" ]; then
    docker run --rm -v "${DESTINO}:/alvo" postgres:17 rm -rf /alvo/dados >/dev/null 2>&1 || true
fi

# Prova direta do critério de sucesso 4 (recomendada, antes do SUCESSO=true):
compose down --volumes
compose up -d db web
aguardar_web
compose exec -T web python manage.py shell -c \
    "from django.contrib.auth import get_user_model; get_user_model().objects.get(email='nascimento@example.invalid')" || \
    falhar 'dados não sobreviveram a down -v && up -d'
```

### Migração named volume → bind mount (nota de documentação, D-40: manual)

```sh
# Fonte: técnica padrão de cópia entre volume e host via container efêmero.
# Com a stack PARADA (docker compose down, SEM -v):
docker run --rm \
  -v <slug>_pgdata:/de \
  -v "$(pwd)/dados/pg:/para" \
  postgres:17 sh -c 'cp -a /de/. /para/'
docker compose up -d
# Confirmado o sistema saudável, remova o volume antigo:
# docker volume rm <slug>_pgdata
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Named volume `pgdata` gerenciado pelo Compose (Fase 1, Assumption A4) | Bind mount `${PGDATA_DIR:-./dados/pg}` | Esta fase (D-73) | `down -v` deixa de ser destrutivo; dados visíveis no diretório do projeto |
| PCA produção: named volume `external: true` (pós-incidente 2026-07-28) | Template: bind mount | D-73 | Mesma garantia sem passo manual de `docker volume create` |
| postgres ≤17: mount em `/var/lib/postgresql/data` | postgres ≥18: mount em `/var/lib/postgresql` (PGDATA versionado) | postgres 18 (2025) | Upgrade de major da imagem = migração deliberada; comentar no compose |

**Deprecated/outdated:** nada a remover; `ops/gerar_icones_pwa.py` permanece como está (recomendação: não estender).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Entrypoint do postgres:17, iniciando como root, faz chown do diretório de dados para 999 e step-down via gosu — diretório vazio criado pelo engine (root:root) funciona sem intervenção | Pattern 1 / Don't Hand-Roll | Baixo: se falhasse, o `up` erraria imediatamente no tracer; comportamento amplamente documentado e o repo nunca define `user:` no serviço db |
| A2 | Orientação "use subdiretório quando o alvo é mountpoint com lost+found" segue válida em 17 (docs atuais focam ≥18) | Pitfall 6 | Baixo: é nota de troubleshooting, não caminho feliz |
| A3 | SELinux exige `:z/:Z` em RHEL/Fedora | Pitfall 7 | Baixo: alvo declarado do template é Debian/Ubuntu |
| A4 | Rendered `.gitignore.jinja` substitui o `.gitignore` verbatim do template na cópia (precedente README.md.jinja) | Pitfall 3 | Médio: se a colisão se comportar diferente, o teste de template detecta; validar com `copier copy` de fumaça no plano |

## Open Questions

1. **Migração de sistemas já nascidos (named volume → bind mount): documentar onde?**
   - What we know: nenhum sistema de produção usa o template ainda (Orçamento será o primeiro); o único ambiente vivo é o ensaio `--keep` da Fase 5 (efêmero, re-executável). A PCA não usa o template.
   - What's unclear: se vale gastar seção inteira de runbook para um cenário hoje hipotético.
   - Recommendation: nota curta na seção "Atualizações do template" do `README.md.jinja` com o one-liner de cópia (ver Code Examples) + reforço de que dump/restore é o caminho canônico (D-75). Não criar script (D-40).
2. **Favicon (discretion):** browsers pedem `/favicon.ico`; hoje a request cai no `LoginRequiredMiddleware` (302 ruidoso e inofensivo). Recomendação: adicionar `<link rel="icon" href="{% static 'img/icon-192.png' %}">` no `base.html` — zero arquivo novo, segue contrato existente. Decisão fica com o planner.
3. **PNG como formato alternativo de logo (discretion):** recomendação: NÃO aceitar — o contrato é nome+extensão fixos (`<img src>` aponta para `.svg`). Documentar uma linha: "tem só PNG? converta para SVG embrulhando com `<image>` ou exporte da arte vetorial original".

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker Engine + Compose | tracer, verificação do compose | ✓ | 29.5.2 | — |
| Imagem postgres:17 | tracer / limpeza via container | ✓ (local) | 17 / 17.11 | pull automático |
| python3 | template-tests | ✓ | 3.14.4 | — |
| Copier (`.venv-template`) | tracer / testes de template | ✓ | 9.17.1 (versão exigida pelo tracer) | — |
| Pillow (host) | só se regenerar ícones (não requerido nesta fase) | — | — | não necessário |

**Missing dependencies with no fallback:** nenhuma.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | fase não toca auth |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | marginal | `PGDATA_DIR` é interpolação do Compose (não chega ao Django); logos são arquivos confiáveis do operador, não input de usuário |
| V6 Cryptography | no | — |

### Known Threat Patterns for este stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Dados do banco commitados no git (bind mount dentro do repo) | Information Disclosure | `dados/` no `.gitignore` do sistema gerado E do template (D-74) — inclui corrigir a ausência total de `.gitignore` gerado (Pitfall 3) |
| SVG com script servido como estático (XSS se aberto diretamente na origem) | Elevation of Privilege | Logos são arquivos confiáveis do operador (upload via admin foi deliberadamente adiado); referência sempre via `<img>` (não executa script); nota na documentação: usar SVG limpo/exportado, não de fonte não confiável |
| Diretório de dados legível por outros usuários do host | Information Disclosure | initdb aplica mode 700 no diretório de dados; documentar uid 999 para troubleshooting (D-74) |

## Sources

### Primary (HIGH confidence)
- Codebase local (verificado nesta sessão): `compose.yml.jinja`, `copier.yml` (`_exclude` com `.gitignore`), `core/views.py::manifest_view`, `core/templates/core/{shell,login,_login_form}.html`, `core/templates/base.html`, `config/settings/base.py.jinja` (STORAGES WhiteNoise), `Dockerfile` (collectstatic no build), `core/tests/{test_shell,test_pwa}.py`, `.template-tests/{test_05_nascimento.sh,test_04_03_identity.py}`, `ops/{gerar_icones_pwa.py,MIGRACAO.md.jinja}`, `/opt/web/pca/compose.yml` (somente leitura — named volume `external: true` + registro do incidente 2026-07-28)
- docs.docker.com/reference/cli/docker/compose/down — semântica exata do `-v` (só named/anonymous volumes)
- docs.docker.com/reference/compose-file/services (#volumes) — resolução de caminho relativo, `create_host_path`, distinção bind × named volume
- raw.githubusercontent.com/docker-library/postgres/master/17/bookworm/Dockerfile — uid/gid 999, `ENV PGDATA`, `VOLUME`

### Secondary (MEDIUM confidence)
- hub.docker.com/_/postgres e docker-library/docs (content.md) — initdb só em diretório vazio; mount em `/var/lib/postgresql/data` para ≤17; mudança de layout em ≥18; notas de usuário arbitrário

### Tertiary (LOW confidence)
- Notas lost+found/PGDATA-subdir (versões anteriores das docs oficiais) e SELinux `:z/:Z` — usadas apenas como troubleshooting, marcadas [ASSUMED]

## Metadata

**Confidence breakdown:**
- Bind mount / semântica down -v: HIGH — verificado em docs oficiais + Dockerfile oficial da imagem
- Contrato de logos SVG + WhiteNoise: HIGH — mecanismo idêntico já provado no repo (ícones do manifest); padrões extraídos do código existente
- Impactos no tracer e no copier (`_exclude`/`.gitignore`): HIGH para o diagnóstico (lido do código), MEDIUM para a solução `.gitignore.jinja` (precedente documentado no próprio copier.yml, mas validar com `copier copy` de fumaça — Assumption A4)
- Pitfalls de troubleshooting (lost+found, SELinux): MEDIUM/LOW — marcados, não afetam o caminho feliz

**Research date:** 2026-08-19
**Valid until:** ~2026-09-18 (stack estável; atenção apenas a mudanças da imagem postgres)
