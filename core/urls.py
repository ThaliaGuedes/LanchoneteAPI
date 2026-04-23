from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CardapioUnidadeView,
    EstoqueListView,
    EstoqueMovimentacaoCreateView,
    FidelidadeHistoricoView,
    FidelidadeResgateView,
    FidelidadeSaldoView,
    PagamentoPedidoView,
    PedidoCancelamentoView,
    PedidoDetalheView,
    PedidoListCreateView,
    PedidoStatusUpdateView,
    ProdutoListCreateView,
    PromocaoListView,
    RegistroUsuarioView,
    PerfilUsuarioView,
    UnidadeListView,
)

urlpatterns = [
    path("auth/register/", RegistroUsuarioView.as_view()),
    path("auth/token/", TokenObtainPairView.as_view()),
    path("auth/token/refresh/", TokenRefreshView.as_view()),
    path("usuarios/me/", PerfilUsuarioView.as_view()),
    path("unidades/", UnidadeListView.as_view()),
    path("unidades/<int:unidade_id>/cardapio/", CardapioUnidadeView.as_view()),
    path("produtos/", ProdutoListCreateView.as_view()),
    path("estoques/", EstoqueListView.as_view()),
    path("estoques/movimentacoes/", EstoqueMovimentacaoCreateView.as_view()),
    path("pedidos/", PedidoListCreateView.as_view()),
    path("pedidos/<int:pk>/", PedidoDetalheView.as_view()),
    path("pedidos/<int:pk>/status/", PedidoStatusUpdateView.as_view()),
    path("pedidos/<int:pk>/cancelamento/", PedidoCancelamentoView.as_view()),
    path("pagamentos/pedidos/<int:pedido_id>/", PagamentoPedidoView.as_view()),
    path("fidelidade/saldo/", FidelidadeSaldoView.as_view()),
    path("fidelidade/historico/", FidelidadeHistoricoView.as_view()),
    path("fidelidade/resgates/", FidelidadeResgateView.as_view()),
    path("promocoes/", PromocaoListView.as_view()),
]
