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

4. **Responda as oito perguntas:** nome, slug, hostname, porta, banco, sigla,
   cor primária e inclusão do app exemplo. Os validators recusam valores fora
   do contrato antes de renderizar arquivos. Segredos nunca são respostas
   Copier: as respostas ficam em `.copier-answers.yml`, arquivo sem
   credenciais que será versionado no repositório do sistema.

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

9. **Inicie o repositório do sistema e faça o primeiro commit**, preservando o
   `.copier-answers.yml` (sem credenciais) exigido pelos updates futuros:

   ```bash
   git init
   git add .
   git commit -m "chore: inicia sistema gerado pelo Copier"
   ```

10. **Valide a configuração resolvida do Compose:**

    ```bash
    docker compose --env-file .env config -q
    ```

11. **Suba banco e aplicação.** O serviço `backup` fica de fora até existirem
    credenciais R2 reais:

    ```bash
    docker compose up -d --build db web
    ```

12. **Acompanhe a inicialização pelos logs:**

    ```bash
    docker compose logs -f web
    ```

13. **Aplique as migrações** (comando não interativo com `-T`, adequado a
    scripts e automação):

    ```bash
    docker compose exec -T web python manage.py migrate --noinput
    ```

14. **Crie o administrador.** Este comando é interativo: o operador digita
    e-mail e senha no terminal, por isso ele usa `exec` sem `-T`:

    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

15. **Confirme a saúde do processo web**, usando a porta respondida no Copier:

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
# Contratos da fonte: renderização, update e auditoria estática
.template-tests/test_copier_copy.sh
.template-tests/test_copier_update.sh
python3 -m unittest discover -s .template-tests -p 'test_04_*.py'

# Ensaio real de nascimento: cópia descartável, boot e suíte Django
.template-tests/test_05_nascimento.sh
```

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
- `.template-tests/test_05_nascimento.sh` é o ensaio real de nascimento: gera
  uma cópia descartável com o app exemplo, preenche um `.env` apenas com
  segredos efêmeros, valida a configuração do Compose, sobe somente os
  serviços `db` e `web`, migra, cria um administrador de ensaio não
  interativo, executa a suíte Django de `core` e `apps.exemplo`, faz smoke
  HTTP das rotas de saúde e de login e remove exclusivamente os recursos que
  criou. Com `--keep`, ele retém a cópia aprovada e informa destino, projeto
  Compose e URL para inspeção posterior.

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
git tag -a v0.1.0 -m "descrição da release"

# listar as tags existentes
git tag

# inspecionar o conteúdo de uma tag
git show v0.1.0 --stat
```

Sem `--vcs-ref`, `copier copy` e `copier update` renderizam sempre a **última
tag** (ordenada pelo algoritmo PEP 440), nunca o HEAD — é por isso que
sistemas nascem de releases. Se o repositório não tem nenhuma tag, o Copier
cai no HEAD com uma versão sintética como `0.0.0.postN.dev0+hash` e, se a
árvore estiver suja, emite `DirtyLocalWarning` e inclui as mudanças não
commitadas na cópia — nunca gere um sistema real nesse estado. A opção
`--vcs-ref=HEAD` existe apenas para ensaio e depuração do template, nunca
para nascimento de produção.

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
