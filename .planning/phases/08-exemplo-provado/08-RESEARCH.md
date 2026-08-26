# Fase 8: Exemplo provado — Pesquisa

**Pesquisado:** 2026-08-26
**Domínio:** Fixture Django provado em cópia Copier real via harness existente (`.template-tests/`)
**Confiança:** ALTA — todos os fatos abaixo foram verificados por leitura direta dos arquivos do repositório nesta sessão; zero dependência nova, zero incógnita de ecossistema

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Modelagem de diárias e passagens
- **D-01:** Modelo único `Viagem` — sem entidades relacionadas. Campos na linha de: servidor, destino, período (datas), motivo, valor de diárias, valor de passagens, status. Todo o padrão do app exemplo (listagem paginada, filtros, modal 422, dashboard) se aplica direto sobre ele; capítulos mais curtos para a persona "sabe planilha, não sabe Django".
- **D-02:** Status simples via `choices` (ex.: Solicitada / Aprovada / Paga / Cancelada), `CharField` sem regras de transição. É o filtro principal da listagem e a dimensão categórica dos gráficos.
- **D-03:** Servidor/beneficiário como campo texto simples (`CharField`) — zero acoplamento com o auth do core; é o que uma planilha faria.
- **D-04:** `Viagem` registrada na auditoria com `HistoricalRecords()` — o fixture segue a convenção declarada do template (`core/README.md`), e o guia ensina auditoria como parte natural do modelo.

### Claude's Discretion
- Campos exatos, verbose names, validações e dados de seed do fixture — desde que respeitem D-01–D-04 e as invariantes do projeto (pt-BR, datas DD/MM/AAAA, moeda R$).
- Escopo detalhado das telas e do dashboard — ancorar no critério 4 do roadmap (modelo, admin, listagem paginada com filtros, modal 422/`HX-Trigger`, `_nav_dominio.html` com `{% item_nav %}`, dashboard ECharts com paleta da marca), espelhando os padrões do app exemplo.
- Forma de instalação do fixture na cópia e profundidade dos testes/smoke — guiar-se pela pesquisa do marco (`.planning/research/`) e pelos critérios de sucesso do roadmap.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRV-01 | O código do exemplo completo (fixture em `.template-tests/fixtures/`) instala numa cópia Copier real e passa: migração, testes do app e smoke das telas | Mecânica de instalação verificada: código é ASSADO na imagem (`COPY . .` no Dockerfile) → instalar exige editar a cópia + `compor up -d --build web`; harness `ensaio_django.sh` fornece `subir/testar/executar/compor`; receita completa de smoke com login por curl documentada abaixo |
| PRV-03 | Teste negativo prova que nenhum código de domínio (`apps/diarias`) chega ao template nem à cópia gerada | `copier.yml` `_exclude` cobre `.template-tests` (verificado); padrão de render leve em tempdir já existe em `test_04_04_optional_exemplo.py` e `test_07_nav_extensao.py`; asserções estruturais (não grep de palavra) recomendadas para sobreviver à Fase 9 |
</phase_requirements>

## Summary

A fase não tem incógnita de biblioteca: stack fechada, zero dependência nova. Toda a dificuldade é **mecânica de integração** entre quatro camadas que já existem: (1) o fixture novo em `.template-tests/fixtures/guia/`, (2) o harness `ensaio_django.sh` que mantém uma cópia Copier real viva com Docker Compose, (3) a cópia gerada onde `apps/diarias` será instalado, e (4) o container `web`, cuja imagem **assa o código** (`COPY . .` no Dockerfile — não há bind mount de código). Consequência central para o plano: instalar o fixture na cópia exige `docker compose up -d --build web` (rebuild da imagem), e o estágio de assets do Dockerfile (`COPY apps ./apps` + Tailwind JIT com glob `./apps/**/*.html`) garante que as classes dos templates do fixture entram no CSS compilado.

O segundo eixo é o **contrato de reúso do harness**: a impressão digital do banco de ensaio exclui `.planning` e `.template-tests` (verificado em `impressao_atual()`), portanto nem criar o fixture nem instalá-lo na cópia invalida o banco. Isso corta para os dois lados: o reúso continua barato, mas a suíte precisa ser **idempotente e detectar drift do fixture por conta própria** (banco reusado pode conter um `apps/diarias` desatualizado de uma execução anterior). Há também a armadilha documentada no próprio harness e em `test_07_cor_runtime.sh`: `garantir_banco()` faz UM único curl em `/healthz` sem retry — chamar `testar`/`executar`/`porta` logo depois de um `up -d --build` que ainda está subindo detona recriação completa do banco. A suíte captura porta/destino UMA vez e espera `/healthz` com laço próprio.

O teste negativo (PRV-03) não deve usar o banco de ensaio compartilhado (que ficará legitimamente "sujo" com o fixture instalado): usa o padrão já provado de render leve com Copier em `tempfile.TemporaryDirectory()` (segundos, sem Docker), e faz asserções **estruturais** — ausência do diretório `apps/diarias` e ausência dos bytes dos arquivos do fixture — nunca grep da palavra "diarias", que passará a existir legitimamente em `docs/guia/` na Fase 9.

**Primary recommendation:** duas suítes Python descobertas pelo `test_command` — `test_08_guia_vazamento.py` (render leve em tempdir, teste negativo, rápido) e `test_08_guia_prova.py` (usa `ensaio_django.sh subir` uma vez em `setUpClass`, instala o fixture de forma idempotente com detecção de drift, rebuilda o web, espera healthz com laço próprio, e então prova migração + `manage.py test apps.diarias` + smoke HTTP). O fixture vive como árvore literal `apps/diarias/` espelhando arquivo a arquivo o app exemplo, com migração `0001_initial.py` incluída.

## Project Constraints (from CLAUDE.md)

- **GSD Workflow Enforcement:** todo trabalho de edição passa por comando GSD (`/gsd-execute-phase` para trabalho de fase planejado); sem edições diretas fora do fluxo.
- Stack, convenções e arquitetura do CLAUDE.md ainda não populados — as convenções reais estão em `core/README.md`, `.planning/STATE.md` (decisões acumuladas) e no próprio código; o plano deve segui-las (listadas em "Architecture Patterns" abaixo).
- Idioma: pt-BR em toda documentação e artefato de planejamento (`.planning/config.json` → `"language": "pt-BR"`; decisão Init em STATE.md).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Guardar o código do app diárias | Fixture (`.template-tests/fixtures/guia/`) | — | Fonte da verdade; `_exclude` do copier.yml garante que nunca chega ao gerado [VERIFIED: copier.yml] |
| Gerar/reusar a cópia Copier real | Harness (`ensaio_django.sh`) | — | Já resolve render, .env, compose, healthz, fingerprint; a suíte NÃO reinventa [VERIFIED: leitura integral do script] |
| Instalar `apps/diarias` na cópia | Suíte `test_08_guia_prova.py` | Harness (`compor`) | São os mesmos passos que o leitor do guia fará à mão: copiar app, editar settings/urls/nav, rebuild |
| Rebuild da imagem web com o app novo | Container (Docker) | Suíte (dispara via `compor up -d --build web`) | Código é assado na imagem (`COPY . .`); Tailwind recompila com `./apps/**/*.html` no glob [VERIFIED: Dockerfile, tailwind.config.js] |
| Migração + testes do app | Container web (dentro da cópia) | Suíte (dispara via `compor exec -T`) | Único lugar honesto para exercitar Django — o checkout do template não é rodável [CITED: cabeçalho de ensaio_django.sh] |
| Smoke HTTP das telas | Host (curl/urllib da suíte → porta publicada) | — | Prova de ponta a ponta real: gunicorn + rota + middleware + banco |
| Teste negativo de vazamento | Suíte `test_08_guia_vazamento.py` (render leve em tempdir) | — | Independente de Docker; padrão idêntico a `test_04_04_optional_exemplo.py` |
| Descoberta pelas 13 suítes existentes | `test_command` (`unittest discover -p 'test_*.py'`) | — | Ambas as suítes novas são módulos `.py` no topo de `.template-tests/` [VERIFIED: config.json] |

## Standard Stack

### Core (tudo já existente — nenhuma instalação)

| Ferramenta | Versão | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Copier | 9.17.1 (`.venv-template/bin/copier`) | Render da cópia real (`--vcs-ref=HEAD`) | Versão travada por `exigir_copier()` no harness; `_min_copier_version: "9.17.1"` [VERIFIED: `copier --version` nesta sessão] |
| Docker + Compose | instalado, daemon OK | Subir db (postgres:17) + web (gunicorn) da cópia | `compose.yml.jinja` da cópia; harness embrulha com `--project-name`/`--env-file` [VERIFIED: `docker info` nesta sessão] |
| Python | 3.14.4 (host) / 3.12-slim (container) | unittest no host; Django dentro do container | `test_command` do projeto roda unittest no host [VERIFIED: `python3 --version`] |
| Django + django-simple-history | os do `requirements.txt` do template | O fixture é código Django idêntico em stack ao app exemplo | Stack fechada — decisão do marco: nenhuma dependência nova [CITED: .planning/research/SUMMARY.md] |
| curl | instalado | Smoke HTTP e espera de `/healthz` | Mesmo padrão de `test_05_nascimento.sh` e `test_07_cor_runtime.sh` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Rebuild da imagem (`up -d --build web`) | `docker compose cp` do app para dentro do container + `restart` | cp+restart é mais rápido mas cria container divergente da imagem: qualquer `up -d` posterior (ex.: o de restauração do test_07_cor_runtime.sh) recria o container SEM o app e o estado fica incoerente. Rebuild é o que o README ensina ao leitor (`docker compose up -d --build`) — didaticamente fiel e coerente. **Use rebuild.** |
| Suíte única | Duas suítes (`test_08_guia_vazamento.py` + `test_08_guia_prova.py`) | Suíte única acopla o teste negativo barato ao Docker caro. Duas suítes mantêm o padrão `test_08_guia*` do critério e deixam o negativo rodar mesmo com Docker indisponível. **Use duas.** |
| Smoke autenticado via curl com dança de CSRF | Só asserção de 302 → `/login/` | O 302 prova rota registrada mas não prova a tela renderizando. A combinação recomendada: 302 nas 3 telas (rota viva) + `manage.py test apps.diarias` dentro do container (200 com `force_login`, mesmo padrão de `test_crud.py`) + smoke autenticado por curl na listagem e no dashboard (ponta a ponta real). Receita completa abaixo. |

**Installation:** nenhuma — `pip install` de qualquer coisa está fora do escopo desta fase.

## Package Legitimacy Audit

**Nenhum pacote externo é instalado nesta fase.** Stack fechada por decisão do marco (SUMMARY.md: "Nenhuma dependência nova"). O fixture usa apenas dependências já presentes no `requirements.txt` do template (Django, django-simple-history etc.), que já estão assadas na imagem do container web. Slopcheck não aplicável.

## Architecture Patterns

### System Architecture Diagram

```
 .template-tests/fixtures/guia/apps/diarias/          (fonte da verdade, nunca renderizada pelo Copier)
        │
        │  test_08_guia_vazamento.py (SEM Docker)
        ├────────────────────────────────────────────────────────────┐
        │                                                            ▼
        │                                  copier copy → tempdir (cópia recém-nascida)
        │                                  asserções: apps/ == {__init__.py, exemplo/}
        │                                  nenhum arquivo da cópia == bytes de arquivo do fixture
        │
        │  test_08_guia_prova.py (setUpClass, uma vez)
        ▼
 ensaio_django.sh subir  ──►  captura ENSAIO_DESTINO / ENSAIO_PORTA / ENSAIO_PROJETO (UMA vez)
        │
        ▼
 instalar (idempotente, com detecção de drift por sha256):
   1. rsync/copytree fixture → DESTINO/apps/diarias
   2. patch config/settings/base.py  (+ "apps.diarias.apps.DiariasConfig",)
   3. patch config/urls.py           (+ path("diarias/", include("apps.diarias.urls")))
   4. patch core/templates/core/_nav_dominio.html (+ {% item_nav "diarias:..." ... %})
        │
        ▼ (só se algo mudou)
 compor up -d --build web  ──►  laço PRÓPRIO de curl /healthz (até 180×1s)
        │
        ▼
 compor exec -T web python manage.py migrate --noinput      (migração aplicada)
 compor exec -T web python manage.py test apps.diarias --noinput   (testes do app verdes)
 curl (host → porta publicada):
   • /diarias/, /diarias/dashboard/, /diarias/novo/ → 302 com Location=/login/?next=...
   • createsuperuser --noinput (env DJANGO_SUPERUSER_*) + login com CSRF → GET autenticado 200
```

### Recommended Fixture Structure

Espelho arquivo a arquivo do app exemplo (fonte: árvore real de `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/`), com a árvore EXATA que o leitor terá ao fim do guia:

```
.template-tests/fixtures/guia/
└── apps/
    └── diarias/
        ├── __init__.py
        ├── apps.py                      # name = "apps.diarias", DiariasConfig
        ├── models.py                    # Viagem (D-01..D-04), HistoricalRecords()
        ├── admin.py                     # SimpleHistoryAdmin (padrão exemplo/admin.py)
        ├── forms.py                     # ViagemForm com widgets Tailwind (padrão exemplo/forms.py)
        ├── views.py                     # listagem paginada + whitelist de ordenação + modal 422/HX-Trigger + dashboard
        ├── urls.py                      # app_name = "diarias"
        ├── migrations/
        │   ├── __init__.py
        │   └── 0001_initial.py          # INCLUÍDA no fixture (determinismo — ver Pitfall 6)
        ├── management/commands/seed_diarias.py   # padrão seed_exemplo.py, dados pt-BR de viagem
        ├── templates/diarias/
        │   ├── viagem_listar.html
        │   ├── _tabela_resultado.html
        │   ├── _filtros.html
        │   ├── _form_modal.html
        │   ├── _confirmar_exclusao_modal.html
        │   └── dashboard.html           # json_script paleta-graficos + ECharts (padrão exemplo)
        └── tests/
            ├── __init__.py
            ├── test_models.py
            ├── test_crud.py             # force_login, 422, HX-Trigger (padrão exemplo/tests/test_crud.py)
            └── test_dashboard.py
```

Os patches de settings/urls/nav NÃO são arquivos do fixture — são constantes nomeadas dentro de `test_08_guia_prova.py` (a Fase 9 poderá citá-las; o leitor fará essas edições à mão seguindo o guia).

### Pattern 1: Render leve em tempdir para o teste negativo
**What:** `copier copy --defaults --vcs-ref=HEAD` para um `tempfile.TemporaryDirectory()`, sem Docker.
**When to use:** PRV-03 e qualquer asserção sobre a cópia "recém-nascida".
**Example:** função `render()` de `test_04_04_optional_exemplo.py` / `test_07_nav_extensao.py` — copiar o padrão verbatim (inclusive `--vcs-ref=HEAD`, obrigatório porque o repo tem tag `v0.2.0` publicada e sem a flag o Copier renderiza a tag, não o HEAD). [VERIFIED: código-fonte das duas suítes]

### Pattern 2: Captura única de porta/destino + laço de espera próprio
**What:** chamar `ensaio_django.sh subir` UMA vez, parsear `ENSAIO_DESTINO/ENSAIO_PORTA/ENSAIO_PROJETO/ENSAIO_URL` da saída, e nunca mais chamar `subir/porta/url/destino`. Depois de qualquer `up -d`/`up -d --build`, esperar `/healthz` com laço próprio de curl (até 180 tentativas de 1s) antes de invocar `testar`/`executar`/`compor` de novo.
**When to use:** sempre que a suíte recriar/rebuildar o web.
**Why:** `garantir_banco()` faz UM único curl sem retry; chamado durante o boot, interpreta "não saudável" e detona `derrubar` + recriação completa com porta NOVA. [CITED: cabeçalho de test_07_cor_runtime.sh, verificado no código de ensaio_django.sh]

### Pattern 3: Instalação idempotente com detecção de drift
**What:** antes de instalar, comparar sha256 (caminho relativo + conteúdo — padrão `impressao_subarvore()` de `test_07_nav_extensao.py`) do fixture vs. `DESTINO/apps/diarias`. Três estados: ausente → instala tudo + patches + rebuild; idêntico → pula direto para migrate/testes/smoke (execução barata); divergente → ver Pitfall 5 (migrate zero com o código antigo antes de trocar). Patches de settings/urls/nav com guarda de idempotência (`if "apps.diarias" not in texto:`).
**Why:** a impressão digital do banco de ensaio EXCLUI `.template-tests` (`git ls-files ... ':!.template-tests'` em `impressao_atual()`) — mudar o fixture nunca recria o banco; a suíte é a única guarda contra fixture instalado obsoleto. [VERIFIED: função impressao_atual de ensaio_django.sh]

### Pattern 4: Restauração não é necessária — deixar instalado é o estado correto
**What:** ao fim da suíte, `apps/diarias` PERMANECE na cópia do banco de ensaio. Nenhuma suíte existente asserta ausência de domínio no banco compartilhado (test_07_cor_runtime só lê cores de `/login/`; test_copier_copy/update usam renders/clones próprios — verificado). Quando o template mudar, o fingerprint recria o banco limpo e a suíte reinstala.
**Why:** restaurar exigiria um SEGUNDO rebuild por execução (caro) e `migrate diarias zero`; o ganho é nulo. A contrapartida obrigatória: o teste negativo NUNCA olha o banco compartilhado (Pattern 1).

### Padrões do código do fixture (espelhar, não inventar)

Invariantes verificadas no app exemplo e nas decisões do STATE.md — o fixture replica todas:

- **Views:** `@login_required`; `Paginator(qs, 10)` server-side; whitelist de ordenação (`COLUNAS_ORDENACAO_PERMITIDAS`); filtros multi-seleção via `request.GET.getlist`; busca com `Q(...|...)`; `extrair_querystring_filtros` preservando filtros na paginação. [VERIFIED: exemplo/views.py]
- **Modal:** form inválido → `status=422`; sucesso → `resposta["HX-Trigger"] = "..."` (exemplo usa `itemSalvo`; o fixture usa nome próprio, ex.: `viagemSalva`). [VERIFIED: exemplo/views.py linhas 105–159]
- **Dashboard:** agregação 100% via ORM (`aggregate`/`annotate`) no PostgreSQL; `json_script` para dados e para `paleta_graficos`; paleta vem de `from core.tema import familia_marca` — **zero hex em template/JS**; chrome do gráfico lido de `getComputedStyle` no cliente; `<script src="{% static 'vendor/echarts.min.js' %}">`; `esc()` em TODA interpolação de formatter (decisão 07-12); `corCard`/`montarGraficos()` reconstruídos no evento `tema:alterado`. [VERIFIED: exemplo/templates/exemplo/dashboard.html + views.py]
- **Modelo:** `HistoricalRecords()` declarado no próprio modelo (D-04; convenção 4 de `core/README.md`); "hoje" sempre `timezone.localdate()` (convenção 1); `TextChoices` para status; `DecimalField(max_digits=12, decimal_places=2)` com `MinValueValidator`; verbose names em pt-BR minúsculo. [VERIFIED: exemplo/models.py + core/README.md]
- **Admin:** `SimpleHistoryAdmin` com `list_display/list_filter/search_fields/ordering`. [VERIFIED: exemplo/admin.py]
- **Nav:** linha no `_nav_dominio.html` da cópia com `{% item_nav "diarias:dashboard" ... %}` e `{% item_nav "diarias:viagem_listar" "..." "..." "/diarias/" "/diarias/dashboard/" %}` — o quinto argumento (exceções) evita dois `aria-current` simultâneos, exatamente como o exemplo faz com `/exemplo/dashboard/`. Arquivo já carrega `{% load navegacao %}` no topo. [VERIFIED: _nav_dominio.html.jinja renderizado]
- **Testes do app:** `force_login` + `reverse("diarias:...")`; asserção de 302 para anônimo; fragmento vs shell completo por header HTMX; 422 para form inválido — padrão integral de `exemplo/tests/test_crud.py`. [VERIFIED]

### Anti-Patterns to Avoid
- **Grep da palavra "diarias" como teste negativo:** quebrará na Fase 9 quando `docs/guia/` citar o app legitimamente. Asserções estruturais: diretório ausente + bytes de arquivo ausentes.
- **Melhorar a modelagem além de D-01–D-04:** o fixture é material didático; FK para servidor, workflow de status, entidades relacionadas — tudo vetado pelo CONTEXT.
- **`compose restart web` para aplicar código novo:** restart religa o MESMO container; não relê código assado nem env. Só `up -d --build web` serve para código. [CITED: cabeçalho de test_07_cor_runtime.sh]
- **`.jinja` em qualquer arquivo do fixture:** o fixture nunca passa pelo Copier (está em `_exclude`); é copiado byte a byte pela suíte. Sufixos `.jinja` ali seriam mentira estrutural.
- **Trap de limpeza que derruba o banco (`derrubar`):** encareceria todas as suítes seguintes; o banco sobrevive por design (diferença deliberada (a) do cabeçalho do harness).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gerar/gerenciar a cópia real | Novo script de copier+compose | `ensaio_django.sh` (subir/compor/executar/testar) | Fingerprint, porta livre, .env com segredos, guarda anti-v0.1.0, diagnóstico — tudo pronto e provado |
| Espera de serviço | Sleep fixo | Laço curl `/healthz` 180×1s (padrão do harness e do cor_runtime) | Teto conhecido, diagnóstico via `compose ps`/`logs` |
| Hash de subárvore p/ drift e vazamento | Novo esquema de hash | `impressao_subarvore()` de test_07_nav_extensao.py (sha256 caminho+`\0`+conteúdo, ignora `__pycache__`/`.pyc`) | Já resolve as colisões sutis (caminho entra no hash) |
| Render de variantes | Novo wrapper de copier | Função `render()` de test_04_04/test_07_nav (com `--vcs-ref=HEAD`) | Padrão idêntico em 2 suítes; dados não-default explícitos |
| Framework de teste | pytest ou runner novo | `unittest` stdlib | `test_command` do projeto é `unittest discover`; pytest não está instalado no host |
| Código do app diárias | Design novo de telas/views | Espelho do app exemplo, renomeado para o domínio | O critério 4 é literalmente "espelhar os padrões do app exemplo"; cada desvio vira dívida na Fase 9 |

**Key insight:** esta fase é 90% reaproveitamento disciplinado. O valor está em NÃO inventar: o fixture é o app exemplo re-instanciado no domínio de viagens, e a suíte é a composição de três padrões já provados no repositório (render leve, banco de ensaio, laço de healthz próprio).

## Common Pitfalls

### Pitfall 1: Código assado na imagem — instalar sem rebuild "funciona" pela metade
**What goes wrong:** copiar `apps/diarias` para `DESTINO/` e rodar migrate/testes sem rebuild → o container web não enxerga nada (o código vem de `COPY . .` no build). Pior: `compose exec` roda no filesystem do container, então `manage.py test apps.diarias` falha com import error — ou, se só settings foi patchado no DESTINO, nada muda no container e o teste passa em falso vazio.
**How to avoid:** sequência obrigatória: editar DESTINO → `compor up -d --build web` → esperar healthz → só então migrate/testes/smoke.
**Warning signs:** `ModuleNotFoundError: apps.diarias` dentro do container; telas 404 após "instalação".

### Pitfall 2: `garantir_banco()` chamado durante o boot detona o banco
**What goes wrong:** `testar`/`executar`/`compor`/`porta` chamam `garantir_banco()`, que faz UM curl sem retry; logo após `up -d --build`, o web ainda sobe → "não saudável" → `derrubar` + recriação completa (minutos) com PORTA NOVA — e a suíte segue com a porta velha na mão.
**How to avoid:** laço de healthz PRÓPRIO da suíte entre o rebuild e qualquer chamada subsequente ao harness (Pattern 2).
**Warning signs:** stderr com "ENSAIO: recriando banco de ensaio"; smoke com connection refused na porta capturada.

### Pitfall 3: Orçamento de tempo — timeouts do executor
**What goes wrong:** primeira criação do banco (cache Docker frio) pode passar de 600s; rebuild com cache morno leva minutos (COPY . . invalida collectstatic; estágio assets refaz `npx tailwindcss@3.4.17`).
**How to avoid:** regra normativa do cabeçalho do harness: quem invoca usa timeout explícito de 600000 ms; primeira criação em BACKGROUND com polling; um estouro de tempo com recriação anunciada em stderr NÃO é reprovação — só reprova comando que TERMINOU com código ≠ 0. O plano deve repetir este orçamento nas ações de verificação.
**Warning signs:** gate "reprovado" sem código de saída real.

### Pitfall 4: Fingerprint não cobre o fixture — banco reusado com diarias obsoleto
**What goes wrong:** editar o fixture e rodar a suíte de novo: banco reusado (fingerprint só olha a árvore do template), `apps/diarias` instalado é a versão anterior — testes provam código morto.
**How to avoid:** detecção de drift por sha256 fixture ↔ instalado a cada execução (Pattern 3); reinstalar + rebuild quando divergir.
**Warning signs:** mudança no fixture sem mudança no resultado dos testes.

### Pitfall 5: Drift de modelo com migração já aplicada
**What goes wrong:** fixture v2 muda o modelo; a suíte sobrescreve `apps/diarias` e roda `migrate` — o Django vê `0001_initial` já aplicada (por nome, em `django_migrations`) e não faz nada; schema do banco fica divergente do modelo; testes do app criam test-DB própria e passam, mas o smoke autenticado quebra de forma obscura.
**How to avoid:** quando o drift detectado tocar `models.py` ou `migrations/`, rodar `compor exec -T web python manage.py migrate diarias zero --noinput` COM O CÓDIGO ANTIGO ainda instalado (antes de sobrescrever), só então trocar os arquivos, rebuildar e migrar. Alternativa mais simples e sempre correta (custo alto): `derrubar` + recriação quando `models.py`/`migrations/` divergirem. O plano escolhe; a primeira é a recomendada.
**Warning signs:** `ProgrammingError: column ... does not exist` no smoke, com testes do app verdes.

### Pitfall 6: `makemigrations` dentro do container em vez de migração no fixture
**What goes wrong:** gerar a migração em runtime grava o arquivo só no filesystem do container; o próximo rebuild a perde, enquanto `django_migrations` mantém o registro — estado fantasma.
**How to avoid:** o fixture SHIPA `migrations/0001_initial.py` (determinística, com a tabela `HistoricalViagem` do simple-history incluída). O guia (Fase 9) pode ensinar `makemigrations` ao leitor mesmo assim — PRV-02 exige igualdade byte a byte só das cercas de código mostradas, e o cabeçalho gerado (`# Generated by Django ... on ...`) varia, então a migração não deve virar cerca integral no guia.
**Warning signs:** migração "aplicada" que não existe em disco após rebuild.

### Pitfall 7: Smoke autenticado esbarra no django-axes e no CSRF
**What goes wrong:** login por curl com senha errada conta para o lockout do axes (por usuário+IP); POST sem cookie `csrftoken` + campo `csrfmiddlewaretoken` → 403.
**How to avoid:** criar o usuário com senha conhecida via `compor exec -T -e DJANGO_SUPERUSER_EMAIL=... -e DJANGO_SUPERUSER_PASSWORD=... web python manage.py createsuperuser --noinput` (idempotência: tolerar "already exists" no stderr, ou verificar antes via `shell -c`); login em duas etapas com cookie jar (receita em Code Examples). Campos do form real: `email`, `password`, `csrfmiddlewaretoken`, `next` (verificado em `core/_login_form.html`; a view autentica com `authenticate(request, username=email, ...)`). Rota: `/login/` (`core:login`).
**Warning signs:** 403 no POST de login; lockout após tentativas com credencial errada.

### Pitfall 8: Teste negativo que apodrece na Fase 9
**What goes wrong:** negativo baseado em `grep -r diarias` na cópia passa hoje e quebra quando `docs/guia/*.md` citarem `apps/diarias` legitimamente.
**How to avoid:** asserções estruturais: (a) `(dest/"apps").iterdir()` contém exatamente `__init__.py` e `exemplo` (variante `incluir_app_exemplo=true`) ou só `__init__.py` (variante `false` — vale cobrir as duas); (b) nenhum sha256 de arquivo do fixture aparece entre os sha256 dos arquivos da cópia; (c) `apps/diarias` ausente também na árvore DO TEMPLATE fora de `.template-tests/fixtures/` (PRV-03 cobre "não chega ao template": `git ls-files` do repo não lista `apps/diarias` fora do fixture).
**Warning signs:** teste negativo referenciando conteúdo textual em vez de estrutura.

### Pitfall 9: unittest não garante ordem entre módulos nem entre métodos
**What goes wrong:** depender de "o negativo roda antes da prova" ou de método A antes de B.
**How to avoid:** cada suíte auto-suficiente; estado caro em `setUpClass` (uma vez por classe); o negativo independe do banco compartilhado por construção (Pattern 1/4).

### Pitfall 10: `.dockerignore` exclui `*.md`
**What goes wrong:** um `README.md` do fixture instalado na cópia nunca chega à imagem; um teste in-container que o leia falha.
**How to avoid:** nenhum teste in-container depende de arquivo `.md`; se o fixture tiver README, ele é documentação de host. [VERIFIED: .dockerignore]

## Code Examples

Todos extraídos/adaptados de código real do repositório (fontes indicadas).

### Capturar o banco de ensaio uma única vez (setUpClass)
```python
# Fonte do padrão: test_07_cor_runtime.sh (passo 1), traduzido para Python
saida = subprocess.run(
    ["sh", str(ROOT / ".template-tests" / "ensaio_django.sh"), "subir"],
    cwd=ROOT, text=True, capture_output=True, check=True,
).stdout
valores = dict(l.split("=", 1) for l in saida.splitlines() if "=" in l)
cls.destino = Path(valores["ENSAIO_DESTINO"])
cls.porta = valores["ENSAIO_PORTA"]
cls.projeto = valores["ENSAIO_PROJETO"]
cls.url = valores["ENSAIO_URL"]
```

### Patches idempotentes na cópia (os mesmos passos do leitor)
```python
# Âncoras verificadas em config/settings/base.py.jinja e config/urls.py.jinja
settings_path = destino / "config/settings/base.py"
texto = settings_path.read_text(encoding="utf-8")
if '"apps.diarias.apps.DiariasConfig",' not in texto:
    # variante com exemplo: âncora na linha do ExemploConfig; sem exemplo: âncora no fim da lista
    texto = texto.replace(
        '"apps.exemplo.apps.ExemploConfig",',
        '"apps.exemplo.apps.ExemploConfig",\n    "apps.diarias.apps.DiariasConfig",',
    )
    settings_path.write_text(texto, encoding="utf-8")

urls_path = destino / "config/urls.py"
texto = urls_path.read_text(encoding="utf-8")
if 'include("apps.diarias.urls")' not in texto:
    texto = texto.replace(
        '    path("", include("core.urls")),',
        '    path("diarias/", include("apps.diarias.urls")),\n    path("", include("core.urls")),',
    )
    urls_path.write_text(texto, encoding="utf-8")

nav_path = destino / "core/templates/core/_nav_dominio.html"
texto = nav_path.read_text(encoding="utf-8")
if 'item_nav "diarias:' not in texto:
    texto += (
        '{% item_nav "diarias:dashboard" "Viagens — Painel" "grafico" %}\n'
        '{% item_nav "diarias:viagem_listar" "Diárias e Passagens" "lista" '
        '"/diarias/" "/diarias/dashboard/" %}\n'
    )
    nav_path.write_text(texto, encoding="utf-8")
```

### Rebuild + espera própria + migração + testes do app
```python
def compor(*args):  # compose exec/up com project-name e env-file, cwd na cópia
    return subprocess.run(
        ["docker", "compose", "--project-name", projeto, "--env-file", ".env", *args],
        cwd=destino, text=True, capture_output=True,
    )

compor("up", "-d", "--build", "web")           # código novo → rebuild obrigatório (Dockerfile: COPY . .)
esperar_healthz(porta)                          # laço próprio 180×1s — NUNCA ensaio subir/porta aqui
compor("exec", "-T", "web", "python", "manage.py", "migrate", "--noinput")
r = compor("exec", "-T", "web", "python", "manage.py", "test", "apps.diarias", "--noinput")
assert r.returncode == 0, r.stderr
# migração aplicada, verificável:
r = compor("exec", "-T", "web", "python", "manage.py", "showmigrations", "diarias")
assert "[X] 0001_initial" in r.stdout
```

### Smoke autenticado por curl/urllib (dança de CSRF, campos reais do form)
```python
# Campos verificados em core/templates/core/_login_form.html: email, password, next, csrfmiddlewaretoken
import http.cookiejar, urllib.request, urllib.parse, re
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
corpo = op.open(f"{url}/login/").read().decode()
token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', corpo).group(1)
dados = urllib.parse.urlencode({
    "csrfmiddlewaretoken": token,
    "email": "guia@example.invalid",
    "password": senha_conhecida,
    "next": "/diarias/",
}).encode()
req = urllib.request.Request(f"{url}/login/", data=dados, headers={"Referer": f"{url}/login/"})
resposta = op.open(req)                      # segue o redirect com a sessão no jar
assert resposta.status == 200               # /diarias/ autenticado renderiza
corpo_dash = op.open(f"{url}/diarias/dashboard/").read().decode()
assert 'id="paleta-graficos"' in corpo_dash  # json_script da paleta presente
```

### Criar usuário de smoke (env vars via compose exec)
```bash
# Fonte do padrão: test_05_nascimento.sh (createsuperuser --noinput)
docker compose --project-name "$PROJETO" --env-file .env exec -T \
  -e DJANGO_SUPERUSER_EMAIL=guia@example.invalid \
  -e DJANGO_SUPERUSER_PASSWORD="$SENHA" \
  web python manage.py createsuperuser --noinput   # idempotência: tolerar 'already taken' no re-run
```

### Teste negativo (render leve, asserções estruturais)
```python
# Fonte do padrão: test_04_04_optional_exemplo.py render() + test_07_nav_extensao.py impressao_subarvore()
with tempfile.TemporaryDirectory() as tmp:
    dest = render(Path(tmp) / "recem-nascida", incluir_app_exemplo=True)
    self.assertFalse((dest / "apps" / "diarias").exists())
    nomes = sorted(p.name for p in (dest / "apps").iterdir())
    self.assertEqual(nomes, ["__init__.py", "exemplo"])
    hashes_fixture = set(impressao_subarvore(FIXTURE).values())
    hashes_copia = set(impressao_subarvore(dest).values())   # hash NÃO inclui o prefixo da raiz
    self.assertFalse(hashes_fixture & hashes_copia)
# Obs.: impressao_subarvore usa caminho RELATIVO no hash — comparar por CONTEÚDO puro
# (sha256 só dos bytes) para a interseção fixture×cópia, senão caminhos diferentes nunca colidem.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Docs como prosa não provada | Guarda executável: fixture + suíte antes do texto | Lição central da v0.2.0, formalizada no marco v0.3.0 | O guia (Fase 9) só descreve o que a Fase 8 já provou |
| Testes Django "soltos" no checkout do template | Toda prova Django DENTRO de cópia gerada via harness | Fase 7 (criação do ensaio_django.sh) | O checkout não é rodável; `compose exec` solto ERRA em vez de falhar |
| `restart web` para recarregar | `up -d` (env) / `up -d --build` (código) | Fase 7 (test_07_cor_runtime.sh) | restart não relê env nem código assado |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Rebuild com cache morno (pip/apt em cache; assets + collectstatic refeitos) cabe confortavelmente no orçamento de 600000 ms | Pitfalls 1/3 | Suíte estoura timeout no primeiro run pós-recriação; mitigação já normativa: background + polling |
| A2 | Nenhuma suíte futura assumirá banco de ensaio "puro" (sem diarias instalado) | Pattern 4 | Se surgir, precisará de render próprio (como todas as atuais já fazem) — convenção a registrar no cabeçalho da suíte nova |
| A3 | `createsuperuser --noinput` re-executado com o mesmo e-mail falha com erro identificável ("that email is already taken") — a suíte trata como sucesso idempotente | Pitfall 7 | Mensagem varia com versão do Django; alternativa robusta: `shell -c` com `get_or_create` + `set_password` |

## Open Questions (RESOLVED)

1. **Cobertura da variante `incluir_app_exemplo=false` na prova positiva**
   - What we know: o banco de ensaio usa `incluir_app_exemplo=true` fixo; o negativo pode (e deve, é barato) cobrir as duas variantes por render leve.
   - What's unclear: se a instalação do fixture também deve ser provada numa cópia SEM exemplo (âncora do patch de settings muda).
   - Recommendation: RESOLVED: prova positiva só na variante `true` (a do banco de ensaio — é o cenário do leitor, que nasce com o exemplo como referência); o patch de settings deve ter âncora com fallback (inserir antes de `]` de INSTALLED_APPS se a linha do exemplo não existir), deixando o código pronto para o futuro sem custo extra de Docker.

2. **Profundidade do smoke autenticado**
   - What we know: 302 → login prova rota; testes in-container provam 200 com force_login; o smoke autenticado por curl é o único que exercita gunicorn+sessão+banco de ponta a ponta.
   - Recommendation: RESOLVED: os três níveis, na ordem barato→caro (302 nas 3 telas; `manage.py test apps.diarias`; curl autenticado em `/diarias/` e `/diarias/dashboard/`). É o que o critério 1 pede sem ambiguidade.

3. **Seed no smoke**
   - What we know: dashboard e listagem funcionam com banco vazio (agregações tratam None — verificado em exemplo/views.py). `seed_diarias` existe para o guia, não para a prova.
   - Recommendation: RESOLVED: smoke NÃO depende de seed (páginas 200 vazias bastam); um teste opcional roda `seed_diarias` e verifica contagem — mas cuidado: dados seedados persistem no banco reusado; o comando deve ser idempotente (get_or_create ou truncate próprio) como `seed_exemplo`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| docker (daemon ativo) | banco de ensaio | ✓ | `docker info` OK | — |
| docker compose (plugin) | harness | ✓ | usado por todas as suítes sh | — |
| curl | healthz/smoke | ✓ | /usr/bin/curl | urllib (stdlib) no smoke |
| python3 (host) | unittest | ✓ | 3.14.4 | — |
| Copier | render | ✓ | 9.17.1 em `.venv-template/bin/copier` (exigido exatamente) | — (harness falha ruidosamente sem ele) |

**Missing dependencies with no fallback:** nenhuma.

## Security Domain

Fase de teste/fixture, sem superfície nova exposta. Categorias aplicáveis ao CÓDIGO do fixture (que o guia propagará a sistemas reais — errar aqui multiplica):

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V4 Access Control | yes | `@login_required` em todas as views do fixture (padrão exemplo) |
| V5 Input Validation | yes | ModelForm + validators; ordenação por whitelist (nunca `order_by(request.GET[...])`); filtros via `choices` |
| V3 Session Management | yes (indireto) | Login/CSRF do core reutilizados; smoke usa a dança real de CSRF, sem desligar proteções |
| V6 Cryptography | no | Nada novo; segredos do `.env` da cópia gerados pelo harness |

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection na ordenação/filtros | Tampering | Whitelist `COLUNAS_ORDENACAO_PERMITIDAS` + ORM (padrão exemplo, replicar) |
| XSS via formatter ECharts | Tampering | `esc()` em toda interpolação (decisão 07-12, replicar no dashboard do fixture) |
| CSRF no login/modais | Spoofing | `{% csrf_token %}` + `htmx:configRequest` já no base.html; smoke respeita o fluxo |
| Lockout abuse (axes) no smoke | DoS de teste | Credencial correta única; nunca loop de tentativas erradas |

## Sources

### Primary (HIGH confidence — leitura direta nesta sessão)
- `.template-tests/ensaio_django.sh` — integral: orçamento de tempo, fingerprint (exclusões), garantir_banco, subcomandos
- `.template-tests/test_07_cor_runtime.sh` — captura única de porta, laço próprio, trap de restauração, `up -d` vs restart
- `.template-tests/test_04_04_optional_exemplo.py`, `test_07_nav_extensao.py` — render leve, impressao_subarvore, asserções estruturais
- `Dockerfile`, `compose.yml.jinja`, `.dockerignore`, `tailwind.config.js` — código assado na imagem, globs de assets, env_file
- `copier.yml` — `_exclude` (.template-tests), `_skip_if_exists`, perguntas/validators
- `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/` — models, views, forms, admin, urls, templates, tests, seed
- `config/settings/base.py.jinja`, `config/urls.py.jinja`, `core/templates/core/_nav_dominio.html.jinja`, `core/templates/core/_login_form.html`, `core/urls.py`, `core/README.md`
- `.planning/research/{SUMMARY,ARCHITECTURE,PITFALLS}.md`, `.planning/config.json`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`
- Sondagem de ambiente nesta sessão: docker/curl/python3/copier (ver Environment Availability)

### Secondary / Tertiary
- Nenhuma — nenhuma consulta externa foi necessária; o domínio é 100% interno ao repositório.

## Metadata

**Confidence breakdown:**
- Mecânica de instalação/rebuild: ALTA — Dockerfile e compose lidos; precedente cor_runtime cobre a semântica de recriação
- Padrões do fixture: ALTA — app exemplo é a especificação viva, lida arquivo a arquivo
- Suíte e descoberta: ALTA — test_command verificado; padrões de suíte copiáveis de 2 arquivos existentes
- Orçamentos de tempo: ALTA como regra normativa (cabeçalho do harness); MÉDIA nos números absolutos de rebuild (A1)

**Research date:** 2026-08-26
**Valid until:** estável enquanto `ensaio_django.sh`, `Dockerfile` e `copier.yml` não mudarem (revalidar se qualquer um for tocado)
