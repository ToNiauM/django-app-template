"""Views do app de diárias demonstrando CRUD com paginação server-side, filtros HTMX e modais."""

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from core.tema import familia_marca

from .forms import ViagemForm
from .models import StatusChoices, Viagem

COLUNAS_ORDENACAO_PERMITIDAS = {
    "servidor": "servidor",
    "-servidor": "-servidor",
    "destino": "destino",
    "-destino": "-destino",
    "data_inicio": "data_inicio",
    "-data_inicio": "-data_inicio",
    "valor_diarias": "valor_diarias",
    "-valor_diarias": "-valor_diarias",
    "valor_passagens": "valor_passagens",
    "-valor_passagens": "-valor_passagens",
    "status": "status",
    "-status": "-status",
    "criado_em": "criado_em",
    "-criado_em": "-criado_em",
}


# ordem é reanexada explicitamente pelos templates e nunca deve viajar dentro da querystring de filtros.
def extrair_querystring_filtros(params, excluir=("pagina", "ordem")):
    """Preserva os filtros na querystring excluindo parâmetros transitórios como a página atual."""
    qdict = params.copy()
    for chave in excluir:
        qdict.pop(chave, None)
    return qdict.urlencode()


@login_required
def viagem_listar_view(request):
    """Listagem paginada server-side com busca textual, filtro de status e ordenação."""
    qs = Viagem.objects.all()

    # 1. Filtro de busca textual
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(servidor__icontains=q) | Q(destino__icontains=q) | Q(motivo__icontains=q)
        )

    # 2. Filtro multi-seleção de status — só valores conhecidos entram na query
    status_list = [s for s in request.GET.getlist("status") if s in StatusChoices.values]
    if status_list:
        qs = qs.filter(status__in=status_list)

    # 3. Ordenação segura com whitelist — nunca order_by de entrada crua
    ordem_param = request.GET.get("ordem", "-criado_em")
    ordem_segura = COLUNAS_ORDENACAO_PERMITIDAS.get(ordem_param, "-criado_em")
    qs = qs.order_by(ordem_segura)

    # 4. Paginação server-side
    paginador = Paginator(qs, 10)
    pagina_num = request.GET.get("pagina", 1)
    pagina = paginador.get_page(pagina_num)

    contexto = {
        "pagina": pagina,
        "q": q,
        "status_selecionados": status_list,
        "ordem_atual": ordem_param,
        "opcoes_status": StatusChoices.choices,
        "querystring_filtros": extrair_querystring_filtros(request.GET),
        "trilha": [
            {"rotulo": "Início", "url": reverse("core:shell")},
            {"rotulo": "Diárias e Passagens", "url": None},
            {"rotulo": "Viagens", "url": None},
        ],
    }

    if getattr(request, "htmx", False):
        return render(request, "diarias/_tabela_resultado.html", contexto)
    return render(request, "diarias/viagem_listar.html", contexto)


@login_required
def viagem_criar_view(request):
    """Modal de criação de viagem via HTMX/Alpine com retorno de erro 422 ou trigger de sucesso."""
    if request.method == "POST":
        form = ViagemForm(request.POST)
        if form.is_valid():
            form.save()
            resposta = HttpResponse(
                '<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'
            )
            resposta["HX-Trigger"] = "viagemSalva"
            return resposta

        return render(
            request,
            "diarias/_form_modal.html",
            {"form": form, "modo": "criar"},
            status=422,
        )

    form = ViagemForm()
    return render(request, "diarias/_form_modal.html", {"form": form, "modo": "criar"})


@login_required
def viagem_editar_view(request, pk):
    """Modal de edição de viagem via HTMX/Alpine."""
    viagem = get_object_or_404(Viagem, pk=pk)

    if request.method == "POST":
        form = ViagemForm(request.POST, instance=viagem)
        if form.is_valid():
            form.save()
            resposta = HttpResponse(
                '<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'
            )
            resposta["HX-Trigger"] = "viagemSalva"
            return resposta

        return render(
            request,
            "diarias/_form_modal.html",
            {"form": form, "viagem": viagem, "modo": "editar"},
            status=422,
        )

    form = ViagemForm(instance=viagem)
    return render(
        request,
        "diarias/_form_modal.html",
        {"form": form, "viagem": viagem, "modo": "editar"},
    )


@login_required
def viagem_excluir_view(request, pk):
    """Modal de confirmação e processamento de exclusão de viagem via HTMX."""
    viagem = get_object_or_404(Viagem, pk=pk)

    if request.method == "POST":
        viagem.delete()
        resposta = HttpResponse(
            '<div id="modal-container" x-data x-init="$el.innerHTML = \'\'"></div>'
        )
        resposta["HX-Trigger"] = "viagemSalva"
        return resposta

    return render(
        request,
        "diarias/_confirmar_exclusao_modal.html",
        {"viagem": viagem},
    )


@login_required
def dashboard_view(request):
    """Dashboard analítico com agregações 100% no PostgreSQL via ORM e gráficos ECharts."""
    qs = Viagem.objects.all()

    # 1. KPIs executivos via .aggregate() no banco
    kpis = qs.aggregate(
        total_viagens=Count("id"),
        total_diarias=Sum("valor_diarias"),
        total_passagens=Sum("valor_passagens"),
        pagas=Count("id", filter=Q(status=StatusChoices.PAGA)),
        aprovadas=Count("id", filter=Q(status=StatusChoices.APROVADA)),
        solicitadas=Count("id", filter=Q(status=StatusChoices.SOLICITADA)),
        canceladas=Count("id", filter=Q(status=StatusChoices.CANCELADA)),
    )

    total_viagens = kpis["total_viagens"] or 0
    total_diarias = kpis["total_diarias"] or Decimal("0.00")
    total_passagens = kpis["total_passagens"] or Decimal("0.00")
    valor_total = total_diarias + total_passagens
    pagas = kpis["pagas"] or 0

    taxa_pagamento = (
        (Decimal(pagas) / Decimal(total_viagens) * Decimal("100"))
        if total_viagens > 0
        else Decimal("0.0")
    )

    # 2. Agrupamento por Status (Donut) — contagem e soma de diárias + passagens
    dados_status = list(
        qs.values("status")
        .annotate(
            qtd=Count("id"),
            total_valor=Sum(F("valor_diarias") + F("valor_passagens")),
        )
        .order_by("status")
    )

    # 3. Série mensal (Barras) — soma dos valores por mês de início da viagem
    dados_mensais = list(
        qs.annotate(mes=TruncMonth("data_inicio"))
        .values("mes")
        .annotate(
            total_diarias=Sum("valor_diarias"),
            total_passagens=Sum("valor_passagens"),
            qtd=Count("id"),
        )
        .order_by("mes")
    )

    # 4. Paleta semântica do donut — DADO, não estilo. O chrome do gráfico
    # (eixo, grade, tooltip) é lido das variáveis CSS no cliente; só a
    # paleta categórica do donut precisa vir do servidor, porque um
    # template não consegue escolher matizes que sobrevivam a qualquer
    # COR_PRIMARIA e continuem legíveis para daltônicos. A rampa é
    # SEQUENCIAL (monocromática), derivada de settings.COR_PRIMARIA pela
    # mesma familia_marca() que alimenta o <style> de base.html — as duas
    # nunca divergem porque são a mesma função. Quatro cores porque
    # StatusChoices tem quatro valores (models.py), e as QUATRO são degraus
    # de DADO da rampa `seq-*`: nenhum token de superfície entra aqui.
    #
    # A ordem é do mais destacado ao menos destacado CONTRA O FUNDO DO CARD,
    # em ambos os temas — seq-750, seq-600, seq-450, seq-300 (a mesma régua
    # medida no dashboard do app exemplo).
    familia_clara = familia_marca(settings.COR_PRIMARIA)
    paleta_graficos = {
        "rampa_status": {
            "claro": [
                familia_clara["seq-750"],
                familia_clara["seq-600"],
                familia_clara["seq-450"],
                familia_clara["seq-300"],
            ],
            "escuro": [
                familia_clara["seq-750:escuro"],
                familia_clara["seq-600:escuro"],
                familia_clara["seq-450:escuro"],
                familia_clara["seq-300:escuro"],
            ],
        }
    }

    contexto = {
        "kpis": {
            "total_viagens": total_viagens,
            "total_diarias": total_diarias,
            "total_passagens": total_passagens,
            "valor_total": valor_total,
            "pagas": pagas,
            "taxa_pagamento": taxa_pagamento,
        },
        "dados_status": [
            {
                "status": item["status"],
                "rotulo": dict(StatusChoices.choices).get(item["status"], item["status"]),
                "qtd": item["qtd"],
                "total_valor": float(item["total_valor"] or 0),
            }
            for item in dados_status
        ],
        "dados_mensais": [
            {
                "mes": item["mes"].isoformat() if item["mes"] else None,
                "total_diarias": float(item["total_diarias"] or 0),
                "total_passagens": float(item["total_passagens"] or 0),
                "qtd": item["qtd"],
            }
            for item in dados_mensais
        ],
        "paleta_graficos": paleta_graficos,
        "trilha": [
            {"rotulo": "Início", "url": reverse("core:shell")},
            {"rotulo": "Diárias e Passagens", "url": None},
            {"rotulo": "Dashboard", "url": None},
        ],
    }
    return render(request, "diarias/dashboard.html", contexto)
