from django.contrib import admin

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
    Usuario,
)

admin.site.register(Usuario)
admin.site.register(Unidade)
admin.site.register(Produto)
admin.site.register(Estoque)
admin.site.register(EstoqueMovimentacao)
admin.site.register(Pedido)
admin.site.register(Pagamento)
admin.site.register(Fidelidade)
admin.site.register(FidelidadeMovimentacao)
admin.site.register(Promocao)
