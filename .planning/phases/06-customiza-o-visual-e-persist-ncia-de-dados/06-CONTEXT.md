# Phase 6: Customização Visual e Persistência de Dados - Context

**Gathered:** 2026-08-19
**Status:** Ready for planning

<domain>
## Phase Boundary

O template ganha pontos de customização de marca claros, centralizados no app `core` e documentados: logo principal da entidade (ex.: CFC), logo do subsistema e logo/nome do PWA — cada um com um local único onde o operador insere/troca o arquivo ou valor, sem editar código. Além disso, os dados do PostgreSQL passam a persistir no host via bind mount: `docker compose down -v` (ou recriação dos containers) não perde dados.

**Atenção estrutural:** o repositório é um template Copier desde a Fase 4 — as mudanças desta fase tocam os arquivos-fonte do template (`compose.yml.jinja`, `README.md.jinja`, `.env.example.jinja`, `core/` etc.) e devem preservar o princípio D-50 (".env primeiro, .jinja mínimo") e o fluxo `copier copy`/`copier update`.

Fora desta fase: upload de logos via admin (exigiria media storage — nova capacidade), SSO, qualquer conteúdo de domínio, alterações em `/opt/web/pca`.

</domain>

<decisions>
## Implementation Decisions

*(Modo `--auto`: decisões selecionadas automaticamente com a opção recomendada, ancoradas nas decisões D-16/D-17/D-20 da Fase 2 e D-50 da Fase 4. Numeração continua de D-64.)*

### Mecanismo e local dos logos (entidade + subsistema)
- **D-65:** Logos são **arquivos estáticos em caminhos fixos e documentados** no core: `core/static/img/logo-entidade.svg` (logo principal da entidade, ex.: CFC) e `core/static/img/logo-subsistema.svg` (logo do sistema específico). Customizar = substituir o arquivo mantendo nome e extensão — nenhuma edição de código, nenhuma variável nova. Sem upload via admin (media storage é nova capacidade, fora do escopo) e sem caminho configurável via `.env` (indireção desnecessária; o nome fixo É o contrato).
- **D-66:** O template entrega **placeholders neutros em SVG** nos dois caminhos (sem marca de domínio — TPL-04), no espírito dos ícones PWA placeholder (D-20). Os templates sempre referenciam os arquivos via `{% static %}`; nunca há referência quebrada num sistema recém-nascido.
- **D-67:** Os placeholders SVG podem ser simples (ex.: monograma com a sigla/forma neutra) e devem renderizar bem em fundo claro do shell/login. Texto (`sistema_nome`/`sistema_sigla`) permanece ao lado/abaixo dos logos — o logo complementa a identidade textual (D-16), não a substitui (acessibilidade: `alt` sempre presente).

### Posicionamento dos logos no UI
- **D-68:** **Logo do subsistema** aparece no cabeçalho da aside do shell (junto à sigla/nome, hoje texto puro em `shell.html`) e no header mobile da gaveta. É a identidade "deste sistema".
- **D-69:** **Logo da entidade** aparece na tela de login (acima do formulário, identidade institucional) e discretamente no rodapé da aside do shell. É a identidade "da casa" comum a toda a família.
- **D-70:** O **admin não ganha logo** — mantém a identidade por nome/cor via override cirúrgico existente (D-14). Qualquer mudança no admin além disso está fora.

### PWA — logo e nome
- **D-71:** O **nome do PWA já é customizável** e permanece como está: `SISTEMA_NOME`/`SISTEMA_SIGLA` no `.env` → settings → `manifest_view` (D-16/D-18). Esta fase não muda o mecanismo — apenas o documenta como O local de customização do nome do PWA.
- **D-72:** O **logo do PWA** segue o contrato de arquivos fixos: `core/static/img/icon-192.png`, `icon-512.png`, `icon-512-maskable.png`. Customizar = substituir esses três arquivos pela arte oficial (derivada do logo do subsistema) **ou** regenerar os placeholders com `ops/gerar_icones_pwa.py` (lê sigla/cor do `.env`). Nomes de arquivo do manifest não mudam (compatibilidade com hashing do WhiteNoise via `static()` já resolvida).

### Persistência do banco no host
- **D-73:** O serviço `db` troca o named volume `pgdata` por **bind mount para diretório no host**, com caminho configurável via `.env` (`PGDATA_DIR`, aplicando D-50) e **default relativo ao diretório do projeto** (ex.: `./dados/pg`). Bind mounts não são removidos por `docker compose down -v` — os dados sobrevivem por construção.
- **D-74:** O diretório de dados entra no `.gitignore` do sistema gerado (e do template). Documentar o requisito de permissões do PostgreSQL no container (o initdb ajusta ownership do diretório vazio; documentar uid/gid se necessário para troubleshooting).
- **D-75:** A **invariante de portabilidade é preservada e reforçada**: o runbook de migração (dump + `.env` + `compose up`) continua o caminho canônico; o bind mount adiciona a garantia de que operações rotineiras de compose (down -v, recriação) jamais destroem dados. `MIGRACAO.md` e README ganham nota sobre o novo layout de dados.
- **D-76:** Mudança aplicada no **`compose.yml.jinja`** (fonte do template) e refletida no `.env.example.jinja` (variável `PGDATA_DIR` com default comentado). Healthcheck e demais serviços (web, backup) permanecem intactos.

### Documentação da customização
- **D-77:** Uma **seção única "Customização de marca"** no `README.md.jinja` (README do sistema gerado) lista TODOS os pontos de customização em um só lugar: logo da entidade (arquivo), logo do subsistema (arquivo), ícones/nome do PWA (arquivos + `.env`), cor primária (`.env` + `tailwind.config.js`), nome/sigla (`.env`). O `core/README.md` referencia os mesmos pontos como convenção do core.
- **D-78:** O `README.md` do template (raiz) atualiza o passo a passo do nascimento para incluir a etapa opcional "inserir logos oficiais" e a nota sobre persistência dos dados no host.

### Claude's Discretion
- Desenho exato dos placeholders SVG (monograma, forma geométrica neutra) e dimensões/classes Tailwind de exibição.
- Aceitar PNG como formato alternativo dos logos (e como documentar isso sem quebrar o contrato de nome fixo).
- Favicon derivado dos ícones existentes (se entrar, segue o mesmo contrato de arquivo fixo).
- Estender `ops/gerar_icones_pwa.py` para gerar ícones a partir do arquivo de logo do subsistema (opcional, não obrigatório).
- Nome exato da variável (`PGDATA_DIR` ou similar) e do diretório default de dados (`./dados/pg` ou similar), e se o `entrypoint`/README precisa de passo de criação do diretório.
- Testes: quais asserções entram (presença dos arquivos de logo nos templates renderizados, manifest, config do compose).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Arquivos do template a tocar nesta fase
- `compose.yml.jinja` — serviço `db` com named volume `pgdata` (linhas do `volumes:`) a trocar por bind mount configurável (D-73..D-76)
- `.env.example.jinja` — ganha `PGDATA_DIR` (ou similar) com default; já concentra a identidade (`SISTEMA_NOME`/`SISTEMA_SIGLA`/`COR_PRIMARIA`)
- `core/templates/core/shell.html` — cabeçalho da aside (hoje `{{ sistema_sigla }}`/`{{ sistema_nome }}` texto puro) recebe o logo do subsistema (D-68); rodapé recebe logo da entidade (D-69)
- `core/templates/core/login.html` + `core/templates/core/_login_form.html` — tela de login recebe o logo da entidade (D-69)
- `core/static/img/` — hoje só ícones PWA (`icon-192.png`, `icon-512.png`, `icon-512-maskable.png`); ganha `logo-entidade.svg` e `logo-subsistema.svg` placeholders (D-65/D-66)
- `core/views.py` — `manifest_view` (D-18) referencia os ícones via `static()`; NÃO muda, mas é o contrato do nome do PWA (D-71/D-72)
- `ops/gerar_icones_pwa.py` — gerador de placeholders dos ícones PWA, citado na documentação de customização (D-72)
- `README.md.jinja` — ganha a seção "Customização de marca" (D-77)
- `README.md` (raiz, doc do template) — passo opcional de logos no nascimento + nota de persistência (D-78)
- `core/README.md` — convenções do core; referencia os pontos de customização (D-77)
- `ops/MIGRACAO.md` (se existir no template) — nota sobre layout de dados no host (D-75)
- `copier.yml` — conferir `_exclude` e se alguma variável nova é necessária (expectativa: NENHUMA variável Copier nova — logos são arquivos substituídos pós-nascimento, dados são `.env`; D-50)
- `.gitignore` — diretório de dados do bind mount (D-74)

### Decisões anteriores que governam esta fase
- `.planning/phases/02-shell-visual-e-kernel/02-CONTEXT.md` — D-16 (identidade via settings/.env), D-17 (dois touchpoints de cor), D-18 (manifest por view), D-20 (ícones placeholder substituíveis)
- `.planning/phases/04-templatiza-o-copier/04-CONTEXT.md` — D-50 (".env primeiro, .jinja mínimo"), D-38 (`_exclude`), D-40 (zero automatismo pós-geração), D-52 (ícones PWA no nascimento)
- `.planning/PROJECT.md` — invariantes: portabilidade (migração = dump + `.env` + compose up), zero menção a PCA/domínio (TPL-04), stack fechada
- `.planning/REQUIREMENTS.md` — requisitos v1 completos; esta fase é pós-v1 (roadmap: Requirements TBD)

### Fonte de extração (somente leitura — NUNCA modificar)
- `/opt/web/pca/compose.yml` — referência de como a PCA monta volumes em produção (conferir se usa named volume ou bind; a decisão D-73 vale independentemente)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `core/context_processors.py` (`identidade`) — expõe `sistema_nome`/`sistema_sigla`/`cor_primaria` a todos os templates; os logos não precisam de context processor (referência estática direta), mas o `alt` dos logos usa esses valores.
- `core/views.py::manifest_view` — nome/short_name do PWA 100% via settings; ícones via `static()` (compatível com hashing WhiteNoise). Mecanismo pronto — só documentar.
- `ops/gerar_icones_pwa.py` — já gera os 3 ícones placeholder a partir de sigla/cor do `.env`; roda no host, PNGs commitados.
- `compose.yml.jinja` — já usa interpolação de env (`${POSTGRES_DB}` etc.); `PGDATA_DIR` com default (`${PGDATA_DIR:-./dados/pg}`) segue o padrão existente.

### Established Patterns
- Comentários em pt-BR explicando o porquê (estilo da casa).
- Identidade com fonte única (`.env` → settings → templates) — os logos estendem o padrão com "arquivo fixo → `{% static %}`".
- Zero automatismo pós-geração (D-40): inserir logos oficiais é passo manual documentado do nascimento, como os ícones (D-52).
- Suíte de testes existente cobre shell, login e PWA (`core/tests/test_shell.py`, `test_login_flow.py`, `test_pwa.py`) — asserções novas seguem esses arquivos.

### Integration Points
- `shell.html` (aside + gaveta mobile) e `login.html`/`_login_form.html` — pontos de inserção dos logos.
- `compose.yml.jinja` serviço `db` + seção `volumes:` — ponto único da mudança de persistência.
- `README.md.jinja` §Customização + `README.md` raiz §Nascimento — pontos de documentação.
- Tracer de nascimento `.template-tests/test_05_nascimento.sh` (Fase 5) — se a mudança de volume afetar o ensaio, o tracer é o teste de regressão do fluxo completo.

</code_context>

<specifics>
## Specific Ideas

- Pedido explícito do usuário: deve ficar **claro onde inserir** cada customização — logo principal da entidade, logo do subsistema, logo e nome do PWA — e isso deve viver **no `core`**.
- Pedido explícito e SUPER IMPORTANTE: os dados do banco devem ficar **no host**, persistindo a `docker compose down -v`.
- Critério operacional da fase: um operador que nunca viu o projeto encontra na documentação, em minutos, onde trocar cada logo e o nome do PWA; `docker compose down -v && docker compose up -d` num sistema gerado não perde nenhum dado.

</specifics>

<deferred>
## Deferred Ideas

- Upload de logos via admin (media storage + formulário) — nova capacidade, fase própria se algum dia for desejada.
- Variantes de logo para dark mode — o template não tem dark mode (decisão da Fase 2).

</deferred>

---

*Phase: 6-Customização Visual e Persistência de Dados*
*Context gathered: 2026-08-19*
