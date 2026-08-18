"""Views do app exemplo demonstrando CRUD com paginação server-side, filtros HTMX e modais."""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
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


@login_required
def dashboard_view(request):
    """Dashboard analítico com agregações 100% no PostgreSQL via ORM e gráficos ECharts."""
    qs = ItemExemplo.objects.filter(ativo=True)

    # 1. KPIs executivos via .aggregate() no banco
    kpis = qs.aggregate(
        total_itens=Count("id"),
        valor_total=Sum("valor"),
        valor_medio=Avg("valor"),
        concluidos=Count("id", filter=Q(status=StatusChoices.CONCLUIDO)),
        em_andamento=Count("id", filter=Q(status=StatusChoices.EM_ANDAMENTO)),
        rascunho=Count("id", filter=Q(status=StatusChoices.RASCUNHO)),
        cancelados=Count("id", filter=Q(status=StatusChoices.CANCELADO)),
    )

    total_itens = kpis["total_itens"] or 0
    valor_total = kpis["valor_total"] or Decimal("0.00")
    valor_medio = kpis["valor_medio"] or Decimal("0.00")
    concluidos = kpis["concluidos"] or 0

    taxa_conclusao = (
        (Decimal(concluidos) / Decimal(total_itens) * Decimal("100"))
        if total_itens > 0
        else Decimal("0.0")
    )

    # 2. Agrupamento por Categoria (Barras)
    dados_categoria = list(
        qs.values("categoria")
        .annotate(total_valor=Sum("valor"), qtd=Count("id"))
        .order_by("-total_valor")
    )

    # 3. Agrupamento por Status (Donut)
    dados_status = list(
        qs.values("status")
        .annotate(qtd=Count("id"), total_valor=Sum("valor"))
        .order_by("status")
    )

    contexto = {
        "kpis": {
            "total_itens": total_itens,
            "valor_total": valor_total,
            "valor_medio": valor_medio,
            "concluidos": concluidos,
            "taxa_conclusao": taxa_conclusao,
        },
        "dados_categoria": [
            {
                "categoria": dict(CategoriaChoices.choices).get(item["categoria"], item["categoria"]),
                "categoria_raw": item["categoria"],
                "total_valor": float(item["total_valor"] or 0),
                "qtd": item["qtd"],
            }
            for item in dados_categoria
        ],
        "dados_status": [
            {
                "status": item["status"],
                "rotulo": dict(StatusChoices.choices).get(item["status"], item["status"]),
                "qtd": item["qtd"],
                "total_valor": float(item["total_valor"] or 0),
            }
            for item in dados_status
        ],
        "trilha": [
            {"rotulo": "Início", "url": reverse("core:shell")},
            {"rotulo": "Exemplo", "url": None},
            {"rotulo": "Dashboard", "url": None},
        ],
    }
    return render(request, "exemplo/dashboard.html", contexto)

