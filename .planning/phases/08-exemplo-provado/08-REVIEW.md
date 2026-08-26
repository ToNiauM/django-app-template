---
phase: 08-exemplo-provado
reviewed: 2026-08-26T12:55:13Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - .template-tests/fixtures/guia/apps/diarias/admin.py
  - .template-tests/fixtures/guia/apps/diarias/apps.py
  - .template-tests/fixtures/guia/apps/diarias/forms.py
  - .template-tests/fixtures/guia/apps/diarias/management/commands/seed_diarias.py
  - .template-tests/fixtures/guia/apps/diarias/migrations/0001_initial.py
  - .template-tests/fixtures/guia/apps/diarias/models.py
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_confirmar_exclusao_modal.html
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_form_modal.html
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/_tabela_resultado.html
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/dashboard.html
  - .template-tests/fixtures/guia/apps/diarias/templates/diarias/viagem_listar.html
  - .template-tests/fixtures/guia/apps/diarias/tests/__init__.py
  - .template-tests/fixtures/guia/apps/diarias/tests/test_crud.py
  - .template-tests/fixtures/guia/apps/diarias/tests/test_dashboard.py
  - .template-tests/fixtures/guia/apps/diarias/tests/test_models.py
  - .template-tests/fixtures/guia/apps/diarias/urls.py
  - .template-tests/fixtures/guia/apps/diarias/views.py
  - .template-tests/test_08_guia_prova.py
  - .template-tests/test_08_guia_vazamento.py
  - .dockerignore
findings:
  critical: 2
  warning: 3
  info: 8
  total: 13
status: issues_found
---

# Phase 08: Code Review Report

**Reviewed:** 2026-08-26T12:55:13Z
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found

## Summary

Revisão do fixture didático `apps/diarias` (modelo, migração manual, views CRUD+dashboard, templates HTMX/Alpine, seed e testes do app) mais as duas suítes de nível de template (`test_08_guia_prova.py`, `test_08_guia_vazamento.py`) e o `.dockerignore`. As verificações cruzaram o fixture com o core real do template (`core/tema.py`, `core/templatetags/{formatos,navegacao}.py`, `core/templates/{base,core/shell}.html`, htmx 1.9.12 vendorado) e com o app de referência `apps/exemplo`.

Os fundamentos estão sólidos: ordenação por whitelist, filtro de status validado contra `StatusChoices.values`, agregações 100% via ORM, `json_script` + `esc()` no formatter do ECharts (XSS coberto nas duas pontas), CSRF real nos modais, autenticação em todas as rotas, suíte de vazamento com guardas contra falso verde. As assinaturas externas conferem (`familia_marca` expõe os degraus `seq-*` e `seq-*:escuro` usados; `item_nav` aceita os 5 argumentos das constantes de patch; `moeda` existe; `tema:alterado` é disparado em `document`; o `#modal-container` fica dentro do escopo `x-data` do shell, então `@viagem-salva.window` inicializa; htmx 1.9.12 de fato despacha a forma kebab-case de `viagemSalva`).

Porém, dois defeitos funcionais reais — herdados byte a byte do app de referência `apps/exemplo` — tornam a UI de listagem parcialmente quebrada: a alternância de ordenação para de funcionar depois do primeiro clique/filtro (CR-01) e os gatilhos "vivos" de busca e status são inertes no htmx (CR-02). Como este fixture é o artefato canônico que todo leitor do guia vai copiar, esses defeitos se propagam para cada sistema derivado.

## Critical Issues

### CR-01: Alternância de ordenação quebra após o primeiro sort ou após qualquer filtro (parâmetro `ordem` duplicado; o valor ANTIGO vence)

**File:** `.template-tests/fixtures/guia/apps/diarias/views.py:37-42` e `.template-tests/fixtures/guia/apps/diarias/templates/diarias/_tabela_resultado.html:12-13` (e todos os demais cabeçalhos de coluna: linhas 30-31, 48-49, 66-67, 84-85, 102-103)
**Issue:** `extrair_querystring_filtros()` exclui apenas `pagina` — `ordem` permanece dentro de `querystring_filtros`. Os links de cabeçalho da tabela montam `?ordem={novo}&{{ querystring_filtros }}`, produzindo URLs como `?ordem=-servidor&ordem=servidor`. `QueryDict.get("ordem")` do Django retorna o **último** valor da lista (`MultiValueDict.__getitem__` → `list_[-1]`), ou seja, o valor ANTIGO. Consequência rastreada:

1. Página limpa → clicar "Servidor" ordena (funciona 1 vez; URL empurrada: `?ordem=servidor`).
2. Segundo clique gera `?ordem=-servidor&ordem=servidor` → `get()` devolve `servidor` → a inversão nunca acontece; a seta fica travada em ↑.
3. Pior: o form de filtros carrega `<input type="hidden" name="ordem">` (`_filtros.html:77`), então após QUALQUER busca/filtro a querystring já contém `ordem` — e a partir daí **todo** clique de ordenação vira no-op (`?ordem=destino&ordem=-criado_em&q=ana` → ordena por `-criado_em`).

Os testes não pegam porque `test_ordenacao_segura_com_whitelist` envia `ordem` único direto na view, nunca a URL composta pelos templates. O mesmo defeito existe no app de referência `apps/exemplo` (fora do escopo desta revisão, mas a origem da cópia) — corrigir só o fixture faria guia e referência divergirem; recomenda-se corrigir os dois.
**Fix:**
```python
# views.py — ordem é reanexada explicitamente pelos templates; nunca deve
# viajar dentro da querystring de filtros:
def extrair_querystring_filtros(params, excluir=("pagina", "ordem")):
```
(Os links de paginação já anexam `&ordem={{ ordem_atual }}` por conta própria — com a exclusão acima eles continuam corretos e a duplicação idêntica que hoje existe neles também desaparece.)

### CR-02: Filtros "ao vivo" são inertes — `hx-trigger` sem verbo AJAX é no-op no htmx, e o form não tem botão de submit

**File:** `.template-tests/fixtures/guia/apps/diarias/templates/diarias/_filtros.html:94` (input de busca) e `:104` (select de status)
**Issue:** O input tem `hx-trigger="input changed delay:300ms, search"` e o select tem `hx-trigger="change"`, mas nenhum dos dois tem `hx-get`/`hx-post` — e verbos AJAX **não são herdados** do `<form>` pai no htmx. No htmx 1.9.12 vendorado (`core/static/vendor/htmx.min.js`), gatilhos "naked" recebem um handler vazio (comentário literal do fonte: *"For 'naked' triggers, don't do anything at all"*; eles apenas emitem `htmx:trigger`, que ninguém escuta aqui). Resultado: digitar na busca não dispara requisição nenhuma; trocar o status não dispara nada; e como o form não tem botão de submit, o único caminho é a submissão implícita por Enter dentro do campo de texto. A busca com debounce de 300ms — comportamento central que o guia se propõe a ensinar — simplesmente não funciona. Os testes passam porque chamam a view via `client.get` direto, sem exercitar o disparo do DOM. Mesmo defeito no `apps/exemplo` de referência.
**Fix:** mover os gatilhos para o elemento que possui o verbo (o form), usando `from:`:
```html
<form id="form-filtros"
      hx-get="{% url 'diarias:viagem_listar' %}"
      hx-target="#tabela-container"
      hx-swap="innerHTML"
      hx-push-url="true"
      hx-trigger="submit, input changed delay:300ms from:find input[name='q'], change from:find select[name='status']"
      ...>
```
e remover os `hx-trigger` órfãos do input e do select. (Alternativa: dar `hx-get` + `hx-include="#form-filtros"` + `hx-target`/`hx-push-url` a cada controle.)

## Warnings

### WR-01: Idempotência do `seed_diarias` só vale dentro do mesmo dia — em banco reusado entre dias, cada execução insere até 14 linhas novas

**File:** `.template-tests/fixtures/guia/apps/diarias/management/commands/seed_diarias.py:40-52`
**Issue:** A chave do `get_or_create` é `(servidor, destino, data_inicio)`, mas `data_inicio = timezone.localdate() + timedelta(days=desloc)` muda todo dia. A docstring afirma "rodar o comando duas vezes não duplica registro nenhum" — verdadeiro apenas no mesmo dia. O banco de ensaio da Fase 8 é explicitamente REUSADO entre execuções (Pattern 4, docstring de `test_08_guia_prova.py`): rodar o seed em dias distintos infla a tabela em 14 registros por dia, exatamente o cenário que a própria suíte diz evitar. O teste `test_comando_seed_diarias_e_idempotente` não pega porque as duas chamadas ocorrem no mesmo processo/dia.
**Fix:** chavear o `get_or_create` sem a data (ex.: por `(servidor, destino)`, com `data_inicio` nos `defaults`) ou ancorar as datas numa referência fixa (ex.: primeiro dia do mês corrente) e documentar o comportamento real.

### WR-02: Resposta de sucesso dos modais cria `id="modal-container"` duplicado no DOM (HTML inválido) com `x-init` morto

**File:** `.template-tests/fixtures/guia/apps/diarias/views.py:98-101, 124-127, 152-155`
**Issue:** As três views devolvem `'<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'` que é trocado via `hx-swap="innerHTML"` **dentro** do `#modal-container` real — o DOM fica com dois elementos de mesmo id aninhados (HTML inválido; `querySelector` passa a depender de retornar o primeiro match para continuar funcionando). O `x-init` limpa o `innerHTML` do div interno, que já nasce vazio — código morto que sugere intenção não realizada (limpar o container externo). O mesmo literal é ainda duplicado três vezes.
**Fix:** devolver corpo vazio — o swap `innerHTML` com string vazia já fecha o modal:
```python
resposta = HttpResponse("")
resposta["HX-Trigger"] = "viagemSalva"
return resposta
```
(extraído para um helper único, ex.: `_resposta_modal_fechado()`).

### WR-03: `ordem_atual` expõe o parâmetro cru (não sanitizado) e o propaga por hidden input e links

**File:** `.template-tests/fixtures/guia/apps/diarias/views.py:63-64, 76`
**Issue:** O contexto publica `ordem_atual = ordem_param` (entrada crua) em vez de `ordem_segura`. Não há XSS (autoescape cobre atributo e URL) nem injeção no ORM (whitelist cobre o `order_by`), mas um valor inválido (`?ordem=zzz`) fica ecoando para sempre: entra no hidden `name="ordem"` de `_filtros.html:77`, em todos os links de paginação e nas comparações dos indicadores de seta — que passam a não acender nenhuma coluna enquanto a ordenação real é `-criado_em`. Estado da UI dessincronizado da query executada.
**Fix:** `"ordem_atual": ordem_segura` no contexto (a comparação dos cabeçalhos e o hidden passam a refletir a ordenação efetiva).

## Info

### IN-01: Docstring e testes prometem "multi-seleção" de status, mas a UI é um `<select>` simples

**File:** `.template-tests/fixtures/guia/apps/diarias/views.py:57` e `templates/diarias/_filtros.html:102-110`
**Issue:** A view usa `getlist("status")` e `test_filtro_multi_selecao_de_status` envia lista, mas o select não tem `multiple` — pelo navegador só é possível um status por vez. Documentação do fixture promete um comportamento que a tela não oferece.
**Fix:** Ou adicionar `multiple` ao select (com ajuste de UX), ou reescrever a docstring/nome do teste para "filtro de status (backend aceita múltiplos valores)".

### IN-02: `{% load static %}` não utilizado

**File:** `.template-tests/fixtures/guia/apps/diarias/templates/diarias/viagem_listar.html:287`
**Issue:** O template carrega `static` mas nunca usa `{% static %}`.
**Fix:** Remover o load.

### IN-03: Modais respondem fragmento cru para navegação direta (não-HTMX)

**File:** `.template-tests/fixtures/guia/apps/diarias/views.py:111-112, 137-142, 158-162`
**Issue:** GET direto em `/diarias/novo/`, `/editar/` ou `/excluir/` (URL na barra, sem HTMX) devolve o fragmento do modal sem `<html>`/CSS — página quebrada, embora autenticada. A listagem trata `request.htmx`; os modais não.
**Fix:** Para requisição não-HTMX, redirecionar para a listagem (`HttpResponseRedirect(reverse("diarias:viagem_listar"))`) ou renderizar dentro do shell.

### IN-04: Mensagem de timeout do healthz subestima o pior caso em ~6x

**File:** `.template-tests/test_08_guia_prova.py:186-199`
**Issue:** O laço faz até 180 tentativas com `urlopen(timeout=5)` + `sleep(1)` — pior caso ~1080s, mas a mensagem de falha afirma "não respondeu em /healthz em 180s". Diagnóstico enganoso e potencial estouro do orçamento de 600s sem aviso.
**Fix:** Controlar por relógio (`deadline = time.monotonic() + 180`) e ajustar a mensagem.

### IN-05: Fallback de `_patch_settings` falha com `ValueError` cru se `INSTALLED_APPS = [` não existir

**File:** `.template-tests/test_08_guia_prova.py:249-252`
**Issue:** `texto.index(marcador)` e `texto.index("\n]", inicio)` levantam `ValueError` sem contexto, ao contrário de `_patch_urls`, que levanta `AssertionError` com mensagem clara sobre a âncora ausente.
**Fix:** Envolver em try/except e levantar `AssertionError("INSTALLED_APPS não encontrado em config/settings/base.py")`.

### IN-06: Falha do `copier copy` esconde o stderr no relatório de teste

**File:** `.template-tests/test_08_guia_vazamento.py:52-81`
**Issue:** `subprocess.run(..., check=True, capture_output=True)` — quando o copier falha, o `CalledProcessError` propagado não exibe o stderr capturado na saída do unittest, dificultando diagnóstico.
**Fix:** Capturar a exceção e re-levantar `AssertionError` incluindo `exc.stderr`, ou usar `check=False` + asserção com diagnóstico.

### IN-07: Senha efêmera do smoke transita pelo argv do `docker compose exec`

**File:** `.template-tests/test_08_guia_prova.py:474-483`
**Issue:** A senha gerada entra literal no comando `python manage.py shell -c "...set_password('...')"` — visível em `/proc/<pid>/cmdline` para outros usuários locais durante a execução. Risco baixo (banco de ensaio local, credencial efêmera, mitigação T-08-P4-01 já evita literal no repo), registrado por completude.
**Fix:** Passar a senha via stdin (`manage.py shell` lendo `sys.stdin`) ou variável de ambiente no `exec -e`.

### IN-08: Literal de resposta de sucesso duplicado em três views

**File:** `.template-tests/fixtures/guia/apps/diarias/views.py:98-101, 124-127, 152-155`
**Issue:** O mesmo HTML de fechamento de modal + header `HX-Trigger` aparece três vezes. Já coberto pela correção sugerida em WR-02 (helper único); registrado como item de duplicação.
**Fix:** Extrair helper `_resposta_modal_fechado()`.

---

**Sem achados em:** `admin.py`, `apps.py`, `forms.py`, `migrations/0001_initial.py`, `models.py`, `urls.py`, `_confirmar_exclusao_modal.html`, `_form_modal.html` (exceto o alvo do swap coberto em WR-02), `dashboard.html` (JS com escape consistente, `rotuloMes` sem `new Date`, fallbacks de paleta corretos), `tests/*` do app, `.dockerignore` (inclusão de `dados/` correta). A migração manual está consistente com `models.py` (a suíte de prova valida via `makemigrations --check` in-container) e a suíte de vazamento tem guardas adequadas contra passar em vácuo.

---

_Reviewed: 2026-08-26T12:55:13Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
