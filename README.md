# Template Django com Copier

Este repositório é o **template-fonte** de uma família de sistemas Django. A
árvore contém arquivos Jinja e não é executável: nunca rode Django ou Docker
Compose diretamente neste checkout. Use o Copier para criar um repositório
derivado, autocontido e versionado, e execute todos os comandos de runtime
somente no sistema gerado. O `README.md` que aparece no sistema gerado é outro
arquivo, renderizado a partir de `README.md.jinja`, e é o guia da operação
cotidiana daquele sistema específico.

## Os três ciclos de trabalho

Todo comando deste README pertence a exatamente um de três ciclos, com
frequências muito diferentes entre si. Identifique o ciclo antes de digitar
qualquer comando: isso evita rodar um script de release dentro de um sistema
gerado ou um comando de runtime na raiz do template.

- **Evoluir o template** — raro, apenas quando o core muda. Rode a regressão
  completa de `.template-tests/` e só então crie a tag semver. Os scripts
  `.sh` do template rodam uma vez por release, nunca por sistema. Veja
  [Regressão do template](#regressão-do-template) e
  [Releases e atualização do núcleo](#releases-e-atualização-do-núcleo).

- **Nascer um sistema** — uma vez por sistema: `copier copy` da tag estável,
  depois `.env`, Compose, migrate e createsuperuser e, quando for publicar,
  proxy/TLS. Nenhum script do template é executado no nascimento — a tag já
  foi validada pela regressão. Veja
  [Nascimento local de um sistema](#nascimento-local-de-um-sistema) e
  [Publicação com proxy, TLS e DNS](#publicação-com-proxy-tls-e-dns).

- **Operar um sistema** — dia a dia: `docker compose logs/exec/restart` e a
  suíte Django do próprio sistema (`manage.py test`), guiado pelo README
  renderizado dentro do sistema gerado. Os `.template-tests/` nem existem no
  sistema gerado.

| Ciclo | Quando | Comandos-chave | Seção de referência |
| --- | --- | --- | --- |
| Evoluir o template | Antes de cada release do core | `.template-tests/*.sh` + tag semver | [Regressão do template](#regressão-do-template) e [Releases e atualização do núcleo](#releases-e-atualização-do-núcleo) |
| Nascer um sistema | Uma vez por sistema | `copier copy` + `.env` + `docker compose up` | [Nascimento local de um sistema](#nascimento-local-de-um-sistema) e [Publicação com proxy, TLS e DNS](#publicação-com-proxy-tls-e-dns) |
| Operar um sistema | Cotidiano do sistema gerado | `docker compose logs/exec` + `manage.py test` | README renderizado dentro do próprio sistema gerado |

> **Regra-resumo:** `.sh` = só antes de tag; `copier copy` = só no
> nascimento; `copier update` = só ao puxar uma versão nova do template para
> um sistema existente.

## Ferramenta isolada e versão aprovada

Instale o CLI somente no ambiente local do template; ele não pertence a
`requirements.txt` nem ao Python global:

```bash
python3 -m venv .venv-template
.venv-template/bin/pip install 'copier==9.17.1'
.venv-template/bin/copier --version
```

O diretório `.venv-template/` é ignorado pelo Git. Não substitua a versão
pinada sem uma nova avaliação de procedência e uma atualização explícita deste
contrato.

## Estrutura do repositório do template

Três regras explicam qualquer arquivo desta árvore:

- **Sufixo `.jinja` = renderizado.** `_templates_suffix: .jinja` no
  `copier.yml`. O arquivo `compose.yml.jinja` vira `compose.yml` no sistema
  gerado, com as respostas interpoladas. `_envops.undefined` é
  `jinja2.StrictUndefined`: uma variável não declarada aborta a renderização
  em vez de virar string vazia silenciosa.
- **Sem sufixo = verbatim.** `tailwind.config.js`, `core/tema.py`,
  `core/templatetags/navegacao.py` e todo o `core/` chegam byte a byte ao
  sistema gerado. É o que torna o `copier update` previsível: o derivado não
  edita esses arquivos, logo eles nunca conflitam.
- **`_exclude` = não sai daqui.** `.planning/`, `.template-tests/`,
  `copier.yml`, `CLAUDE.md`, `IDEIA.md` e `REVIEW.md` são do template e não
  existem no sistema gerado. `README.md` é exceção estudada: `README.md.jinja`
  renderiza e substitui este arquivo durante a cópia, porque o `_exclude` do
  Copier se aplica ao caminho de **destino**.

| Caminho | Papel |
| --- | --- |
| `copier.yml` | Perguntas, validators, `_exclude` e `_skip_if_exists`. Não sai do template. |
| `config/settings/*.py.jinja` | Settings por ambiente; `base.py.jinja` valida `COR_PRIMARIA` no boot. |
| `core/` | Kernel verbatim: usuário customizado, shell, login, tema, templatetags, testes. |
| `core/static/src/input.css` | **Fonte física de toda cor.** Verbatim. |
| `core/static/src/dominio.css` | Stub enviado uma vez; a partir daí é do derivado (`_skip_if_exists`). |
| `core/templates/core/_nav.html` | Navegação do núcleo. Verbatim — nunca editar no derivado. |
| `core/templates/core/_nav_dominio.html.jinja` | Stub dos itens do domínio; vira propriedade do derivado (`_skip_if_exists`). |
| `tailwind.config.js` | Verbatim, sem nenhum valor de cor — só aponta para `var(--cor-*)`. |
| `apps/` | App exemplo, renderizado apenas quando `incluir_app_exemplo` é `true`. |
| `ops/` | Runbook de migração, vhost Nginx e gerador de ícones PWA. |
| `.template-tests/` | Regressão do template. **Não** existe no sistema gerado. |

### Os dois arquivos que passam a ser do derivado

`_skip_if_exists` no `copier.yml` lista exatamente dois caminhos:

```yaml
_skip_if_exists:
  - core/templates/core/_nav_dominio.html
  - core/static/src/dominio.css
```

Depois da primeira cópia, o `copier update` **nunca** reescreve esses dois
arquivos — nem quando o template muda o próprio conteúdo padrão deles. É o
mecanismo que permite ao derivado ter menu e tokens de estado próprios sem
jamais tocar em arquivo upstream. A lista não é decorativa: sem ela, o
primeiro `copier update` que mude a resposta correspondente grava
`<<<<<<< before updating` dentro do arquivo do derivado.

## Nascimento local de um sistema

A sequência abaixo leva do template a um sistema navegável sem editar código.
Todos os comandos Django e Docker acontecem dentro do diretório gerado, nunca
na raiz do template. Não há `_tasks`, migrations Copier ou qualquer automação
oculta após a cópia: cada passo é consciente e auditável.

1. **Pré-requisitos.** Docker Engine com o plugin Docker Compose, Python 3,
   Git e curl instalados no host; o Copier aprovado instalado na
   `.venv-template` (seção anterior).

2. **Escolha uma tag estável do template**, por exemplo `v0.1.0`. Sistemas
   nascem de releases revisadas, não de commits arbitrários. Para criar a
   tag, veja [Criando a tag de release](#criando-a-tag-de-release).

3. **Gere a cópia a partir de um diretório de trabalho fora do destino:**

   ```bash
   /caminho/para/template/.venv-template/bin/copier copy /caminho/para/template /caminho/para/novo-sistema
   ```

4. **Responda as oito perguntas.** Os validators recusam valores fora do
   contrato **antes** de renderizar qualquer arquivo:

   | Pergunta | Tipo | Default | O que o validator exige |
   | --- | --- | --- | --- |
   | `sistema_nome` | str | — | não vazio |
   | `sistema_slug` | str | nome em minúsculas, sem espaços | só `[a-z0-9]`, sem separadores |
   | `sistema_hostname` | str | `<slug>.exemplo.gov.br` | hostname DNS completo, sem esquema, caminho ou porta |
   | `sistema_porta` | int | `8000` | entre 1024 e 65535 |
   | `sistema_banco` | str | `<slug>` | só `[a-z0-9]`, sem separadores |
   | `sistema_sigla` | str | iniciais do nome, em maiúsculas | não vazia |
   | `cor_primaria` | str | `#1e40af` | formato `#RRGGBB` |
   | `incluir_app_exemplo` | bool | `true` | — |

   Segredos nunca são respostas Copier: as respostas ficam em
   `.copier-answers.yml`, arquivo sem credenciais que será versionado no
   repositório do sistema. `cor_primaria` é a única resposta que vira
   comportamento de runtime — veja
   [O design system herdado](#o-design-system-herdado).

5. **Entre no projeto gerado e crie o ambiente local:**

   ```bash
   cd /caminho/para/novo-sistema
   cp .env.example .env
   ```

   O `.env.example` já vem pré-preenchido com slug, porta e identidade
   respondidos no Copier; falta essencialmente preencher os segredos, que são
   valores locais do `.env` e nunca entram no Git.

6. **Gere a `SECRET_KEY` localmente** e cole o resultado no `.env`:

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

7. **Preencha `POSTGRES_PASSWORD` e `DATABASE_URL` de forma coerente:** a
   mesma senha deve aparecer nos dois valores. O `DATABASE_URL` já traz
   usuário e banco derivados do slug; troque apenas o placeholder de senha
   pelos mesmos caracteres usados em `POSTGRES_PASSWORD`.

8. **Credenciais R2** (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
   `R2_ENDPOINT`, `R2_BUCKET`) pertencem ao serviço `backup` e podem
   permanecer com os placeholders durante a prova inicial local. Quando o
   backup entrar em operação, preencha-as diretamente no `.env`; nunca crie
   perguntas Copier, valores padrão reais ou commits para essas credenciais.

9. **(Opcional) Insira os logos oficiais.** Substitua
   `core/static/img/logo-entidade.svg` (logo da entidade) e
   `core/static/img/logo-subsistema.svg` (logo deste sistema) mantendo nome e
   extensão; se quiser ícones PWA próprios, substitua os três
   `core/static/img/icon-*.png` ou rode `python3 ops/gerar_icones_pwa.py`.
   Os placeholders neutros funcionam — o passo pode ficar para depois; a
   referência completa é a seção "Customização de marca" do README do
   sistema gerado.

10. **Inicie o repositório do sistema e faça o primeiro commit**, preservando
    o `.copier-answers.yml` (sem credenciais) exigido pelos updates futuros:

    ```bash
    git init
    git add .
    git commit -m "chore: inicia sistema gerado pelo Copier"
    ```

11. **Valide a configuração resolvida do Compose:**

    ```bash
    docker compose --env-file .env config -q
    ```

12. **Suba banco e aplicação.** O serviço `backup` fica de fora até existirem
    credenciais R2 reais:

    ```bash
    docker compose up -d --build db web
    ```

    Os dados do banco ficam em `./dados/pg`, dentro do diretório do sistema
    (bind mount), e sobrevivem a `docker compose down -v`. O diretório é
    criado automaticamente no primeiro `up` e pertence ao uid 999 (usuário
    postgres do container).

13. **Acompanhe a inicialização pelos logs:**

    ```bash
    docker compose logs -f web
    ```

14. **Aplique as migrações** (comando não interativo com `-T`, adequado a
    scripts e automação):

    ```bash
    docker compose exec -T web python manage.py migrate --noinput
    ```

15. **Crie o administrador.** Este comando é interativo: o operador digita
    e-mail e senha no terminal, por isso ele usa `exec` sem `-T`:

    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

16. **Confirme a saúde do processo web**, usando a porta respondida no Copier:

    ```bash
    curl -fsS http://127.0.0.1:<porta>/healthz
    ```

### Telas navegáveis da cópia com app exemplo

Com o sistema no ar e o administrador criado, abra no navegador (substitua
`<porta>` pela resposta Copier):

| URL | Tela |
| --- | --- |
| `http://127.0.0.1:<porta>/login/` | Login por e-mail e senha com o CTA `Entrar`. |
| `http://127.0.0.1:<porta>/` | Shell autenticado: aside de navegação no desktop, gaveta no móvel e breadcrumbs. |
| `http://127.0.0.1:<porta>/exemplo/` | CRUD de referência: tabela paginada, ordenação, filtros e criação/edição em modal HTMX (`Novo item`). |
| `http://127.0.0.1:<porta>/exemplo/dashboard/` | Dashboard de exemplo: KPIs e dois gráficos ECharts com drill-down para a lista filtrada. |

As duas últimas URLs existem apenas quando `incluir_app_exemplo=true`. A
operação cotidiana — logs, ícones PWA, remoção do app exemplo, atualizações do
template — é descrita no README renderizado dentro do próprio sistema gerado.

### Convenção de portas da família

A porta 8000 é apenas o default e pode ser sobrescrita pela pergunta Copier.
Mantenha uma alocação documentada para evitar colisões no host:

| Faixa | Uso convencional |
| --- | --- |
| 8000 | Novo sistema / desenvolvimento local |
| 8001 | Primeiro sistema publicado da família |
| 8002 | Segundo sistema publicado da família |
| 8003–8099 | Próximos sistemas, por registro operacional |

O Compose continua ligado a `127.0.0.1`; o proxy do host é a única fronteira
de exposição externa.

## O design system herdado

Um sistema recém-nascido já vem com o padrão visual inteiro da família — não
há passo de reskin. Esta seção existe para que o derivado saiba **onde** cada
peça mora e, principalmente, o que ele não deve editar.

### A fonte física das cores

`core/static/src/input.css` é o único arquivo com valores de cor. Ele declara
**23** variáveis em `:root` (tema claro) e sobrescreve **20** delas no bloco
`[data-tema="escuro"]` — os tokens do escuro são um subconjunto estrito dos
do claro, nunca um vocabulário paralelo. Os três que **não** invertem são
`--cor-baseline`, `--cor-destructive` e `--cor-secundaria`: linha de base de
gráfico, vermelho de ação destrutiva e dourado institucional funcionam nos
dois temas com o mesmo valor.

O `tailwind.config.js` não contém nenhum valor: cada cor nomeada aponta para
`var(--cor-*)`.

```js
colors: {
  page: "var(--cor-page)",
  surface: "var(--cor-surface)",
  // ... nenhum literal, em nenhuma entrada
}
```

A consequência é o que torna o tema escuro barato: os utilitários que o
Tailwind gera (`bg-page`, `text-ink`, `border-grid`) resolvem em **runtime**,
nos dois temas, com uma única regra CSS cada. Trocar de tema não recompila
nada.

Nunca escreva hex em template ou em JS de template. A regressão falha se
algum aparecer.

### `COR_PRIMARIA` resolve em runtime, sem rebuild

A cor de marca é a única resposta Copier que vira comportamento de runtime.
O caminho completo:

```
.env → settings.COR_PRIMARIA → core.tema.css_da_marca() → <style> em base.html
```

`config/settings/base.py` valida o valor contra `#RRGGBB` com `re.fullmatch`
no boot e levanta `ImproperlyConfigured` se não bater — a cor é interpolada
em CSS, e essa validação é a barreira contra injeção via `.env`.

`core/tema.py` deriva a família inteira de uma única cor com `colorsys`:

| Chave | Papel |
| --- | --- |
| `brand` | a cor respondida, sem alteração |
| `brand-hover` | tom de hover |
| `brand-ink` | tom pressionado / texto de ênfase |
| `brand-tint` | fundo tênue do item ativo |
| `seq-750` `seq-600` `seq-450` `seq-300` | rampa sequencial de gráfico, do mais forte ao mais fraco |

São as **8** chaves de `_CHAVES_MARCA`, derivadas nos dois temas — 16
variáveis geradas por `css_da_marca()` a partir de um único hex. Trocar
`COR_PRIMARIA` no `.env` e reiniciar o container muda a marca inteira,
**sem** rebuild do CSS. `.template-tests/test_07_cor_runtime.sh` prova
exatamente isso.

**`--cor-brand-tx` é a exceção, e é deliberada.** É a cor do **texto** sobre
o fundo da marca, e **não** é derivada de `COR_PRIMARIA`: são dois hex planos
no `input.css` — `#ffffff` no claro e `#0f0e0d` no escuro, este último
idêntico ao `--cor-page` do tema escuro. Ele é fixo porque o texto sobre a
marca só tem duas respostas possíveis (claro ou escuro), e derivá-lo da cor
introduziria uma variável onde a decisão é binária.

Botão primário usa `bg-brand text-brand-tx`, nunca `text-white`: no tema
escuro o fundo da marca é claro, e `text-white` fica ilegível — com o hover,
que clareia ainda mais o fundo, como pior caso.

### Tema escuro

```js
darkMode: ["selector", '[data-tema="escuro"]']
```

O atributo vive em `<html>`. A preferência é persistida em `localStorage`
(chave `tema`, valores `claro`, `escuro` e `auto`; o default é `auto`, que
segue o sistema operacional) — **nunca** em cookie, porque uma navegação
servida pelo cache do navegador não passaria pelo servidor a tempo. O
`base.html` aplica o atributo antes de qualquer CSS pintar, o que elimina o
flash de tema errado no recarregamento, e dispara `tema:alterado` para que os
gráficos se repintem sem reload.

### Elevação, raio, régua e fonte

**Elevação** — no tema escuro, elevação é **luminosidade**, não sombra. O
mapa dos três níveis está escrito em `core/templates/core/shell.html`:

| Nível | Receita clara | Receita escura |
| --- | --- | --- |
| Base | `bg-surface border border-grid`, sem sombra | idem (o token já muda) |
| Elevado | `bg-surface border border-grid shadow-sm` | `dark:bg-surface-2 dark:shadow-none` |
| Flutuante | `bg-surface shadow-lg` | `dark:bg-surface-3 dark:shadow-md` |

**Raio** — único, de 2px, com as seis chaves colapsadas (`DEFAULT`, `sm`,
`md`, `lg`, `xl`, `2xl`). `rounded-lg` e `rounded-sm` produzem o mesmo
resultado por construção: não há como um template desalinhar o raio.

**Régua tipográfica** — seis degraus, com teto real em 20px:

| Classe | Tamanho | Uso típico |
| --- | --- | --- |
| `text-xs` | 11px | metadados |
| `text-sm` | 12px | apoio |
| `text-base` | 13px | corpo e botões |
| `text-md` | 14px | ênfase de corpo |
| `text-lg` | 16px | título de seção e de card |
| `text-xl` | 20px | título de página |

`fontSize` fica em `theme`, **não** em `theme.extend`. A diferença importa:
`extend` somaria à escala default do Tailwind e `text-2xl`…`text-9xl`
continuariam gerando regra, furando o teto. Em `theme`, a escala é
substituída e o teto de 20px passa a ser propriedade da build.

**Fonte** — pilha `system-ui`, sem webfont e sem requisição de rede.

**Anel de foco** — regra única em `@layer base`: outline sólido de 2px na cor
da marca, com offset, em qualquer elemento focável. Não há declaração de foco
espalhada por template.

### Classes de componente

O `@layer components` do `input.css` entrega oito classes: `.results`,
`.module`, `.form-row`, `.btn` e as quatro variações `.btn--primaria`,
`.btn--secundaria`, `.btn--neutro`, `.btn--destrutiva`.

As oito estão na `safelist` do `tailwind.config.js` por necessidade, não por
excesso de zelo: o JIT do Tailwind poda qualquer seletor que não apareça
literalmente no conteúdo varrido, e uma classe usada só via `data-*` ou só
pelo derivado desapareceria do CSS.

### Paleta de gráfico

Os gráficos não têm cor cravada no JS. A view monta `paleta_graficos` a
partir de `core.tema.familia_marca(settings.COR_PRIMARIA)`, com listas
separadas para claro e escuro, e entrega ao template por
`json_script:"paleta-graficos"`. O JS lê o JSON e, no evento
`tema:alterado`, refaz `dispose()` + `init()` — os gráficos repintam sem
recarregar a página.

O cromo do gráfico (eixo, grade, tooltip, borda de fatia) **não** vem do
JSON: é lido de `getComputedStyle` em runtime, para acompanhar o tema pelo
mesmo caminho que o resto da página.

A rampa sequencial tem quatro degraus (`seq-750`, `seq-600`, `seq-450`,
`seq-300`), todos derivados da marca e todos degraus de **dado** — nenhum
deles é token de fundo. O donut do app exemplo consome os quatro.

### Tokens de estado do domínio

`core/static/src/dominio.css` é o lugar — e o único lugar — dos tokens de
estado do seu sistema ("concluído", "atrasado", "em análise"). O template
envia um stub comentado uma única vez e nunca mais toca no arquivo.

O contrato, resumido (a versão completa está nos comentários do próprio
stub):

1. Cada estado declara um **par**: `--cor-<estado>` (o matiz) e
   `--cor-<estado>-tx` (o par de texto). No tema escuro, normalmente só a
   variante `-tx` precisa de um par clareado.
2. A ponte entre dado e cor fica **fora** de qualquer `@layer` — dentro dele
   o Tailwind poda a regra, porque `data-*` só resolve em runtime.
3. Piso de contraste nos dois temas: 4,5:1 para texto, 3:1 para elemento
   gráfico. Valide também para daltonismo antes de fixar os matizes.

Nenhum nome de estado concreto sobe do template: os pares de status do padrão
de referência da família são vocabulário do domínio **dele**. O que sobe é a
mecânica do par e a disciplina.

### A guarda de contraste que o derivado herda

`core/tests/contraste.py` viaja **dentro** do sistema gerado — não é helper
de template. Ele é a fonte única da fórmula WCAG (`luminancia_relativa`,
`contraste`, `tokens_do_input_css`) e alimenta os testes de contraste que
nascem junto com o sistema. Quando o derivado trocar `COR_PRIMARIA` ou
acrescentar tokens em `dominio.css`, a suíte do próprio sistema é quem
reprova um par ilegível.

## Ponto de extensão da navegação

O derivado põe os próprios itens no menu **sem editar um único arquivo do
núcleo**. São três peças.

### 1. `_nav.html` — do núcleo, nunca editar

```django
<nav aria-label="Navegação principal" class="flex flex-col gap-1">
  {% item_nav "core:shell" "Início" "casa" %}
  {% nav_dominio %}
</nav>
```

Toda edição aqui vira conflito no próximo `copier update`. O arquivo tem um
item só — "Início", a rota `core:shell` que todo sistema gerado possui — e a
tag de extensão.

### 2. `{% nav_dominio %}` — a inserção tolerante

Não é `{% include %}`. O `{% include %}` do Django com string literal levanta
`TemplateDoesNotExist` quando o arquivo some, e derrubaria com 500 **toda**
página que estende `shell.html`. O Django não tem `ignore missing` — isso é
Jinja2.

Como `_nav_dominio.html` pertence ao derivado, apagá-lo é um estado previsto:
o resultado tem que ser menu sem itens de domínio, nunca erro.

### 3. `_nav_dominio.html` — do derivado, uma linha por item

```django
{% item_nav "app:rota" "Rótulo" "icone" "prefixo-opcional" "excecoes-opcionais" %}
```

| Argumento | Obrigatório | O que faz |
| --- | --- | --- |
| `rota` | sim | **Nome** da rota (`app:nome`), não a URL. Rota inexistente → o item não aparece, sem erro. |
| `rotulo` | sim | Texto do item. |
| `icone` | não | Nome de um ícone embutido. Disponíveis: `casa`, `grafico`, `lista`. |
| `prefixo` | não | Acende o item também nas rotas-filhas (ex.: `"/clientes/"`). |
| `excecoes` | não | Caminhos sob `prefixo`, separados por espaço, que **não** devem acender este item. |

O estado ativo vem por construção: fundo `bg-brand-tint`, texto
`text-brand-ink`, filete vertical de 2px à esquerda e `aria-current="page"`.
Nenhum derivado reescreve essa string de classes.

**Sobre `excecoes`.** Sem ela, um item com `prefixo="/clientes/"` acende
junto com o item de `/clientes/relatorio/`, e a página passa a ter dois
`aria-current="page"`. A exceção é **declarada no sítio da chamada**, não
inferida: uma `inclusion_tag` renderiza um item por vez, sem enxergar os
irmãos, e qualquer desempate automático dependeria da ordem das linhas no
arquivo — frágil exatamente no arquivo que pertence ao derivado.

A correspondência **exata** nunca é anulada por `excecoes`: um item continua
ativo na própria URL, aconteça o que acontecer. É o que impede que uma
exceção mal escrita apague o estado ativo do item dono da rota.

Exemplo real, o que o app exemplo renderiza:

```django
{% item_nav "exemplo:dashboard" "Dashboard" "grafico" %}
{% item_nav "exemplo:item_listar" "Itens (CRUD)" "lista" "/exemplo/" "/exemplo/dashboard/" %}
```

Sem `request` no contexto (`render_to_string()` sem `request=`, template de
e-mail, geração de PDF, comando de management) não há caminho atual: o item
renderiza inativo em vez de derrubar o render.

`.template-tests/test_07_nav_extensao.py` prova o contrato inteiro — inclusive
que remover os itens do app exemplo não toca em nenhum arquivo do `core`,
conferido por sha256 de toda a subárvore.

## Publicação com proxy, TLS e DNS

O sistema gerado permanece escutando apenas em loopback:
`WEB_BIND_ADDRESS=127.0.0.1` é invariante e o Compose publica a porta somente
em `127.0.0.1:<porta>`. Quem termina TLS e publica o sistema é exclusivamente
o Nginx do host; a aplicação nunca é exposta diretamente. A ordem de
publicação é:

1. **Prepare a VM** com Docker Engine, plugin Docker Compose, Nginx e Certbot
   pelos repositórios oficiais da distribuição, e repita nela o nascimento
   local acima com um `.env` de produção
   (`DJANGO_SETTINGS_MODULE=config.settings.prod`, `DEBUG=false`, segredos
   novos gerados na própria VM).

2. **Mantenha `WEB_BIND_ADDRESS=127.0.0.1`** no `.env` de produção. A porta
   da aplicação continua acessível somente em `127.0.0.1:<porta>` dentro da
   VM.

3. **Crie o registro DNS** do hostname respondido no Copier apontando para o
   IP público da VM e aguarde a propagação.

4. **Libere somente as portas 80 e 443** no firewall do host; nenhuma outra
   porta do sistema é pública.

5. **Publique o vhost e emita o certificado** por um dos dois caminhos
   abaixo. A diferença estrutural entre eles: no Caminho A o Certbot gera os
   blocos TLS a partir do bloco `:80` já ativo; no Caminho B o vhost
   renderizado já nasce com os blocos 443 e o redirect 301, e por isso o
   certificado precisa ser emitido antes, com o Nginx parado.

### Caminho A — vhost em `conf.d` com `certbot --nginx` (padrão operacional da família CFC)

É o fluxo usado nas VMs da família CFC. Crie
`/etc/nginx/conf.d/<hostname>.conf` contendo apenas o bloco `:80` com o proxy
reverso para o serviço em loopback:

```nginx
server {
    server_name <hostname>;

    location / {
        proxy_pass http://127.0.0.1:<porta>;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

Valide e recarregue sem interromper o serviço:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Em seguida, emita o certificado sem parar o Nginx:

```bash
sudo certbot --nginx -d <hostname>
```

O Certbot reescreve o próprio `/etc/nginx/conf.d/<hostname>.conf`,
adicionando o bloco 443 com TLS (`ssl_certificate`,
`options-ssl-nginx.conf`, `ssl-dhparams.pem`) e o redirect 301 de HTTP para
HTTPS — trechos marcados com "managed by Certbot".

### Caminho B — vhost renderizado com certificado standalone

Alternativa válida que usa o vhost completo renderizado pelo Copier. Como
`ops/nginx/<slug>.conf` já traz os blocos 443 e o redirect 301 prontos,
referenciando os arquivos em `/etc/letsencrypt`, o certificado precisa
existir antes de o vhost ser ativado:

```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone -d <hostname>
```

Instale o vhost já gerado — o Copier renderiza `ops/nginx/<slug>.conf` com
`server_name` e `proxy_pass` preenchidos — e habilite-o:

```bash
sudo install -m 0644 ops/nginx/<slug>.conf /etc/nginx/sites-available/<slug>.conf
sudo ln -sf /etc/nginx/sites-available/<slug>.conf /etc/nginx/sites-enabled/<slug>.conf
```

Valide a configuração e reinicie o Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Mesmo quem adota o Caminho A pode consultar `ops/nginx/<slug>.conf` como
referência do formato final do vhost com TLS.

6. **Valide externamente**, qualquer que seja o caminho escolhido: de fora
   da VM, `https://<hostname>/healthz` deve responder com sucesso. O vhost
   termina TLS, redireciona HTTP para HTTPS e encaminha as requisições ao
   serviço em loopback. As invariantes permanecem: aplicação escutando
   somente em loopback, Nginx do host como única fronteira de exposição e
   apenas as portas 80 e 443 públicas.

Os detalhes de migração para uma VM limpa — transferência, restauração de dump
customizado, recuperação e ensaio periódico de restore — vivem no runbook
renderizado [`ops/MIGRACAO.md`](ops/MIGRACAO.md.jinja) dentro do sistema
gerado. Um primeiro nascimento não envolve restore: o banco nasce vazio e é
construído pelas migrações; não repita os comandos destrutivos de restauração
fora do cenário de migração descrito naquele runbook.

## Regressão do template

Execute a regressão no checkout do template antes de cada release. Ela tem
três camadas: contratos da fonte, ensaio real de nascimento e inspeção manual
complementar.

```bash
# Limpa o banco de ensaio deixado por rodadas anteriores no host
.template-tests/ensaio_django.sh derrubar

# Contratos da fonte: renderização, update e auditoria estática
.template-tests/test_copier_copy.sh
.template-tests/test_copier_update.sh
python3 -m unittest discover -s .template-tests -p 'test_*.py'

# Prova de que COR_PRIMARIA resolve em runtime, sem rebuild
.template-tests/test_07_cor_runtime.sh
.template-tests/ensaio_django.sh derrubar

# Ensaio real de nascimento: cópia descartável, boot e suíte Django
.template-tests/test_05_nascimento.sh
```

O primeiro `derrubar` evita que um banco de ensaio esquecido de uma rodada
anterior dispute containers, portas ou espaço com as suítes seguintes; o
segundo repete a limpeza porque `test_07_cor_runtime.sh` recria o banco para
provar a resolução da cor em runtime.

> **Orçamento de tempo.** Rode **cada** etapa com timeout próprio de 600 s;
> não encadeie as sete num único comando de timeout curto. As etapas 2, 3, 5
> e 7 fazem gerações completas de sistema, e a 7 sobe Compose, migra e roda a
> suíte Django inteira dentro da cópia. Com cache Docker frio, a primeira
> criação pode passar de 600 s sozinha — nesse caso repita a mesma etapa em
> background com polling e espere o código de saída real. Só reprova a
> regressão uma etapa que **terminou** com código diferente de zero.

Antes de qualquer rodada, confirme que o host está limpo com
`docker compose ls -a`: nenhum projeto de ensaio ou nascimento pode estar de
pé. Uma cópia retida por `--keep` de uma sessão anterior é pior que inútil —
a credencial efêmera dela morreu junto com a sessão que a gerou, e ela ainda
disputa portas e espaço com a regressão nova.

- `.template-tests/test_copier_copy.sh` cria somente destinos temporários,
  exercita as variantes com e sem o app exemplo, rejeita respostas inválidas e
  audita a árvore renderizada. A auditoria procura identificadores legados
  como unidades lexicais, sem confundir uma sequência de caracteres dentro de
  outro valor neutro; o único metadado desconsiderado é `_src_path` em
  `.copier-answers.yml`, campo que o próprio Copier precisa para atualizar um
  projeto derivado.
- `.template-tests/test_copier_update.sh` ensaia o ciclo A → B → C de
  `copier update` usando somente repositórios e tags temporários.
- Os contratos Python `test_04_*.py` fixam identidade, app exemplo opcional,
  backup, scripts de operação e o ambiente de `collectstatic` nas variantes
  renderizadas.
- `.template-tests/test_06_persistencia.py` fixa o contrato de persistência:
  `compose.yml` usa bind mount e não named volume, `.env.example` documenta
  `PGDATA_DIR`, o `.gitignore` do template ignora `dados/` e o
  `.gitignore.jinja` renderizado protege `.env` e `/dados/` no sistema
  gerado.
- `.template-tests/test_quick_comentarios_template.py` varre os templates
  atrás de comentário `{# #}` multilinha inline — o padrão que vazava texto
  de comentário para a tela.
- `.template-tests/test_07_tokens.py` prova o contrato dos tokens de design:
  a fonte `system-ui`, a régua tipográfica com teto de 20px e a ausência de
  classes mortas da paleta antiga.
- `.template-tests/test_07_nav_extensao.py` prova o ponto de extensão da
  navegação: um derivado põe os próprios itens em `_nav_dominio.html` sem
  tocar em `_nav.html`.
- `.template-tests/test_07_cor_runtime.sh` prova que `COR_PRIMARIA` resolve
  em runtime — trocar o valor no `.env` e reiniciar o container muda a marca
  sem exigir rebuild do CSS.
- `.template-tests/test_05_nascimento.sh` é o ensaio real de nascimento: gera
  uma cópia descartável com o app exemplo, preenche um `.env` apenas com
  segredos efêmeros, valida a configuração do Compose, sobe somente os
  serviços `db` e `web`, migra, cria um administrador de ensaio não
  interativo, executa a suíte Django de `core` e `apps.exemplo`, faz smoke
  HTTP das rotas de saúde e de login e remove exclusivamente os recursos que
  criou. Com `--keep`, ele retém a cópia aprovada e informa destino, projeto
  Compose e URL para inspeção posterior.

Todas as suítes que invocam `copier copy` usam `--vcs-ref=HEAD`: sem essa
flag, o Copier renderizaria sempre a última tag publicada, e a regressão
provaria o template de uma release passada, não o estado atual do checkout.

### A ferramenta `ensaio_django.sh`

`.template-tests/ensaio_django.sh` **não é suíte** — o nome não começa com
`test_` de propósito, para que nenhum inventário a confunda com regressão.
Ela existe porque o checkout do template não é, por si só, um projeto Django
rodável: não há `compose.yml` (só `compose.yml.jinja`), nem
`config/settings/base.py` (só `.py.jinja`), nem container `web`. É como se
roda qualquer alvo Django contra uma cópia gerada, para desenvolvimento e
depuração da Fase 07. Subcomandos: `subir`, `porta`, `url`, `destino`,
`testar`, `executar`, `compor` e `derrubar`. O banco criado por `subir`
**sobrevive** entre invocações de propósito — reúso é o que torna chamadas
repetidas baratas — e `derrubar` é como se limpa o host inteiro (containers,
volumes, `dados/` e o diretório da cópia).

Nenhum desses comandos automatiza cliques nem regressão visual: o ensaio de
nascimento prova comportamento via suíte Django e alcance HTTP. A inspeção
breve das telas no navegador (login, shell, CRUD e dashboard) na cópia retida
com `--keep` é um checkpoint manual complementar do operador, não uma etapa
automatizada. Os ensaios usam somente recursos temporários e não substituem
revisão, testes e commit em cada sistema derivado.

## Releases e atualização do núcleo

Publique mudanças conscientes do template em tags semver (`v0.1.0`, `v0.2.0`
etc.). Antes de criar uma tag, revise o diff gerado, execute as verificações
cabíveis e só então registre a release. Sistemas derivados só recebem mudanças
quando o operador decide atualizar para uma tag posterior.

### Criando a tag de release

Pré-condições: árvore limpa (`git status --short` sem saída) e a regressão
completa da seção [Regressão do template](#regressão-do-template) verde.

```bash
# criar a tag anotada da release
git tag -a v0.2.0 -m "descrição da release"

# listar as tags existentes
git tag

# inspecionar o conteúdo de uma tag
git show v0.2.0 --stat
```

A `v0.2.0` entrega as Fases 6 e 7 juntas: marca por arquivo fixo e
persistência em bind mount (Fase 6); design system com tokens de cor em
variáveis CSS, tema escuro, elevação, raio único, régua tipográfica, fonte
`system-ui`, focus-ring, classes de componente e o ponto de extensão da
navegação (Fase 7).

Sem `--vcs-ref`, `copier copy` e `copier update` renderizam sempre a **última
tag** (ordenada pelo algoritmo PEP 440), nunca o HEAD — é por isso que
sistemas nascem de releases. Se o repositório não tem nenhuma tag, o Copier
cai no HEAD com uma versão sintética como `0.0.0.postN.dev0+hash` e, se a
árvore estiver suja, emite `DirtyLocalWarning` e inclui as mudanças não
commitadas na cópia — nunca gere um sistema real nesse estado. A opção
`--vcs-ref=HEAD` existe apenas para ensaio e depuração do template, nunca
para nascimento de produção.

### Tag publicada não se move

Enquanto uma tag existe **apenas localmente**, corrigi-la é barato: apagar e
recriar sobre o commit certo não afeta ninguém, porque nenhum sistema
derivado a consumiu. Basta conferir antes que ela realmente não saiu da
máquina:

```bash
git ls-remote --tags origin | grep v0.2.0
# sem saída: a tag nunca foi publicada, recriar é seguro

git tag -d v0.2.0
git tag -a v0.2.0 -m "descrição da release"
```

**Depois do `git push`, a regra inverte e não tem exceção: tag publicada não
se move.** Se um defeito aparecer numa release já publicada, a resposta é uma
**versão nova** — `v0.2.1` —, nunca a mesma tag apontando para outro commit.

O motivo é o Copier. Ele resolve `--vcs-ref v0.2.0` no momento da cópia ou do
update: mover a tag reescreveria, sob os pés de todo derivado que já
atualizou, o que "v0.2.0" significa. Dois sistemas com o mesmo
`_commit: v0.2.0` no `.copier-answers.yml` passariam a ter árvores
diferentes, e o `copier update` seguinte de cada um partiria de uma base que
não corresponde ao que ele realmente recebeu — um diff impossível de
auditar.

Por isso a verificação de publicação é **pré-condição bloqueante** de
qualquer recriação de tag, não uma formalidade: é a única coisa que separa
uma correção barata de um estrago irreversível na família inteira.

### Atualizando um sistema derivado

Faça `copier update` exclusivamente com o Git limpo:

```bash
git status --short
# sem saída: árvore limpa
/caminho/para/template/.venv-template/bin/copier update
```

Para mudar uma resposta, use o próprio Copier, nunca edite
`.copier-answers.yml` manualmente. Por exemplo, para remover o app exemplo:

```bash
/caminho/para/template/.venv-template/bin/copier update --data incluir_app_exemplo=false
```

Se houver conflitos, revise os marcadores inline `<<<<<<<`, `=======` e
`>>>>>>>`, escolha a versão correta, rode testes e faça um commit do resultado.
O ensaio contratual desta evolução é A → B → C: copie na tag A, altere o
núcleo e tageie B, execute `copier update` com `incluir_app_exemplo=false`,
valide a mudança e confirme a remoção do exemplo. Faça então outra mudança de
núcleo, tageie C e atualize novamente; a mudança C deve chegar sem ressuscitar
o diretório, settings, URLs ou navegação do exemplo. Antes de B e C, e após
cada estado aprovado, a árvore Git do sistema deve estar limpa e commitada.

Updates são serializados: nunca rode dois `copier update` sobre o mesmo
repositório. Se uma execução for interrompida, use `git status --short` e
`git diff` para registrar e revisar o estado deixado pelo Copier, resolva os
marcadores inline se existirem, teste e faça um commit antes de tentar outro
update. Essa recuperação é auditável pelo histórico Git; não edite o arquivo
de respostas manualmente nem reinicie o update sobre uma árvore suja.

Antes de criar a tag, execute a regressão completa descrita em
`## Regressão do template`, incluindo o ensaio de nascimento.

### Atualizando um sistema que nasceu na v0.1.0

Um derivado que fez reskin à mão antes desta release editou exatamente os
três arquivos que a `v0.2.0` reescreve inteiros. O conflito no `copier
update` é **certo** e não viola o contrato de update sem resolução manual:
esse contrato vale para arquivo que o derivado **não** tenha tocado, e o que
o derivado escreveu à mão é exatamente o que o núcleo passa a entregar.

| Arquivo | O que o derivado fez | Resolução |
|---|---|---|
| `core/templates/core/_nav.html` | apagou o item "Início", colou os itens do domínio | `git checkout --theirs` e recriar os itens em `core/templates/core/_nav_dominio.html`, uma linha por item com `{% item_nav %}` |
| `tailwind.config.js` | fixou a cor de marca no arquivo e acrescentou `borderRadius`/`fontSize`/`fontFamily` à mão | `git checkout --theirs`; a cor fixada à mão vai para `COR_PRIMARIA` no `.env`, **não** para o config — o config passa a ser verbatim e é reescrito a cada update |
| `core/static/src/input.css` | acrescentou o `@layer base { :focus-visible }` no topo | `git checkout --theirs`; qualquer token próprio de estado migra para `core/static/src/dominio.css`, que o update nunca toca |

O `_skip_if_exists` do `copier.yml` protege `core/templates/core/_nav_dominio.html`
e `core/static/src/dominio.css`: uma vez criados pelo derivado, o `copier
update` nunca mais os reescreve, mesmo quando o template muda o próprio
conteúdo padrão desses arquivos.

Roteiro completo, na ordem:

1. Árvore limpa e uma branch de atualização.
2. `copier update --vcs-ref v0.2.0`.
3. Resolver os três arquivos da tabela acima ficando com a versão do
   template (`git checkout --theirs`).
4. Recriar o menu do domínio em `_nav_dominio.html`, um `{% item_nav %}` por
   item.
5. Mover qualquer token de estado próprio do derivado para
   `core/static/src/dominio.css`.
6. Transportar a cor de marca fixada à mão para `COR_PRIMARIA` no `.env`.
7. `docker compose up -d --build` — o CSS é artefato de build, o rebuild é
   obrigatório.
8. Rodar `manage.py test` do próprio sistema derivado.

## Resumo: nascimento completo em comandos

Conclusão executável para quem já conhece (ou não precisa conhecer) os
detalhes acima: a jornada inteira, da tag ao HTTPS, apenas em comandos. O
exemplo cria o sistema **financeiro** em `financeiro.sistemascfc.org`, porta
`12010` — troque nome, hostname e porta para o seu caso.

```bash
# criar a tag da release (uma vez, no template, com árvore limpa e regressão verde)
cd /opt/sistema_base
git tag -a v0.1.0 -m "primeira release do template"

# gerar a cópia a partir da última tag
/opt/sistema_base/.venv-template/bin/copier copy /opt/sistema_base /opt/web/financeiro
```

```text
# responder as oito perguntas
nome:                Financeiro
slug:                financeiro
hostname:            financeiro.sistemascfc.org
porta:               12010
banco:               financeiro
sigla:               FIN
cor primária:        #0F5132
incluir_app_exemplo: true
```

```bash
# entrar no sistema gerado e criar o .env local
cd /opt/web/financeiro
cp .env.example .env

# gerar a SECRET_KEY e a senha do PostgreSQL
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# colar os segredos no .env (SECRET_KEY, POSTGRES_PASSWORD e a mesma senha no DATABASE_URL)
nano .env

# (opcional) substituir core/static/img/logo-*.svg pelos logos oficiais

# iniciar o repositório do sistema
git init
git add .
git commit -m "chore: inicia sistema gerado pelo Copier"

# validar a configuração resolvida do Compose
docker compose --env-file .env config -q

# subir banco e aplicação
docker compose up -d --build db web

# acompanhar a inicialização
docker compose logs -f web

# aplicar as migrações
docker compose exec -T web python manage.py migrate --noinput

# criar o administrador (interativo)
docker compose exec web python manage.py createsuperuser

# confirmar a saúde local
curl -fsS http://127.0.0.1:12010/healthz
```

```text
# criar o registro DNS: A financeiro.sistemascfc.org -> IP público da VM
```

```nginx
# criar /etc/nginx/conf.d/financeiro.sistemascfc.org.conf com o bloco :80
server {
    server_name financeiro.sistemascfc.org;

    location / {
        proxy_pass http://127.0.0.1:12010;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

```bash
# validar e recarregar o Nginx sem interromper o serviço
sudo nginx -t
sudo systemctl reload nginx

# emitir o certificado e ativar TLS (o Certbot reescreve o vhost)
sudo certbot --nginx -d financeiro.sistemascfc.org

# validar externamente
curl -fsS https://financeiro.sistemascfc.org/healthz
```
