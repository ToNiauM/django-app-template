---
phase: 06-customiza-o-visual-e-persist-ncia-de-dados
verified: 2026-08-19T15:05:00Z
status: passed
score: 16/16 must-haves verificados
---

# Fase 6: Customização Visual e Persistência de Dados — Relatório de Verificação

**Objetivo da fase:** Pontos de customização de marca claros e centralizados no app `core` — logo principal da entidade, logo do subsistema e logo/nome do PWA trocáveis em locais únicos e documentados — e dados do PostgreSQL persistidos no host (bind mount), sobrevivendo a `docker compose down -v`.
**Verificado em:** 2026-08-19T15:05:00Z
**Status:** passed

## Alcance do objetivo

### Verdades observáveis (must_haves dos 3 planos)

#### Plano 06-01 — Persistência por bind mount

| # | Verdade | Status | Evidência |
|---|---------|--------|-----------|
| 1 | `down -v` + `up -d` não perde nenhum dado do banco (D-73, critério 4) | ✓ VERIFICADO | `test_05_nascimento.sh` linhas 206-217: `compose down --volumes` → `up -d` → `get_user_model().objects.get(email='nascimento@example.invalid')` ANTES de `SUCESSO=true`; tracer verde registrado nos SUMMARYs 06-01 e 06-02 |
| 2 | Dados visíveis no host em `./dados/pg` (ou `PGDATA_DIR` do .env) | ✓ VERIFICADO | `compose.yml.jinja:21`: `- ${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data`; `test_04_05_backup.py` valida `type == "bind"`, `target == /var/lib/postgresql/data`, `source` terminando em `/dados/pg` no JSON de `docker compose config` |
| 3 | Sistema gerado nasce com `.gitignore` ignorando `.env` e `/dados/` (D-74) | ✓ VERIFICADO | `.gitignore.jinja` contém `.env` (linha 3) e `/dados/` (linha 12), sem `.venv-template/`; `copier.yml` sem `- .gitignore` no `_exclude`; `GitignoreGeradoTests` prova por cópia Copier real (suíte verde) |
| 4 | Tracer verde ponta a ponta, inclusive limpeza uid 999 | ✓ VERIFICADO | `test_05_nascimento.sh:100`: `docker run --rm -v "${DESTINO}:/alvo" postgres:17 rm -rf /alvo/dados` dentro de `limpar()`; execução verde registrada em 06-01/06-02 |

#### Plano 06-02 — Logos por arquivo fixo

| # | Verdade | Status | Evidência |
|---|---------|--------|-----------|
| 5 | Local único para o logo da entidade: `core/static/img/logo-entidade.svg` (D-65, critério 1) | ✓ VERIFICADO | Arquivo existe (645 bytes, XML válido, viewBox, sem width/height); referenciado só via `{% static %}` |
| 6 | Local único para o logo do subsistema: `core/static/img/logo-subsistema.svg` (D-65, critério 2) | ✓ VERIFICADO | Arquivo existe (801 bytes, XML válido, viewBox); forma distinta da entidade |
| 7 | Subsistema na aside + header mobile; entidade no login + rodapé da aside (D-68/D-69) | ✓ VERIFICADO | `shell.html:41` (header mobile h-6), `:54` (aside h-8), `:77` (rodapé entidade h-5 opacity-60); `login.html:11` (entidade h-12 acima do form) |
| 8 | Sistema recém-nascido renderiza placeholders sem referência quebrada nem marca (D-66) | ✓ VERIFICADO | grep de identidade proibida (cfc/pca/sistema.base/script) vazio nos SVGs; `test_04_03_identity.py` verde na suíte; tracer roda `manage.py test core` na cópia com `test_logos.py` incluso |
| 9 | Todo `<img>` de logo tem `alt` derivado do context processor (D-67) | ✓ VERIFICADO | `alt="Logo de {{ sistema_sigla }}"` nos dois pontos do subsistema; `alt="Logo institucional"` na entidade; `test_alt_do_logo_do_subsistema_deriva_da_identidade` asserta contra `settings.SISTEMA_SIGLA`, nunca literal |
| 10 | Admin NÃO ganhou logo (D-70) | ✓ VERIFICADO | Nenhum arquivo de admin nos `files_modified`/commits da fase (git log 229a7bd/8d0ca19/7da09aa); `core/views.py` intocado (D-71) |

#### Plano 06-03 — Documentação

| # | Verdade | Status | Evidência |
|---|---------|--------|-----------|
| 11 | README gerado tem UMA seção "Customização de marca" com TODOS os pontos (D-77) | ✓ VERIFICADO | `README.md.jinja:70` `## Customização de marca` listando logo-entidade.svg, logo-subsistema.svg, icon-*.png + `gerar_icones_pwa.py`, SISTEMA_NOME/SISTEMA_SIGLA, COR_PRIMARIA |
| 12 | Nome do PWA documentado via SISTEMA_NOME/SISTEMA_SIGLA no .env (D-71, critério 3) | ✓ VERIFICADO | `README.md.jinja:91-92`: item "Nome do PWA" citando reflexo no manifest sem tocar código |
| 13 | Logo do PWA documentado: 3 PNGs fixos ou `ops/gerar_icones_pwa.py` (D-72, critério 3) | ✓ VERIFICADO | Item "Ícones do PWA" na seção de marca; favicon reaproveita `icon-192.png` (`base.html:12`) |
| 14 | README do template com etapa opcional de logos + nota de persistência (D-78) | ✓ VERIFICADO | `README.md:117` (passo opcional citando os dois .svg antes do commit inicial), `:147` (nota `./dados/pg`); comentário no resumo executável presente; âncora A → B → C intacta (linhas 346/416) |
| 15 | MIGRACAO.md e README gerado documentam bind mount + migração de named volume, sem script (D-75, D-40) | ✓ VERIFICADO | `ops/MIGRACAO.md.jinja:41-42` (layout `./dados/pg` + PGDATA_DIR, sem `docker volume create`); `README.md.jinja:122` one-liner manual `cp -a /de/. /para/` com `{{ sistema_slug }}_pgdata` |
| 16 | Operador acha em minutos onde trocar cada logo e o nome do PWA | ✓ VERIFICADO | Seção canônica única no README gerado; `core/README.md:83` convenção `## 5.` referenciando os mesmos caminhos; 4 docs consistentes entre si (mesmos nomes de arquivo/variável) |

**Pontuação:** 16/16 verdades verificadas

### Critérios de sucesso da Fase 6 (ROADMAP.md)

| # | Critério | Status | Evidência |
|---|----------|--------|-----------|
| 1 | Local único e documentado no `core` para o logo principal da entidade | ✓ SATISFEITO | `core/static/img/logo-entidade.svg` + seção "Customização de marca" + convenção 5 do core |
| 2 | Local único e documentado no `core` para o logo do subsistema | ✓ SATISFEITO | `core/static/img/logo-subsistema.svg` + mesma documentação |
| 3 | Logo e nome do PWA customizáveis a partir do `core`, refletindo no manifest e na instalação | ✓ SATISFEITO | Mecanismo pré-existente (D-71/D-72: SISTEMA_NOME/SIGLA → manifest_view; icon-*.png via static()) agora documentado como local canônico; favicon adicionado via `icon-192.png` |
| 4 | Dados do banco no host, sobrevivendo a `docker compose down -v` | ✓ SATISFEITO | Bind mount `${PGDATA_DIR:-./dados/pg}` sem bloco `volumes:` de topo; prova comportamental direta no tracer (superusuário reencontrado após `down --volumes` + `up -d`) |

**Cobertura:** 4/4 critérios satisfeitos. (Os requisitos C1-C4 desta fase pós-v1 não têm IDs em REQUIREMENTS.md — verificação feita contra os Success Criteria do ROADMAP.md, conforme instruído.)

### Artefatos exigidos

| Artefato | Esperado | Status | Detalhes |
|----------|----------|--------|----------|
| `compose.yml.jinja` | Bind mount no db, sem bloco `volumes:` de topo | ✓ EXISTE + SUBSTANTIVO | Linha 21 com o mount exato; zero ocorrências de `pgdata`; web/backup/healthcheck intactos |
| `.env.example.jinja` | PGDATA_DIR documentado | ✓ EXISTE + SUBSTANTIVO | Linhas 42-47: default comentado, exigência do prefixo `./`, regra de subdiretório |
| `.gitignore.jinja` | Fonte do .gitignore gerado | ✓ EXISTE + SUBSTANTIVO | `.env`, `/dados/` e demais entradas; sem `.venv-template/`; texto neutro |
| `.gitignore` (template) | `/dados/` | ✓ EXISTE | Linha 11 |
| `copier.yml` | `.gitignore` fora do `_exclude` | ✓ VERIFICADO | Comentário pt-BR explicando o mecanismo (linhas 9-11) |
| `.template-tests/test_06_persistencia.py` | Contrato bind mount + cópia real (min 40 linhas) | ✓ EXISTE + SUBSTANTIVO | 106 linhas, 6 testes, sem skips |
| `.template-tests/test_04_05_backup.py` | Contrato novo do compose config | ✓ VERIFICADO | Asserções `type=bind`/`target`/`source.endswith("/dados/pg")`; `"volumes" not in compose` |
| `.template-tests/test_05_nascimento.sh` | `down --volumes` + limpeza uid 999 | ✓ VERIFICADO | Linhas 100, 206-217; prova antes de `SUCESSO=true` |
| `core/static/img/logo-entidade.svg` | Placeholder neutro com viewBox | ✓ EXISTE + SUBSTANTIVO | XML válido, sem width/height, sem script, sem marca |
| `core/static/img/logo-subsistema.svg` | Placeholder neutro, forma distinta | ✓ EXISTE + SUBSTANTIVO | Idem, forma distinta (quadrado+losango vs círculo+cruz) |
| `core/templates/core/shell.html` | Logos nos 3 pontos | ✓ VERIFICADO | 2× logo-subsistema + 1× logo-entidade, `{% load static %}` próprio |
| `core/templates/core/login.html` | Logo da entidade | ✓ VERIFICADO | 1× logo-entidade acima do `<h1>Entrar</h1>` |
| `core/templates/base.html` | Favicon | ✓ VERIFICADO | Linha 12: `<link rel="icon" href="{% static 'img/icon-192.png' %}">` |
| `core/tests/test_logos.py` | Regressão dos logos (min 40 linhas) | ✓ EXISTE + SUBSTANTIVO | 78 linhas, 5 métodos de teste cobrindo os 5 comportamentos do plano |
| `README.md.jinja` | Seção de marca + persistência + migração | ✓ VERIFICADO | Todos os tokens presentes; grep de identidade proibida vazio |
| `README.md` | Etapa de logos + nota de persistência | ✓ VERIFICADO | Linhas 117, 147; âncora A → B → C preservada |
| `core/README.md` | Convenção 5 | ✓ VERIFICADO | Linha 83; texto neutro (grep vazio) |
| `ops/MIGRACAO.md.jinja` | Runbook com layout bind mount | ✓ VERIFICADO | PGDATA_DIR/`./dados/pg` explicados; sem `docker volume create`; sem `pca`; test_04_06 verde |

**Artefatos:** 18/18 verificados

### Verificação de ligações-chave (key_links)

| De | Para | Via | Status | Detalhes |
|----|------|-----|--------|----------|
| compose.yml.jinja | .env (PGDATA_DIR) | interpolação Compose com default | ✓ LIGADO | Linha 21: `${PGDATA_DIR:-./dados/pg}:/var/lib/postgresql/data` |
| copier.yml | .gitignore.jinja | `_exclude` sem a entrada `.gitignore` | ✓ LIGADO | Entrada removida + comentário; cópia real prova `.gitignore` renderizado no destino e ausência de `.gitignore.jinja` |
| test_05_nascimento.sh | dados uid 999 no host | container root postgres:17 | ✓ LIGADO | Linha 100: `postgres:17 rm -rf /alvo/dados` |
| shell.html | logo-subsistema.svg | `{% static %}` | ✓ LIGADO | Linhas 41 e 54 |
| login.html | logo-entidade.svg | `{% static %}` | ✓ LIGADO | Linha 11 |
| base.html | icon-192.png | `rel="icon"` | ✓ LIGADO | Linha 12 |
| README.md.jinja | logos em caminhos fixos | seção Customização de marca | ✓ LIGADO | Linhas 75/77 nomeiam os caminhos exatos |
| README.md.jinja | migração named volume → bind mount | one-liner `cp -a /de/. /para/` | ✓ LIGADO | Linha 122 |
| ops/MIGRACAO.md.jinja | compose (bind mount) | explicação do layout `./dados/pg` | ✓ LIGADO | Linhas 41-42 e 126 |

**Fiação:** 9/9 ligações verificadas

## Verificação comportamental

| Verificação | Resultado | Detalhe |
|-------------|-----------|---------|
| Suíte do template (`python3 -m unittest discover -s .template-tests -p 'test_*.py'`) | ✓ 21/21 OK | Re-executada nesta verificação (97,5s); inclui cópias Copier reais (`--vcs-ref=HEAD`) |
| Tracer de nascimento (`test_05_nascimento.sh`) | ✓ verde | Executado nos planos 06-01 e 06-02 (registrado nos SUMMARYs): "OK: dados sobreviveram a down --volumes + up -d" e "OK: nascimento completo da cópia Copier passou."; suíte Django da cópia inclui test_logos.py |
| Scan de identidade (`test_04_03_identity.py`) | ✓ verde | Incluso na suíte de 21 testes; SVGs e docs novos neutros |

## Cobertura de decisões (CONTEXT.md)

`gsd-sdk query check.decision-coverage-verify`: **14/14 decisões honradas** pelos artefatos entregues (D-65…D-78). Nenhuma decisão perdida na execução.

## Auditoria de qualidade dos testes

| Arquivo de teste | Vincula | Ativos | Skips | Circular | Nível de asserção | Veredito |
|------------------|---------|--------|-------|----------|-------------------|----------|
| .template-tests/test_06_persistencia.py | C4 (bind mount + .gitignore gerado) | 6 | 0 | Não | Valor (literais de contrato + cópia real) | ✓ |
| .template-tests/test_04_05_backup.py | C4 (compose resolvido) | 4 | 0 | Não | Valor (JSON de `docker compose config`) | ✓ |
| .template-tests/test_05_nascimento.sh | C4 (prova comportamental) | e2e | 0 | Não | Comportamental (superusuário sobrevive a down -v) | ✓ |
| core/tests/test_logos.py | C1/C2 (contrato de logos) | 5 | 0 | Não | Valor (static() exato, alt via settings) | ✓ |

Nenhum teste desabilitado, nenhum padrão circular (valores esperados são literais de contrato, não gerados pelo sistema sob teste), asserções em nível de valor/comportamental.

## Anti-padrões encontrados

| Arquivo | Linha | Padrão | Severidade | Impacto |
|---------|-------|--------|------------|---------|
| — | — | — | — | Nenhum anti-padrão nos arquivos da fase |

Nota: `core/templates/base.html:46` contém a palavra pt-BR "TODO" ("apaga TODO o Cache Storage") — falso positivo do grep, não é marcador de pendência.

**Anti-padrões:** 0 encontrados (0 bloqueadores, 0 avisos)

## Verificação humana necessária

Nenhuma — todos os critérios de sucesso da fase são verificáveis programaticamente e foram verificados: os critérios exigem *locais únicos e documentados* (existência de arquivos, referências `{% static %}` e documentação — verificados por grep/teste) e *sobrevivência de dados a `down -v`* (provada comportamentalmente pelo tracer). A renderização real das páginas com os logos foi exercitada pela suíte Django dentro da cópia gerada (test_logos.py) e pelo smoke de `/login/` do tracer. Inspeção estética dos placeholders é opcional e não é critério da fase (D-66 exige apenas neutralidade e validade, ambas verificadas).

## Achados do code review (06-REVIEW.md) vs. critérios da fase

O review registrou 1 Critical (CR-01) e 6 Warnings, todos advisories. Avaliação contra os critérios de sucesso:

- **CR-01** (dump baixado morre com o container efêmero no runbook de restore): defeito **pré-existente da fase 04-06** no procedimento de recuperação de desastre; não afeta nenhum dos 4 critérios da Fase 6 (o critério 4 é sobre `down -v` no host, provado). Recomenda-se corrigir em quick task ou fase futura — não é gap desta fase.
- **WR-02/WR-03/WR-04** (atalho de migração pode criar volume vazio; `PGDATA_DIR` sem `./` degrada para named volume; `PGDATA_DIR` customizado escapa do `.gitignore`): bordas do contrato com valores não-default; o comportamento default (que os critérios cobrem) está provado. Endurecimentos recomendáveis, não bloqueantes.
- Nenhum achado do review desprova um critério de sucesso da fase.

## Resumo de lacunas

**Nenhuma lacuna encontrada.** O objetivo da fase foi alcançado: os três pontos de marca têm locais únicos e documentados no `core`, o nome/logo do PWA está documentado como customizável, e a persistência por bind mount está provada comportamentalmente contra `docker compose down -v`.

### Observações não-bloqueantes (transparência)

1. **CR-01 do review** — runbook de restore com download efêmero (pré-existente; corrigir em trabalho futuro).
2. **deferred-items.md da fase** — 4 testes Copier ainda pinados na tag `v0.1.0` (`test_04_03_identity.py`, `test_copier_copy.sh`, `test_04_06_operations.py`, `test_04_04_optional_exemplo.py`): passam, mas validam conteúdo da tag; o 06-03 mitigou com render de fumaça manual `--vcs-ref=HEAD`. Só afeta a rede de regressão do template, não os sistemas gerados.

## Metadados da verificação

**Abordagem:** goal-backward (must_haves dos 3 PLANs + Success Criteria do ROADMAP.md)
**Fonte dos must-haves:** frontmatter de 06-01/06-02/06-03-PLAN.md (16 truths, 18 artefatos, 9 key_links)
**Verificações automatizadas:** 43+ aprovadas, 0 reprovadas (artefatos, ligações, suíte de 21 testes re-executada, cobertura de decisões 14/14)
**Verificações humanas necessárias:** 0
**Tempo total de verificação:** ~6 min

---
*Verificado em: 2026-08-19T15:05:00Z*
*Verificador: Claude (subagente gsd-verifier)*
