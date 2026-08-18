# Fase 4: Templatização Copier — Mapa de Padrões

**Mapeado em:** 2026-08-18  
**Arquivos classificados:** 22  
**Análogos encontrados:** 18 / 22

## Classificação de arquivos

| Arquivo novo/modificado | Papel | Fluxo de dados | Análogo mais próximo | Qualidade |
|---|---|---|---|---|
| `copier.yml` | configuração de template | transformação | nenhum no repositório | nenhum |
| `.copier-answers.yml.jinja` | metadados/configuração | transformação | nenhum no repositório | nenhum |
| `.env.example.jinja` | configuração | transformação | `.env.example` | exato |
| `tailwind.config.js.jinja` | configuração de build | transformação | `tailwind.config.js` | exato |
| `compose.yml.jinja` | configuração de orquestração | request-response | `compose.yml`, `/opt/web/pca/compose.yml` | exato |
| `config/settings/base.py.jinja` | configuração Django | request-response | `config/settings/base.py` | exato |
| `config/urls.py.jinja` | rota | request-response | `config/urls.py` | exato |
| `core/templates/core/_nav.html.jinja` | componente/template | request-response | `core/templates/core/_nav.html` | exato |
| `apps/{% if incluir_app_exemplo %}exemplo{% endif %}/` | pacote condicional | CRUD/request-response | `apps/exemplo/` | exato |
| `apps/exemplo/templates/exemplo/dashboard.html` | componente/template | request-response | próprio arquivo | exato |
| `apps/exemplo/README.md` | documentação | estático | próprio arquivo | exato |
| `ops/gerar_icones_pwa.py` | utilitário | file-I/O | próprio arquivo | exato |
| `README.md` | documentação do template | estático | `apps/exemplo/README.md` | parcial |
| `README.md.jinja` | documentação gerada | transformação | `apps/exemplo/README.md` | parcial |
| `ops/backup/Dockerfile` | configuração de container | batch | `/opt/web/pca/ops/backup/Dockerfile` | exato (referência externa) |
| `ops/backup/backup.sh` | serviço/script | batch | `/opt/web/pca/ops/backup/backup.sh` | exato (referência externa) |
| `ops/backup/retencao.sh` | utilitário | batch | `/opt/web/pca/ops/backup/retencao.sh` | exato (referência externa) |
| `ops/backup/testar_retencao.sh` | teste operacional | batch | `/opt/web/pca/ops/backup/testar_retencao.sh` | exato (referência externa) |
| `ops/backup/ensaio_restore_local.sh` | teste operacional | batch | `/opt/web/pca/ops/backup/ensaio_restore_local.sh` | papel equivalente (generalizar) |
| `ops/nginx/{{ sistema_slug }}.conf.jinja` | configuração de proxy | request-response | `/opt/web/pca/ops/nginx/pca.conf` | exato (referência externa) |
| `ops/MIGRACAO.md.jinja` | runbook | estático | `/opt/web/pca/ops/MIGRACAO.md` | papel equivalente (generalizar) |
| `entrypoint.sh` e `apps/exemplo/management/commands/seed_exemplo.py` | scripts existentes a neutralizar | batch | próprios arquivos | exato |

## Atribuições de padrões

### Configuração Copier e arquivos renderizados

#### `copier.yml` e `.copier-answers.yml.jinja` (configuração, transformação)

**Análogo:** não há uso prévio de Copier no repositório. Aplicar diretamente o contrato de `04-RESEARCH.md` (linhas 137–143), sem `_tasks` e com `StrictUndefined`.

**Convenção a preservar:** o template é *in-place*; só arquivos que contêm expressão ou bloco Jinja recebem `.jinja`. `_exclude` precisa repetir exclusões padrão porque uma lista própria as substitui: `copier.yml`, `.git`, `.planning`, `README.md`, `.env`, caches, `staticfiles`, `core/static/dist`, `.venv`, artefatos de editor e documentos de desenvolvimento.

**Respostas:** use `.copier-answers.yml.jinja` para renderizar `_copier_answers`; não criar script que escreva YAML nem editar respostas manualmente. Perguntas são `sistema_nome`, `sistema_slug`, `sistema_hostname`, `sistema_porta`, `sistema_banco`, `sistema_sigla`, `cor_primaria` e `incluir_app_exemplo`, com validators antes da renderização.

#### `.env.example.jinja` (configuração, transformação)

**Análogo:** `.env.example` (linhas 30–65).

```dotenv
# O bind externo continua limitado a loopback; só WEB_PORT é uma resposta Copier.
WEB_BIND_ADDRESS=127.0.0.1
WEB_PORT=8000

# Identidade e banco já estão centralizados no ambiente.
SISTEMA_NOME=Sistema Base
SISTEMA_SIGLA=SB
COR_PRIMARIA=#1e40af
POSTGRES_DB=sistema_base
POSTGRES_USER=sistema_base
DATABASE_URL=postgres://sistema_base:replace-with-a-database-password@db:5432/sistema_base
```

Renderizar nome, sigla, cor, slug/banco, porta e hostname neste arquivo; manter `SECRET_KEY`, senha PostgreSQL e credenciais R2 como placeholders. Acrescentar knobs de backup com defaults PCA (agenda, 7 diários, 4 semanais, domingo), todos vindos do `.env`.

#### `tailwind.config.js.jinja` (configuração de build, transformação)

**Análogo:** `tailwind.config.js` (linhas 3–19 e 37–41).

```javascript
// ÚNICO valor de identidade deste arquivo.
const COR_PRIMARIA = "#1e40af";

brand: COR_PRIMARIA,
"brand-hover": misturar(COR_PRIMARIA, 255, 0.12),
"brand-ink": misturar(COR_PRIMARIA, 0, 0.18),
"brand-tint": misturar(COR_PRIMARIA, 255, 0.9),
```

Trocar exclusivamente a constante pelo valor Jinja. Não templatear as cores semânticas nem a função `misturar`, para manter uma superfície mínima de conflito em `copier update`.

#### `compose.yml.jinja` (orquestração, request-response)

**Análogos:** `compose.yml` (linhas 19–51) e `/opt/web/pca/compose.yml` (linhas 56–85).

```yaml
ports:
  - "${WEB_BIND_ADDRESS:-127.0.0.1}:${WEB_PORT:-8000}:8000"
healthcheck:
  test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8000/healthz"]

backup:
  build:
    context: ./ops/backup
  restart: unless-stopped
  init: true
  depends_on:
    db:
      condition: service_healthy
  environment:
    RCLONE_CONFIG_R2_TYPE: s3
    RCLONE_CONFIG_R2_PROVIDER: Cloudflare
    RCLONE_CONFIG_R2_NO_CHECK_BUCKET: "true"
    DB_HOST: db
    DB_USER: ${POSTGRES_USER}
    DB_NAME: ${POSTGRES_DB}
    PGPASSWORD: ${POSTGRES_PASSWORD}
```

Adicionar `name: {{ sistema_slug }}` no topo. Preservar a publicação segura em `127.0.0.1`, healthchecks e volume **gerenciado** `pgdata:` (não copiar o volume `external: true` da PCA). Passar R2 e knobs de backup somente pelo ambiente.

### Opcionalidade do app exemplo e identidade em runtime

#### `config/settings/base.py.jinja` (configuração Django, request-response)

**Análogo:** `config/settings/base.py` (linhas 18–21, 23–38, 145–161).

```python
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")
SECRET_KEY = env("SECRET_KEY")

INSTALLED_APPS = [
    # ... núcleo ...
    "axes",
    "apps.exemplo.apps.ExemploConfig",
]

SISTEMA_NOME = env("SISTEMA_NOME", default="Sistema Base")
SISTEMA_SIGLA = env("SISTEMA_SIGLA", default="SB")
COR_PRIMARIA = env("COR_PRIMARIA", default="#1e40af")
if not re.fullmatch(r"#[0-9a-fA-F]{6}", COR_PRIMARIA):
    raise ImproperlyConfigured(...)
```

Manter `read_env`, a validação de cor e a mensagem em pt-BR; retirar os três defaults de identidade, tornando os envs obrigatórios. Envolver somente a linha do `ExemploConfig` em `{% if incluir_app_exemplo %}`; não tocar ordem de `MIDDLEWARE` nem controles de segurança.

#### `config/urls.py.jinja` e `core/templates/core/_nav.html.jinja` (rota/componente, request-response)

**Análogos:** `config/urls.py` (linhas 7–15) e `_nav.html` (linhas 22–58).

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("exemplo/", include("apps.exemplo.urls")),
    path("", include("core.urls")),
]
```

```django
{% url 'exemplo:dashboard' as url_exemplo_dash %}
{% url 'exemplo:item_listar' as url_exemplo_crud %}
<!-- blocos <a> Dashboard e Itens (CRUD) -->
```

Envolver o `include`, ambas as resoluções de URL e os dois links completos em blocos Jinja Copier condicionais. Não remover o link de início nem alterar o contrato de item de navegação descrito no topo do partial. O diretório `apps/exemplo/` deve ser condicional e não deve usar `_skip_if_exists`, para que um update posterior não o recrie.

#### `apps/exemplo/templates/exemplo/dashboard.html` e `ops/gerar_icones_pwa.py` (component/utilitário, request-response/file-I/O)

**Análogos:** próprios arquivos, dashboard linhas 102–107; gerador linhas 27–29 e 60–72.

```django
const corBrand = "{{ cor_primaria|default:'#1e40af' }}";
```

```python
RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "core" / "static" / "img"

cor = sys.argv[1] if len(sys.argv) > 1 else "#1e40af"
sigla = sys.argv[2] if len(sys.argv) > 2 else "SB"
```

Remover o fallback de cor no dashboard (o context processor entrega valor obrigatório) e mudar o gerador para carregar `COR_PRIMARIA`/`SISTEMA_SIGLA` do `.env`, preservando argumentos explícitos se forem úteis. Não introduzir defaults de identidade no código; o `.env.example.jinja` é a única origem de defaults.

#### `entrypoint.sh`, `seed_exemplo.py` e `apps/exemplo/README.md` (scripts/documentação)

**Análogos:** próprios arquivos. `entrypoint.sh` (linhas 1–5) mantém o Gunicorn interno em `0.0.0.0:8000`; `WEB_PORT` regula apenas a publicação Compose e o `proxy_pass`, evitando duas portas configuráveis. `seed_exemplo.py` não tem literal de marca atual; só deve ser revisado para não introduzir `sistema_base`/nome antigo. O README do app (linhas 12–66) é a fonte do protocolo dos três acoplamentos, mas deve ser reconciliado para orientar `copier update --data incluir_app_exemplo=false`, em vez de recomendar remoção manual como caminho primário.

### Operação

#### `ops/backup/{Dockerfile,backup.sh,retencao.sh,testar_retencao.sh}` (container, batch)

**Análogos externos de leitura:** `/opt/web/pca/ops/backup/Dockerfile` (linhas 1–48), `backup.sh` (1–28), `retencao.sh` (1–27), `testar_retencao.sh` (1–59).

```dockerfile
FROM postgres:17-alpine
RUN apk add --no-cache curl unzip dcron tzdata
ARG PIN_RCLONE_VERSION=v1.68.2
# download fixado + SHA256SUMS, depois COPY dos scripts
ENV TZ=America/Sao_Paulo
CMD ["crond", "-f", "-d", "8"]
```

```sh
set -eu
. "$(dirname "$0")/retencao.sh"
DATA=$(date +%Y-%m-%d_%H%M%S)
pg_dump --format=custom --host="${DB_HOST}" --username="${DB_USER}" "${DB_NAME}" > "${ARQUIVO}"
rclone copy "${ARQUIVO}" "r2:${R2_BUCKET}/daily/"
manter_ultimos "daily" 7
manter_ultimos "weekly" 4
```

```sh
manter_ultimos() {
  destino="$1"; manter="$2"
  listagem=$(rclone lsf "r2:${R2_BUCKET}/${destino}/" --format tp --separator ";" 2>/dev/null | sort -r)
  # apaga apenas a partir do índice manter + 1
}
```

Manter imagem PostgreSQL alinhada ao banco, download rclone pinado com checksum, `set -eu`, dump customizado, cópia diária/semanal e retenção compartilhada. Generalizar prefixos para o slug e mover agenda/limites/dia para `.env`; criar entrypoint que valida valores numéricos e horário antes de gerar o crontab. O teste de retenção deve usar prefixo descartável, bloquear argumentos `daily|weekly` e limpar por `trap`.

#### `ops/backup/ensaio_restore_local.sh` (teste operacional, batch)

**Análogo externo:** `/opt/web/pca/ops/backup/ensaio_restore_local.sh` (linhas 20–115).

```sh
set -eu
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
REDE="pca_rehearsal_net"
VOLUME_PGDATA="pca_rehearsal_pgdata"
DB_CONTAINER="pca_rehearsal_db"

docker run -d --name "${DB_CONTAINER}" --network "${REDE}" ... postgres:17
docker compose exec -T backup sh -c 'rclone lsf "r2:${R2_BUCKET}/daily/" --format tp --separator ";"' | ...
docker exec -i "${DB_CONTAINER}" pg_restore --clean --if-exists --no-owner ...
```

Preservar `set -eu`, recursos efêmeros nomeados por slug, `trap` de limpeza e a cadeia: descobrir dump → restaurar custom dump em DB isolado → `migrate --plan` → `migrate --noinput` → `manage.py check`. Não copiar consultas, imagens, contagens, nome de volume ou prefixos PCA; limpar estritamente recursos criados pelo ensaio.

#### `ops/nginx/{{ sistema_slug }}.conf.jinja` e `ops/MIGRACAO.md.jinja` (proxy/runbook)

**Análogos externos:** `/opt/web/pca/ops/nginx/pca.conf` (linhas 18–50) e `/opt/web/pca/ops/MIGRACAO.md` (linhas 298–333).

```nginx
server {
    server_name <dominio>;
    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/<dominio>/fullchain.pem;
}
```

Interpolar hostname e porta no nome do arquivo, `server_name`, certificados e `proxy_pass`; preservar cabeçalhos definidos pelo Nginx e redirect HTTP→HTTPS. O runbook deve orientar Docker/Compose, Nginx, Certbot e rclone; `.env`, restore com `pg_restore --clean --if-exists --no-owner`, `/healthz`, `nginx -t`, TLS e DNS. Retirar qualquer projeto, modelo, bucket, volume, incidente ou domínio específico da PCA.

## Padrões compartilhados

### `.env` primeiro

**Fontes:** `.env.example` (42–65), `config/settings/base.py` (18–21, 145–161), `compose.yml` (27–34).  
**Aplicar a:** identidade, banco, backup e runtime.

Código Django e scripts não ganham valores de marca ou nomes de sistema; somente `.env.example.jinja` e `copier.yml` fornecem defaults. O bind público continua com fallback seguro de loopback.

### Comentários operacionais em pt-BR e falha explícita

**Fontes:** `compose.yml` (30–43), `config/settings/base.py` (153–161), scripts PCA.  
**Aplicar a:** configuração Copier, backup, nginx e runbooks.

Manter comentários que expliquem invariantes de segurança/portabilidade. Scripts usam `set -eu`; validações falham antes de executar operação perigosa. Não transportar comentários PCA que revelem incidentes ou detalhes de outro sistema.

### Isolamento e segurança de infraestrutura

**Fontes:** `compose.yml` (29–51), `/opt/web/pca/compose.yml` (56–85), `/opt/web/pca/ops/nginx/pca.conf` (21–50).  
**Aplicar a:** Compose, backup, nginx, restore.

`name: slug` isola stack/volume/rede; `web` só publica em `127.0.0.1`; backup conecta a `db` internamente, espera healthcheck e usa `init: true`; TLS termina no Nginx, que define headers confiáveis.

## Sem análogo local

| Arquivo | Motivo | Direção ao planejador |
|---|---|---|
| `copier.yml` | primeiro template Copier do repositório | seguir `04-RESEARCH.md` e documentação oficial, com checkpoint humano antes de instalar Copier |
| `.copier-answers.yml.jinja` | primeiro arquivo de respostas | renderizar `_copier_answers`; nunca criar escritor manual |
| `README.md` / `README.md.jinja` | não há README raiz de sistema/template | usar a estrutura procedural do README de `apps/exemplo`, mas cobrir nascimento, tags/update, resolução de conflito, backup/restore, proxy/DNS e ícones |
| `ops/backup/ensaio_restore_local.sh` | PCA é específico do domínio | reter somente a orquestração isolada e remover qualquer verificação de dados de negócio |

## Metadados

**Escopo de busca:** raiz do template, `config/`, `core/`, `apps/exemplo/`, `ops/` e referências somente-leitura em `/opt/web/pca/ops/` e `/opt/web/pca/compose.yml`.  
**Arquivos de código/referência lidos:** 18.  
**Data de extração:** 2026-08-18.
