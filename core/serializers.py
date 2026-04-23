from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import (
    Estoque,
    EstoqueMovimentacao,
    Fidelidade,
    FidelidadeMovimentacao,
    Pagamento,
    Pedido,
    Produto,
    Promocao,
    Unidade,
)
from .services import atualizar_status_pedido, cancelar_pedido, criar_pedido, movimentar_estoque, resgatar_pontos

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "password", "first_name", "last_name", "role"]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        Fidelidade.objects.get_or_create(usuario=user)
        return user


class UnidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ["id", "nome", "endereco", "ativa"]


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ["id", "nome", "descricao", "preco", "ativo"]


class CardapioItemSerializer(serializers.ModelSerializer):
    produtoId = serializers.IntegerField(source="produto.id", read_only=True)
    nome = serializers.CharField(source="produto.nome", read_only=True)
    descricao = serializers.CharField(source="produto.descricao", read_only=True)
    preco = serializers.DecimalField(source="produto.preco", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Estoque
        fields = ["produtoId", "nome", "descricao", "preco", "quantidade"]


class EstoqueSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    unidade = UnidadeSerializer(read_only=True)

    class Meta:
        model = Estoque
        fields = ["id", "produto", "unidade", "quantidade"]


class EstoqueMovimentacaoSerializer(serializers.ModelSerializer):
    produto_id = serializers.IntegerField(write_only=True)
    unidade_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = EstoqueMovimentacao
        fields = [
            "produto_id",
            "unidade_id",
            "tipo",
            "quantidade",
            "motivo",
        ]

    def create(self, validated_data):
        produto_id = validated_data.pop("produto_id")
        unidade_id = validated_data.pop("unidade_id")

        # 🔥 cria ou pega estoque automaticamente
        estoque, _ = Estoque.objects.get_or_create(
            produto_id=produto_id,
            unidade_id=unidade_id,
            defaults={"quantidade": 0}
        )

        # 🔄 atualiza quantidade
        if validated_data["tipo"] == "ENTRADA":
            estoque.quantidade += validated_data["quantidade"]
        else:
            estoque.quantidade -= validated_data["quantidade"]

        estoque.save()

        # 💾 cria movimentação
        movimentacao = EstoqueMovimentacao.objects.create(
            estoque=estoque,
            **validated_data
        )

        return movimentacao


class PedidoItemInputSerializer(serializers.Serializer):
    produtoId = serializers.IntegerField(source="produto_id")
    quantidade = serializers.IntegerField()


class PedidoItemSerializer(serializers.Serializer):
    produtoId = serializers.IntegerField(source="produto.id")
    nome = serializers.CharField(source="produto.nome")
    quantidade = serializers.IntegerField()
    precoUnitario = serializers.DecimalField(source="preco_unitario", max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = ["status", "payload", "referencia_externa", "created_at", "updated_at"]


class PedidoSerializer(serializers.ModelSerializer):
    itens = PedidoItemSerializer(many=True, read_only=True)
    pagamento = PagamentoSerializer(read_only=True)
    usuarioId = serializers.IntegerField(source="usuario.id", read_only=True)
    unidadeId = serializers.IntegerField(source="unidade.id")
    valorTotal = serializers.DecimalField(source="valor_total", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id",
            "usuarioId",
            "unidadeId",
            "canalPedido",
            "status",
            "valorTotal",
            "cancelamento_motivo",
            "created_at",
            "updated_at",
            "itens",
            "pagamento",
        ]


class PedidoCreateSerializer(serializers.Serializer):
    unidadeId = serializers.PrimaryKeyRelatedField(source="unidade", queryset=Unidade.objects.filter(ativa=True))
    canalPedido = serializers.ChoiceField(choices=Pedido.Canais.choices)
    itens = PedidoItemInputSerializer(many=True)

    def create(self, validated_data):
        request = self.context["request"]
        return criar_pedido(
            usuario=request.user,
            unidade=validated_data["unidade"],
            canal_pedido=validated_data["canalPedido"],
            itens=validated_data["itens"],
        )

    def to_representation(self, instance):
        return PedidoSerializer(instance, context=self.context).data


class PedidoStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Pedido.Status.choices)

    def update(self, instance, validated_data):
        return atualizar_status_pedido(pedido=instance, novo_status=validated_data["status"])


class PedidoCancelamentoSerializer(serializers.Serializer):
    motivo = serializers.CharField(max_length=255)

    def update(self, instance, validated_data):
        request = self.context["request"]
        return cancelar_pedido(
            pedido=instance,
            motivo=validated_data["motivo"],
            usuario=request.user,
            restaurar_estoque=True,
        )


class FidelidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fidelidade
        fields = ["consentimento", "pontos", "updated_at"]


class FidelidadeConsentimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fidelidade
        fields = ["consentimento"]


class FidelidadeMovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FidelidadeMovimentacao
        fields = ["id", "tipo", "pontos", "descricao", "created_at"]


class ResgateSerializer(serializers.Serializer):
    pontos = serializers.IntegerField()
    descricao = serializers.CharField(max_length=255)

    def create(self, validated_data):
        request = self.context["request"]
        return resgatar_pontos(
            usuario=request.user,
            pontos=validated_data["pontos"],
            descricao=validated_data["descricao"],
        )


class PromocaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocao
        fields = ["id", "titulo", "descricao", "percentual_desconto", "ativa", "canais", "created_at"]
