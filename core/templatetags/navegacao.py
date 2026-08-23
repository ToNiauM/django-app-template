"""Ponto de extensão da navegação principal (NAV-01/NAV-02/NAV-03).

`{% item_nav rota rotulo icone prefixo %}` monta uma linha do menu com o
tratamento visual do padrão de referência por construção. `rota` é o NOME da
rota (`app:nome`), nunca a URL. Se `reverse(rota)` falhar — porque o app foi
removido pelo `copier update` — o item some em silêncio (sem
`NoReverseMatch`, T-07-08): é o mesmo contrato documentado do
`{% url 'x' as var %}` do Django, aplicado do lado Python (D-89, critério 6).

`icone` é o NOME de um ícone do dicionário fechado `ICONES` abaixo — a tag
NUNCA aceita markup SVG como argumento (T-07-06). Um nome desconhecido
renderiza o item sem ícone, nunca quebra a página (D-90).

`item_nav` NÃO é mecanismo de autorização: ela não checa permissão nenhuma.
Esconder um item de menu não protege a rota correspondente — a proteção
continua sendo o `LoginRequiredMiddleware` e a permissão da própria view
(T-07-07).
"""

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

register = template.Library()

# Ícones por nome — o markup interno do <svg> 24x24, stroke="currentColor".
# Dicionário FECHADO: só os nomes aqui existem; qualquer outro nome devolve
# ícone vazio (D-90), nunca levanta erro.
ICONES = {
    "casa": mark_safe(
        '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>'
    ),
    "grafico": mark_safe(
        '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>'
    ),
    "lista": mark_safe(
        '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="m9 12 2 2 4-4"/>'
    ),
}


@register.inclusion_tag("core/_item_nav.html", takes_context=True)
def item_nav(context, rota, rotulo, icone="", prefixo=""):
    """Um item da navegação principal, com o estado ativo por construção.

    `prefixo` marca o item ativo também nas rotas-filhas (ex.: "/exemplo/"),
    além da correspondência exata de `request.path` com a URL revertida.
    """
    try:
        url = reverse(rota)
    except NoReverseMatch:
        return {"url": ""}

    caminho = context["request"].path
    ativo = caminho == url or bool(prefixo and caminho.startswith(prefixo))

    return {
        "url": url,
        "rotulo": rotulo,
        "icone": ICONES.get(icone, ""),
        "ativo": ativo,
    }
