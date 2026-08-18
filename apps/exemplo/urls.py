"""Rotas do app exemplo."""

from django.urls import path

from . import views

app_name = "exemplo"

urlpatterns = [
    path("", views.item_listar_view, name="item_listar"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("novo/", views.item_criar_view, name="item_criar"),
    path("<int:pk>/editar/", views.item_editar_view, name="item_editar"),
    path("<int:pk>/excluir/", views.item_excluir_view, name="item_excluir"),
]
