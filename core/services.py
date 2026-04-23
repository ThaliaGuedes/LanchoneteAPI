import uuid
from decimal import Decimal
from random import choice

from django.db import transaction
from rest_framework import serializers

from .models import (
    Estoque,
    EstoqueMovimentacao,
    Fidelidade,
    FidelidadeMovimentacao,
    ItemPedido,
    Pagamento,
    Pedido,
    Produto,
)


class MockPaymentGateway:
    @staticmethod
    def solicitar_pagamento(*, pedido, valor, canal):
        status = choice([Pagamento.Status.APROVADO, Pagamento.Status.NEGADO])
        return {
            "status": status,
            "payload": {
                "mock": True,
                "pedidoId": pedido.id,
                "valor": str(valor),
                "canalPedido": canal,
            },
            "referencia_externa": uuid.uuid4().hex[:16],
        }


@transaction.atomic
def criar_pedido(*, usuario, unidade, canal_pedido, itens):
    if not itens:
        raise serializers.ValidationError({"itens": ["Informe ao menos um item."]})

    pedido = Pedido.objects.create(
        usuario=usuario,
        unidade=unidade,
        canalPedido=canal_pedido,
        status=Pedido.Status.CRIADO,
    )

    total = Decimal("0.00")

    for item in itens:
        try:
            produto = Produto.objects.get(pk=item["produto_id"], ativo=True)
        except Produto.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"itens": [f"Produto {item['produto_id']} nao encontrado ou inativo."]}
            ) from exc

        try:
            estoque = (
                Estoque.objects.select_for_update()
                .select_related("produto", "unidade")
                .get(produto=produto, unidade=unidade)
            )
        except Estoque.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"itens": [f"Produto {produto.nome} indisponivel na unidade selecionada."]}
            ) from exc
        quantidade = item["quantidade"]

        if quantidade <= 0:
            raise serializers.ValidationError({"itens": ["Quantidade deve ser maior que zero."]})

        if estoque.quantidade < quantidade:
            raise serializers.ValidationError(
                {"itens": [f"Estoque insuficiente para o produto {produto.nome}."]}
            )

        subtotal = produto.preco * quantidade
        total += subtotal

        estoque.quantidade -= quantidade
        estoque.save(update_fields=["quantidade"])
        EstoqueMovimentacao.objects.create(
            estoque=estoque,
            tipo=EstoqueMovimentacao.Tipos.SAIDA,
            quantidade=quantidade,
            motivo=f"Reserva para pedido {pedido.id}",
            criado_por=usuario,
        )

        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal,
        )

    pedido.valor_total = total
    pedido.save(update_fields=["valor_total"])

    retorno_pagamento = MockPaymentGateway.solicitar_pagamento(
        pedido=pedido,
        valor=total,
        canal=canal_pedido,
    )
    Pagamento.objects.create(
        pedido=pedido,
        status=retorno_pagamento["status"],
        payload=retorno_pagamento["payload"],
        referencia_externa=retorno_pagamento["referencia_externa"],
    )

    if retorno_pagamento["status"] == Pagamento.Status.APROVADO:
        pedido.status = Pedido.Status.EM_PREPARO
        pedido.save(update_fields=["status", "updated_at"])
        creditar_pontos_por_pedido(pedido)
    else:
        cancelar_pedido(
            pedido=pedido,
            motivo="Pagamento negado pelo mock externo.",
            usuario=usuario,
            restaurar_estoque=True,
        )

    return pedido


def creditar_pontos_por_pedido(pedido):
    fidelidade, _ = Fidelidade.objects.get_or_create(usuario=pedido.usuario)
    if not fidelidade.consentimento:
        return

    pontos = int(pedido.valor_total)
    if pontos <= 0:
        return

    fidelidade.pontos += pontos
    fidelidade.save(update_fields=["pontos", "updated_at"])
    FidelidadeMovimentacao.objects.create(
        fidelidade=fidelidade,
        tipo=FidelidadeMovimentacao.Tipos.CREDITO,
        pontos=pontos,
        descricao=f"Credito do pedido {pedido.id}",
    )


@transaction.atomic
def cancelar_pedido(*, pedido, motivo, usuario=None, restaurar_estoque=False):
    if pedido.status == Pedido.Status.CANCELADO:
        raise serializers.ValidationError({"status": ["Pedido ja esta cancelado."]})

    if pedido.status == Pedido.Status.ENTREGUE:
        raise serializers.ValidationError({"status": ["Pedido entregue nao pode ser cancelado."]})

    pedido.status = Pedido.Status.CANCELADO
    pedido.cancelamento_motivo = motivo
    pedido.save(update_fields=["status", "cancelamento_motivo", "updated_at"])

    if restaurar_estoque:
        for item in pedido.itens.select_related("produto").all():
            estoque = Estoque.objects.select_for_update().get(
                produto=item.produto,
                unidade=pedido.unidade,
            )
            estoque.quantidade += item.quantidade
            estoque.save(update_fields=["quantidade"])
            EstoqueMovimentacao.objects.create(
                estoque=estoque,
                tipo=EstoqueMovimentacao.Tipos.ESTORNO,
                quantidade=item.quantidade,
                motivo=f"Estorno do pedido {pedido.id}",
                criado_por=usuario,
            )

    if hasattr(pedido, "pagamento") and pedido.pagamento.status == Pagamento.Status.APROVADO:
        fidelidade = getattr(pedido.usuario, "fidelidade", None)
        pontos = int(pedido.valor_total)
        if fidelidade and fidelidade.consentimento and pontos > 0 and fidelidade.pontos >= pontos:
            fidelidade.pontos -= pontos
            fidelidade.save(update_fields=["pontos", "updated_at"])
            FidelidadeMovimentacao.objects.create(
                fidelidade=fidelidade,
                tipo=FidelidadeMovimentacao.Tipos.DEBITO,
                pontos=pontos,
                descricao=f"Debito do cancelamento do pedido {pedido.id}",
            )


def atualizar_status_pedido(*, pedido, novo_status):
    fluxo = {
        Pedido.Status.EM_PREPARO: {Pedido.Status.PRONTO, Pedido.Status.CANCELADO},
        Pedido.Status.PRONTO: {Pedido.Status.ENTREGUE, Pedido.Status.CANCELADO},
        Pedido.Status.CRIADO: {Pedido.Status.CANCELADO},
        Pedido.Status.CANCELADO: set(),
        Pedido.Status.ENTREGUE: set(),
    }

    permitidos = fluxo.get(pedido.status, set())
    if novo_status not in permitidos:
        raise serializers.ValidationError(
            {"status": [f"Transicao invalida de {pedido.status} para {novo_status}."]}
        )

    pedido.status = novo_status
    pedido.save(update_fields=["status", "updated_at"])
    return pedido


@transaction.atomic
def movimentar_estoque(*, estoque, tipo, quantidade, motivo, usuario=None):
    if quantidade <= 0:
        raise serializers.ValidationError({"quantidade": ["Quantidade deve ser maior que zero."]})

    if tipo == EstoqueMovimentacao.Tipos.ENTRADA:
        estoque.quantidade += quantidade
    elif tipo in {EstoqueMovimentacao.Tipos.SAIDA, EstoqueMovimentacao.Tipos.AJUSTE}:
        if estoque.quantidade < quantidade:
            raise serializers.ValidationError({"quantidade": ["Estoque insuficiente."]})
        estoque.quantidade -= quantidade
    else:
        raise serializers.ValidationError({"tipo": ["Tipo de movimentacao invalido."]})

    estoque.save(update_fields=["quantidade"])
    return EstoqueMovimentacao.objects.create(
        estoque=estoque,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo,
        criado_por=usuario,
    )


@transaction.atomic
def resgatar_pontos(*, usuario, pontos, descricao):
    fidelidade, _ = Fidelidade.objects.get_or_create(usuario=usuario)
    if not fidelidade.consentimento:
        raise serializers.ValidationError(
            {"consentimento": ["Consentimento obrigatorio para usar fidelidade."]}
        )
    if pontos <= 0:
        raise serializers.ValidationError({"pontos": ["Informe uma quantidade valida."]})
    if fidelidade.pontos < pontos:
        raise serializers.ValidationError({"pontos": ["Saldo insuficiente para resgate."]})

    fidelidade.pontos -= pontos
    fidelidade.save(update_fields=["pontos", "updated_at"])
    return FidelidadeMovimentacao.objects.create(
        fidelidade=fidelidade,
        tipo=FidelidadeMovimentacao.Tipos.RESGATE,
        pontos=pontos,
        descricao=descricao,
    )
