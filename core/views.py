from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Estoque, Fidelidade, Pagamento, Pedido, Produto, Promocao, Unidade, Usuario
from .permissions import IsAdminOrManager, IsCozinhaOuGestao, IsStaffOperacao
from .serializers import (
    CardapioItemSerializer,
    EstoqueMovimentacaoSerializer,
    EstoqueSerializer,
    FidelidadeConsentimentoSerializer,
    FidelidadeMovimentacaoSerializer,
    FidelidadeSerializer,
    PagamentoSerializer,
    PedidoCancelamentoSerializer,
    PedidoCreateSerializer,
    PedidoSerializer,
    PedidoStatusSerializer,
    ProdutoSerializer,
    PromocaoSerializer,
    RegistroUsuarioSerializer,
    UnidadeSerializer,
    UsuarioSerializer,
    ResgateSerializer,
)

class RegistroUsuarioView(generics.CreateAPIView):
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [AllowAny]


class PerfilUsuarioView(generics.RetrieveAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UnidadeListView(generics.ListAPIView):
    serializer_class = UnidadeSerializer
    permission_classes = [AllowAny]
    queryset = Unidade.objects.filter(ativa=True).order_by("nome")


class ProdutoListCreateView(generics.ListCreateAPIView):
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        queryset = Produto.objects.all().order_by("nome")
        ativo = self.request.query_params.get("ativo")
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() == "true")
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrManager()]


class CardapioUnidadeView(generics.ListAPIView):
    serializer_class = CardapioItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        unidade_id = self.kwargs["unidade_id"]
        return (
            Estoque.objects.select_related("produto")
            .filter(unidade_id=unidade_id, quantidade__gt=0, produto__ativo=True)
            .order_by("produto__nome")
        )


class EstoqueListView(generics.ListAPIView):
    serializer_class = EstoqueSerializer
    permission_classes = [IsAuthenticated, IsStaffOperacao]

    def get_queryset(self):
        queryset = Estoque.objects.select_related("produto", "unidade").order_by("unidade__nome", "produto__nome")
        unidade_id = self.request.query_params.get("unidadeId")
        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)
        return queryset


class EstoqueMovimentacaoCreateView(generics.CreateAPIView):
    serializer_class = EstoqueMovimentacaoSerializer
    permission_classes = [IsAuthenticated, IsStaffOperacao]


class PedidoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Pedido.objects.select_related("unidade", "usuario", "pagamento").prefetch_related("itens__produto")
        request = self.request

        canal = request.query_params.get("canalPedido")
        unidade_id = request.query_params.get("unidadeId")
        status_param = request.query_params.get("status")

        if request.user.role == Usuario.Roles.CLIENTE:
            queryset = queryset.filter(usuario=request.user)

        if canal:
            queryset = queryset.filter(canalPedido=canal)
        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PedidoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PedidoSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PedidoCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)


class PedidoDetalheView(generics.RetrieveAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.select_related("unidade", "usuario", "pagamento").prefetch_related("itens__produto")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == Usuario.Roles.CLIENTE:
            queryset = queryset.filter(usuario=self.request.user)
        return queryset


class PedidoStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsCozinhaOuGestao]

    def patch(self, request, pk):
        pedido = generics.get_object_or_404(Pedido, pk=pk)
        serializer = PedidoStatusSerializer(data=request.data, instance=pedido, context={"request": request})
        serializer.is_valid(raise_exception=True)
        pedido = serializer.update(pedido, serializer.validated_data)
        return Response(PedidoSerializer(pedido).data)


class PedidoCancelamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        pedido = generics.get_object_or_404(Pedido, pk=pk)
        if request.user.role == Usuario.Roles.CLIENTE and pedido.usuario_id != request.user.id:
            return Response(
                {"error": {"code": "http_403", "message": "Sem permissao.", "details": {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PedidoCancelamentoSerializer(data=request.data, instance=pedido, context={"request": request})
        serializer.is_valid(raise_exception=True)
        pedido = serializer.update(pedido, serializer.validated_data)
        return Response(PedidoSerializer(pedido).data)


class PagamentoPedidoView(generics.RetrieveAPIView):
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pedido_id"
    queryset = Pagamento.objects.select_related("pedido")

    def get_object(self):
        pagamento = generics.get_object_or_404(self.get_queryset(), pedido_id=self.kwargs["pedido_id"])
        if self.request.user.role == Usuario.Roles.CLIENTE and pagamento.pedido.usuario_id != self.request.user.id:
            self.permission_denied(self.request)
        return pagamento


class FidelidadeSaldoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fidelidade, _ = Fidelidade.objects.get_or_create(usuario=request.user)
        return Response(FidelidadeSerializer(fidelidade).data)

    def patch(self, request):
        fidelidade, _ = Fidelidade.objects.get_or_create(usuario=request.user)
        serializer = FidelidadeConsentimentoSerializer(fidelidade, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(FidelidadeSerializer(fidelidade).data)


class FidelidadeHistoricoView(generics.ListAPIView):
    serializer_class = FidelidadeMovimentacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        fidelidade, _ = Fidelidade.objects.get_or_create(usuario=self.request.user)
        return fidelidade.movimentacoes.order_by("-created_at")


class FidelidadeResgateView(generics.CreateAPIView):
    serializer_class = ResgateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        movimentacao = serializer.save()
        return Response(FidelidadeMovimentacaoSerializer(movimentacao).data, status=status.HTTP_201_CREATED)


class PromocaoListView(generics.ListAPIView):
    serializer_class = PromocaoSerializer
    permission_classes = [AllowAny]
    queryset = Promocao.objects.filter(ativa=True).order_by("-created_at")
