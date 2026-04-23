from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Roles(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        ATENDENTE = "ATENDENTE", "Atendente"
        COZINHA = "COZINHA", "Cozinha"
        GERENTE = "GERENTE", "Gerente"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENTE)


class Unidade(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255, blank=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="estoques")
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name="estoques")
    quantidade = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["produto", "unidade"], name="unique_produto_unidade_estoque"),
        ]

    def __str__(self):
        return f"{self.unidade} - {self.produto}"


class EstoqueMovimentacao(models.Model):
    class Tipos(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saida"
        AJUSTE = "AJUSTE", "Ajuste"
        ESTORNO = "ESTORNO", "Estorno"

    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE, related_name="movimentacoes")
    tipo = models.CharField(max_length=20, choices=Tipos.choices)
    quantidade = models.IntegerField()
    motivo = models.CharField(max_length=255, blank=True)
    criado_por = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class Pedido(models.Model):
    class Canais(models.TextChoices):
        APP = "APP", "App"
        TOTEM = "TOTEM", "Totem"
        BALCAO = "BALCAO", "Balcao"
        PICKUP = "DELIVERY", "DELIVERY"
        WEB = "WEB", "Web"

    class Status(models.TextChoices):
        CRIADO = "CRIADO", "Criado"
        EM_PREPARO = "EM_PREPARO", "Em preparo"
        PRONTO = "PRONTO", "Pronto"
        ENTREGUE = "ENTREGUE", "Entregue"
        CANCELADO = "CANCELADO", "Cancelado"

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="pedidos")
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name="pedidos")
    canalPedido = models.CharField(max_length=20, choices=Canais.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CRIADO)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancelamento_motivo = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.pk}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)


class Pagamento(models.Model):
    class Status(models.TextChoices):
        SOLICITADO = "SOLICITADO", "Solicitado"
        APROVADO = "APROVADO", "Aprovado"
        NEGADO = "NEGADO", "Negado"
        ERRO = "ERRO", "Erro"

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="pagamento")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SOLICITADO)
    payload = models.JSONField(default=dict)
    referencia_externa = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Fidelidade(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="fidelidade")
    consentimento = models.BooleanField(default=False)
    pontos = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class FidelidadeMovimentacao(models.Model):
    class Tipos(models.TextChoices):
        CREDITO = "CREDITO", "Credito"
        DEBITO = "DEBITO", "Debito"
        RESGATE = "RESGATE", "Resgate"

    fidelidade = models.ForeignKey(Fidelidade, on_delete=models.CASCADE, related_name="movimentacoes")
    tipo = models.CharField(max_length=20, choices=Tipos.choices)
    pontos = models.IntegerField()
    descricao = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Promocao(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    percentual_desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ativa = models.BooleanField(default=True)
    canais = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
