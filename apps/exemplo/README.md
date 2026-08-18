# App Exemplo — Documentação Viva e Blueprint de Domínio

O app `apps/exemplo` é um modelo de referência arquitetural para sistemas
derivados. Ele demonstra convenções reutilizáveis da stack Django:

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

## Remover o App Exemplo

Para um sistema derivado que não precise desta documentação viva, atualize o
template com `copier update --data incluir_app_exemplo=false`. O fluxo remove o
diretório e os três pontos de integração acima sem exigir edição manual.

Depois da atualização, valide a integridade do sistema:
```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py test
```
