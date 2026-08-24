# Milestones

## v0.2.0 — Design system herdado do PCA (fechado em 2026-08-24)

**Entregue:** um template Copier maduro do qual nasce, em minutos, um sistema
Django completo — autenticação, shell visual, CRUD e dashboard de exemplo,
Docker, backup — e que agora nasce também com o design system inteiro do
Sistema CFC e com um ponto de extensão de navegação que torna o `copier update`
dos derivados indolor.

**Escopo:** 7 fases · 38 planos · 77 tasks · 282 commits · ~7.100 linhas
(Python, templates, JS, CSS, shell) · 2026-08-17 → 2026-08-24

**Tag:** `v0.2.0` → `01ced83`, anotada e **publicada** em
`git@github.com:ToNiauM/sistema-base.git` (objeto `6c7bc99`, idêntico ao local).
Aponta para o commit posterior aos quatro consertos da rodada de gap closure —
a tag anterior, sobre `367dd9a`, ainda continha os bloqueadores e foi apagada e
recriada antes de sair da máquina. Como o Copier lê a última tag do repositório
e não o HEAD, é esta publicação que entrega as Fases 6 e 7 aos derivados.
A tag está publicada: pela regra do README, não se move mais.

### Principais entregas

1. **Fundação replicável (Fases 1–2)** — Django 5.2 em Docker Compose com
   PostgreSQL 17, `Usuario` customizado por e-mail desde a migração 0001,
   `django-axes` com lockout que preserva a resposta 200 da view, CSRF do HTMX
   por `htmx:configRequest` (nunca `hx-headers`, porque o token rotaciona no
   login/logout), admin isolado em `SistemaAdminSite`, PWA parametrizada e
   auditoria por `django-simple-history`.

2. **Documentação viva descartável (Fase 3)** — `apps/exemplo/` com CRUD de
   referência (paginação server-side, ordenação com whitelist, filtros
   multi-seleção, modais HTMX com HTTP 422 e `HX-Trigger`) e dashboard ECharts
   com agregações 100% via ORM. Autocontido: um protocolo de 4 passos o remove,
   e testes de isolamento por AST provam zero import reverso do `core`.

3. **Templatização Copier (Fase 4)** — o sistema-modelo vira template
   parametrizado in-place. `copier copy` gera, `copier update` puxa evoluções do
   núcleo, e o app exemplo é uma unidade opcional com seus três acoplamentos.
   Operação portátil junto: backup e retenção containerizados, ensaio de restore
   confinado, vhost TLS e runbook de migração.

4. **Nascimento provado ponta a ponta (Fase 5)** — tracer POSIX que gera uma
   cópia Copier real, sobe o build Docker, roda a suíte Django dentro dela e faz
   smoke HTTP em loopback. Inspeção humana aprovou 32/32 estados do UI-SPEC.

5. **Persistência e marca (Fase 6)** — PostgreSQL em bind mount configurável
   (`PGDATA_DIR`, default `./dados/pg`): `docker compose down -v` provadamente
   não perde dados. Pontos únicos de customização de marca por arquivo fixo, e
   `.gitignore` gerado protegendo `.env` e `/dados/`.

6. **Design system do PCA (Fase 7)** — `input.css` vira a fonte física de 21
   tokens claros e 18 overrides escuros; `tailwind.config.js` chega verbatim ao
   sistema gerado. `core/tema.py` deriva a família de marca inteira de uma única
   cor em Python no boot: trocar `COR_PRIMARIA` no `.env` e recriar só o `web`
   — sem rebuild — muda a paleta nos dois temas. Tema escuro com controle de 3
   estados e zero flash. Paleta de gráfico servida por `json_script` e
   reconstruída no evento `tema:alterado`. Zero hex de cor em template ou JS de
   template, no repositório e nas árvores geradas.

7. **O conflito de upstream eliminado (Fase 7)** — `_nav_dominio.html` como
   ponto de extensão protegido por `_skip_if_exists` e a inclusion tag
   `{% item_nav %}` entregando o tratamento visual por construção. O derivado
   põe os próprios itens sem tocar um único arquivo do `core` — provado por
   sha256 de toda a subárvore `core/`, exigindo que o único caminho divergente
   seja o arquivo do próprio derivado. O `copier update` de v0.1.0 para v0.2.0
   sai com exit 0, zero marcador de conflito e zero `.rej`.

### Qualidade no fecho

- Regressão em três camadas: 13 suítes em `.template-tests/` mais os testes
  Django do core e do app exemplo, rodando dentro de uma cópia Copier real
  (`ensaio_django.sh`). Última execução completa: verde em 394s somados —
  39 testes de `.template-tests/`, 169 Django na cópia gerada.
- 36/36 requisitos v1 fechados e mapeados em fases; nenhum órfão.
- 7/7 fases com verificação `passed`.
- Uma rodada de gap closure (planos 07-09..07-14) fechou os 5 defeitos que a
  revisão de código posterior à verificação encontrou — todos na fresta entre
  "estrutura declarada" (o que os critérios testavam) e "resultado renderizado".
  Quatro deles eram de contraste ou de estado ativo, invisíveis a teste
  estrutural.

### Itens conhecidos no fecho

- **Commits de planejamento à frente da tag.** A `v0.2.0` está publicada em
  `01ced83`; `main` segue com commits posteriores que são só de `.planning/`,
  diretório excluído pelo `copier.yml`. Nenhum sistema gerado é afetado por eles.
- **Inspeção humana parcial na Fase 3.** Três comportamentos dos roteiros de
  UAT originais — foco automático no primeiro campo do modal, redimensionamento
  da janela e drill-down por clique no dashboard — nunca tiveram inspeção
  humana direta. Fechados por cobertura (testes automatizados de 422 e
  `HX-Trigger`, mais o gate visual aprovado na 07-08 sobre as mesmas telas),
  por decisão do operador em 2026-08-24.
- **Ruído de ferramenta, não do projeto:** `gsd-sdk query audit-open` reporta
  os 5 quick tasks como incompletos porque lê `.planning/quick/<dir>/SUMMARY.md`
  enquanto o `/gsd-quick` grava `<dir>/<id>-SUMMARY.md`. Os 5 têm PLAN, SUMMARY
  e commit (`ba86084`, `8a52155`, `f910787`, `44ae507`, e uma auditoria
  docs-only).
