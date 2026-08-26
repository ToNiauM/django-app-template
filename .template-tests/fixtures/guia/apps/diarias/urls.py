"""Rotas do app de diárias e passagens."""

from django.urls import path

from . import views

app_name = "diarias"

urlpatterns = [
    path("", views.viagem_listar_view, name="viagem_listar"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("novo/", views.viagem_criar_view, name="viagem_criar"),
    path("<int:pk>/editar/", views.viagem_editar_view, name="viagem_editar"),
    path("<int:pk>/excluir/", views.viagem_excluir_view, name="viagem_excluir"),
]
