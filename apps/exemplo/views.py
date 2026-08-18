"""Views do app exemplo demonstrando CRUD com paginação server-side, filtros HTMX e modais."""

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import ItemExemploForm
from .models import CategoriaChoices, ItemExemplo, StatusChoices

COLUNAS_ORDENACAO_PERMITIDAS = {
    "titulo": "titulo",
    "-titulo": "-titulo",
    "categoria": "categoria",
    "-categoria": "-categoria",
    "status": "status",
    "-status": "-status",
    "valor": "valor",
    "-valor": "-valor",
    "prazo": "prazo",
    "-prazo": "-prazo",
    "criado_em": "criado_em",
    "-criado_em": "-criado_em",
}


def extrair_querystring_filtros(params, excluir=("pagina",)):
    """Preserva os filtros na querystring excluindo parâmetros transitórios como a página atual."""
    qdict = params.copy()
    for chave in excluir:
        qdict.pop(chave, None)
    return qdict.urlencode()


@login_required
def item_listar_view(request):
    """Listagem paginada server-side com busca textual, filtros multi-seleção e ordenação."""
    qs = ItemExemplo.objects.all()

    # 1. Filtro de busca textual
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q))

    # 2. Filtro multi-seleção de categoria
    categorias = request.GET.getlist("categoria")
    if categorias:
        qs = qs.filter(categoria__in=categorias)

    # 3. Filtro multi-seleção de status
    status_list = request.GET.getlist("status")
    if status_list:
        qs = qs.filter(status__in=status_list)

    # 4. Ordenação segura com whitelist
    ordem_param = request.GET.get("ordem", "-criado_em")
    ordem_segura = COLUNAS_ORDENACAO_PERMITIDAS.get(ordem_param, "-criado_em")
    qs = qs.order_by(ordem_segura)

    # 5. Paginação server-side
    paginador = Paginator(qs, 10)
    pagina_num = request.GET.get("pagina", 1)
    pagina = paginador.get_page(pagina_num)

    contexto = {
        "pagina": pagina,
        "q": q,
        "categorias_selecionadas": categorias,
        "status_selecionados": status_list,
        "ordem_atual": ordem_param,
        "opcoes_categoria": CategoriaChoices.choices,
        "opcoes_status": StatusChoices.choices,
        "querystring_filtros": extrair_querystring_filtros(request.GET),
        "trilha": [
            {"rotulo": "Início", "url": reverse("core:shell")},
            {"rotulo": "Exemplo", "url": None},
            {"rotulo": "Itens", "url": None},
        ],
    }

    if getattr(request, "htmx", False):
        return render(request, "exemplo/_tabela_resultado.html", contexto)
    return render(request, "exemplo/item_listar.html", contexto)


@login_required
def item_criar_view(request):
    """Modal de criação de item via HTMX/Alpine com retorno de erro 422 ou trigger de sucesso."""
    if request.method == "POST":
        form = ItemExemploForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.criado_por = request.user
            item.save()
            resposta = HttpResponse(
                '<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'
            )
            resposta["HX-Trigger"] = "itemSalvo"
            return resposta

        return render(
            request,
            "exemplo/_form_modal.html",
            {"form": form, "modo": "criar"},
            status=422,
        )

    form = ItemExemploForm()
    return render(request, "exemplo/_form_modal.html", {"form": form, "modo": "criar"})


@login_required
def item_editar_view(request, pk):
    """Modal de edição de item via HTMX/Alpine."""
    item = get_object_or_404(ItemExemplo, pk=pk)

    if request.method == "POST":
        form = ItemExemploForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            resposta = HttpResponse(
                '<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'
            )
            resposta["HX-Trigger"] = "itemSalvo"
            return resposta

        return render(
            request,
            "exemplo/_form_modal.html",
            {"form": form, "item": item, "modo": "editar"},
            status=422,
        )

    form = ItemExemploForm(instance=item)
    return render(
        request,
        "exemplo/_form_modal.html",
        {"form": form, "item": item, "modo": "editar"},
    )


@login_required
def item_excluir_view(request, pk):
    """Modal de confirmação e processamento de exclusão de item via HTMX."""
    item = get_object_or_404(ItemExemplo, pk=pk)

    if request.method == "POST":
        item.delete()
        resposta = HttpResponse(
            '<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'
        )
        resposta["HX-Trigger"] = "itemSalvo"
        return resposta

    return render(
        request,
        "exemplo/_confirmar_exclusao_modal.html",
        {"item": item},
    )
