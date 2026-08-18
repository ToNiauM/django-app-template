# App Exemplo — Documentação Viva & Blueprint de Domínio

O app `apps/exemplo` é o modelo de referência arquitetural para os sistemas derivados do **Sistema Base (Template CFC)**. Ele serve como documentação executável demonstrando as convenções e padrões oficiais da stack da casa:

- **CRUD de Alta Produtividade:** ModelForm tipado, tabela paginada no servidor (`Paginator`), busca com debounce, filtros multi-seleção, ordenação protegida por whitelist e modais instantâneos via HTMX + Alpine.js com validação HTTP 422.
- **Dashboard Analítico:** Agregações puras no PostgreSQL via ORM do Django (`.aggregate()` e `.values().annotate()`), serialização segura contra XSS via `json_script` e gráficos interativos Apache ECharts 5.x locais com drill-down para o CRUD.
- **Auditoria Transparente:** Rastreamento automático de mudanças via `django-simple-history` (`HistoricalRecords`).
- **Isolamento Completo (EX-04):** O app não possui dependências reversas no núcleo (`core/`). Ele foi projetado para ser estudado, copiado para novos apps de negócio e descartado com facilidade.

---

## Pontos de Integração com o Sistema

O app exemplo se conecta ao sistema exclusivamente através de **3 pontos documentados**:

1. **Configuração de Apps:** `config/settings/base.py`
   ```python
   INSTALLED_APPS = [
       ...
       "apps.exemplo.apps.ExemploConfig",
   ]
   ```

2. **Roteamento de URLs:** `config/urls.py`
   ```python
   urlpatterns = [
       ...
       path("exemplo/", include("apps.exemplo.urls")),
   ]
   ```

3. **Menu Lateral do Shell:** `core/templates/core/_nav.html`
   ```html
   {% url 'exemplo:dashboard' as url_exemplo_dash %}
   {% url 'exemplo:item_listar' as url_exemplo_crud %}
   ...
   ```

---

## Como Remover este App de Exemplo (Checklist em 4 Passos)

Quando você gerar um novo sistema para um domínio real (ex.: Orçamento, Financeiro, Dívida Ativa) e já tiver modelado seus apps em `apps/`, siga este checklist para remover o `apps/exemplo` com segurança:

### Passo 1: Remover as referências de código nos 3 pontos de integração
1. Em `config/settings/base.py`, remova `"apps.exemplo.apps.ExemploConfig"` de `INSTALLED_APPS`.
2. Em `config/urls.py`, remova a linha `path("exemplo/", include("apps.exemplo.urls")),`.
3. Em `core/templates/core/_nav.html`, remova os blocos `<a>` do Dashboard e de Itens (CRUD).

### Passo 2: Apagar o diretório do app
```bash
rm -rf apps/exemplo/
```

### Passo 3: Limpar as tabelas no banco de dados
No ambiente de banco de dados (via `manage.py dbshell` ou cliente PostgreSQL):
```sql
DROP TABLE IF EXISTS exemplo_historicalitemexemplo CASCADE;
DROP TABLE IF EXISTS exemplo_itemexemplo CASCADE;
DELETE FROM django_migrations WHERE app = 'exemplo';
```

### Passo 4: Validar a integridade do sistema
Execute os testes globais e a verificação do Django para garantir que o sistema permanece 100% íntegro:
```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py test
```
