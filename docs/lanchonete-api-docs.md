# Lanchonete API

Guia completo para executar e testar o backend da lanchonete.

## Visao geral

Este backend foi construido com:

- Django
- Django REST Framework
- JWT com `djangorestframework-simplejwt`
- SQLite
- `django-cors-headers`

Funcionalidades principais:

- autenticacao e cadastro de usuarios
- controle de roles
- consulta de unidades e cardapio
- criacao e acompanhamento de pedidos
- movimentacao de estoque
- fidelidade
- mock de pagamento
- promocoes

## Estrutura principal

- `manage.py`: comandos do projeto Django
- `lanchonete/settings.py`: configuracoes principais
- `core/models.py`: modelos do dominio
- `core/views.py`: endpoints
- `core/serializers.py`: validacoes e contratos
- `core/services.py`: regras de negocio
- `core/tests.py`: testes automatizados

## Requisitos

Antes de rodar o projeto, garanta que voce tenha:

- Python 3.12 ou compativel
- `pip`
- PowerShell ou terminal equivalente

## Instalacao do ambiente

No diretorio raiz do projeto, execute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

Se o PowerShell bloquear a ativacao do ambiente virtual, rode:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Preparacao do banco

O projeto usa SQLite e o banco esta configurado em `lanchonete/settings.py`.

Rode as migrations:

```powershell
python manage.py migrate
```

Observacao:

- a migration `core/migrations/0002_seed_unidade.py` cria uma unidade padrao chamada `Loja Lulu-Burguer`

## Como executar o backend

Com o ambiente virtual ativado:

```powershell
python manage.py runserver
```

Depois disso, a API ficara disponivel em:

- `http://127.0.0.1:8000/`

Schema da API:

- `GET /api/schema/`

## Como rodar os testes automatizados

Os testes existentes estao em `core/tests.py`.

Para rodar tudo:

```powershell
python manage.py test
```

O que esses testes cobrem:

- registro de usuario com criacao automatica da fidelidade
- criacao de pedido com baixa de estoque
- listagem de pedidos filtrando por canal
- resgate de pontos de fidelidade

## Fluxo recomendado de teste manual

A melhor ordem para validar o backend e:

1. subir a API
2. registrar um usuario
3. gerar token JWT
4. consultar perfil
5. consultar unidades
6. criar produtos e estoque, se necessario
7. criar pedido
8. consultar pagamento
9. testar fidelidade
10. testar filtros e mudancas de status

## Autenticacao

### 1. Registrar usuario

Endpoint:

- `POST /api/auth/register/`

Exemplo:

```powershell
curl -X POST http://127.0.0.1:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"cliente1\",\"email\":\"cliente1@teste.com\",\"password\":\"senha123\"}"
```

Resposta esperada:

- `201 Created`

### 2. Fazer login e obter token

Endpoint:

- `POST /api/auth/token/`

Exemplo:

```powershell
curl -X POST http://127.0.0.1:8000/api/auth/token/ `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"cliente1\",\"password\":\"senha123\"}"
```

Resposta esperada:

- `200 OK`
- retorno com `access` e `refresh`

Exemplo de resposta:

```json
{
  "refresh": "seu_refresh_token",
  "access": "seu_access_token"
}
```

Guarde o valor de `access` para usar nas proximas chamadas:

```powershell
$TOKEN="COLE_AQUI_O_ACCESS_TOKEN"
```

### 3. Renovar token

Endpoint:

- `POST /api/auth/token/refresh/`

Exemplo:

```powershell
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ `
  -H "Content-Type: application/json" `
  -d "{\"refresh\":\"SEU_REFRESH_TOKEN\"}"
```

## Testando endpoints autenticados

### 4. Consultar usuario logado

Endpoint:

- `GET /api/usuarios/me/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/usuarios/me/ `
  -H "Authorization: Bearer $TOKEN"
```

## Unidades e cardapio

### 5. Listar unidades

Endpoint:

- `GET /api/unidades/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/unidades/
```

### 6. Consultar cardapio por unidade

Endpoint:

- `GET /api/unidades/{id}/cardapio/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/unidades/1/cardapio/
```

Observacao:

- esse endpoint lista produtos com estoque maior que zero e produto ativo

## Produtos

### 7. Listar produtos

Endpoint:

- `GET /api/produtos/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/produtos/
```

### 8. Criar produto

Endpoint:

- `POST /api/produtos/`

Importante:

- esse endpoint exige usuario autenticado com role de gestao

Exemplo de payload:

```json
{
  "nome": "Hamburguer Artesanal",
  "descricao": "Pao brioche, carne e queijo",
  "preco": "29.90",
  "ativo": true
}
```

Exemplo de chamada:

```powershell
curl -X POST http://127.0.0.1:8000/api/produtos/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"nome\":\"Hamburguer Artesanal\",\"descricao\":\"Pao brioche, carne e queijo\",\"preco\":\"29.90\",\"ativo\":true}"
```

## Estoque

### 9. Consultar estoque

Endpoint:

- `GET /api/estoques/`
- `GET /api/estoques/?unidadeId=1`

Importante:

- esse endpoint exige autenticacao e permissao operacional

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/estoques/?unidadeId=1 `
  -H "Authorization: Bearer $TOKEN"
```

### 10. Registrar movimentacao de estoque

Endpoint:

- `POST /api/estoques/movimentacoes/`

Exemplo de payload:

```json
{
  "produto_id": 1,
  "unidade_id": 1,
  "tipo": "ENTRADA",
  "quantidade": 20,
  "motivo": "Reposicao inicial"
}
```

Exemplo de chamada:

```powershell
curl -X POST http://127.0.0.1:8000/api/estoques/movimentacoes/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"produto_id\":1,\"unidade_id\":1,\"tipo\":\"ENTRADA\",\"quantidade\":20,\"motivo\":\"Reposicao inicial\"}"
```

## Pedidos

### 11. Criar pedido

Endpoint:

- `POST /api/pedidos/`

Exemplo de payload:

```json
{
  "unidadeId": 1,
  "canalPedido": "APP",
  "itens": [
    {
      "produtoId": 1,
      "quantidade": 2
    }
  ]
}
```

Exemplo de chamada:

```powershell
curl -X POST http://127.0.0.1:8000/api/pedidos/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"unidadeId\":1,\"canalPedido\":\"APP\",\"itens\":[{\"produtoId\":1,\"quantidade\":2}]}"
```

Comportamento esperado:

- o estoque eh reduzido
- o valor total do pedido eh calculado
- um pagamento mock eh criado
- se o pagamento mock for aprovado, o pedido vai para `EM_PREPARO`
- se o pagamento mock for negado, o pedido vai para `CANCELADO` com estorno de estoque

### 12. Listar pedidos

Endpoint:

- `GET /api/pedidos/`

Filtros suportados:

- `canalPedido`
- `unidadeId`
- `status`

Exemplos:

```powershell
curl http://127.0.0.1:8000/api/pedidos/ `
  -H "Authorization: Bearer $TOKEN"
```

```powershell
curl "http://127.0.0.1:8000/api/pedidos/?canalPedido=TOTEM&status=PRONTO" `
  -H "Authorization: Bearer $TOKEN"
```

### 13. Consultar detalhe de um pedido

Endpoint:

- `GET /api/pedidos/{id}/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/pedidos/1/ `
  -H "Authorization: Bearer $TOKEN"
```

### 14. Atualizar status do pedido

Endpoint:

- `PATCH /api/pedidos/{id}/status/`

Importante:

- esse endpoint exige autenticacao e permissao de cozinha ou gestao

Exemplo de payload:

```json
{
  "status": "PRONTO"
}
```

Exemplo:

```powershell
curl -X PATCH http://127.0.0.1:8000/api/pedidos/1/status/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"status\":\"PRONTO\"}"
```

Fluxo de status valido:

- `CRIADO -> CANCELADO`
- `EM_PREPARO -> PRONTO`
- `EM_PREPARO -> CANCELADO`
- `PRONTO -> ENTREGUE`
- `PRONTO -> CANCELADO`

### 15. Cancelar pedido

Endpoint:

- `POST /api/pedidos/{id}/cancelamento/`

Exemplo de payload:

```json
{
  "motivo": "Cliente desistiu da compra"
}
```

Exemplo:

```powershell
curl -X POST http://127.0.0.1:8000/api/pedidos/1/cancelamento/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"motivo\":\"Cliente desistiu da compra\"}"
```

## Pagamentos

### 16. Consultar pagamento do pedido

Endpoint:

- `GET /api/pagamentos/pedidos/{pedido_id}/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/pagamentos/pedidos/1/ `
  -H "Authorization: Bearer $TOKEN"
```

O retorno inclui:

- `status`
- `payload`
- `referencia_externa`
- datas de criacao e atualizacao

## Fidelidade

### 17. Consultar saldo

Endpoint:

- `GET /api/fidelidade/saldo/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/fidelidade/saldo/ `
  -H "Authorization: Bearer $TOKEN"
```

### 18. Atualizar consentimento

Endpoint:

- `PATCH /api/fidelidade/saldo/`

Exemplo:

```powershell
curl -X PATCH http://127.0.0.1:8000/api/fidelidade/saldo/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"consentimento\":true}"
```

### 19. Consultar historico

Endpoint:

- `GET /api/fidelidade/historico/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/fidelidade/historico/ `
  -H "Authorization: Bearer $TOKEN"
```

### 20. Resgatar pontos

Endpoint:

- `POST /api/fidelidade/resgates/`

Exemplo:

```powershell
curl -X POST http://127.0.0.1:8000/api/fidelidade/resgates/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"pontos\":20,\"descricao\":\"Cupom simples\"}"
```

## Promocoes

### 21. Listar promocoes

Endpoint:

- `GET /api/promocoes/`

Exemplo:

```powershell
curl http://127.0.0.1:8000/api/promocoes/
```

## Cenarios de teste sugeridos

### Cenario 1: cadastro e login

Resultado esperado:

- usuario criado com sucesso
- token JWT retornado
- endpoint `/api/usuarios/me/` responde com o usuario autenticado

### Cenario 2: pedido com estoque suficiente

Pre-condicao:

- produto ativo
- estoque disponivel na unidade

Resultado esperado:

- pedido criado
- estoque reduzido
- pagamento criado

### Cenario 3: pedido com estoque insuficiente

Resultado esperado:

- erro de validacao ao criar pedido

### Cenario 4: pagamento negado pelo mock

Resultado esperado:

- pedido cancelado
- estoque restaurado

Observacao:

- o mock escolhe aprovado ou negado de forma aleatoria

### Cenario 5: fidelidade com consentimento

Fluxo:

1. ativar consentimento
2. criar pedido aprovado
3. consultar saldo

Resultado esperado:

- pontos creditados

### Cenario 6: resgate de pontos

Resultado esperado:

- pontos debitados
- historico atualizado

## Possiveis erros comuns

### Erro: `ModuleNotFoundError: No module named 'django'`

Causa:

- dependencias nao instaladas no ambiente atual

Correcao:

```powershell
.\.venv\Scripts\Activate.ps1
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

### Erro: `401 Unauthorized`

Causa:

- token ausente, expirado ou invalido

Correcao:

- gere um novo token em `/api/auth/token/`
- confira o header `Authorization: Bearer SEU_TOKEN`

### Erro: `403 Forbidden`

Causa:

- usuario sem role suficiente para o endpoint

Correcao:

- use um usuario com permissao adequada para estoque, produtos ou mudanca de status

### Erro: `400 Bad Request`

Causa:

- payload invalido

Correcao:

- confira nomes de campos como `unidadeId`, `canalPedido`, `produtoId`, `quantidade`

## Resumo rapido de comandos

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
python manage.py migrate
python manage.py runserver
python manage.py test
```

## Endpoints principais

- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET /api/usuarios/me/`
- `GET /api/unidades/`
- `GET /api/unidades/{id}/cardapio/`
- `GET|POST /api/produtos/`
- `GET /api/estoques/`
- `POST /api/estoques/movimentacoes/`
- `GET|POST /api/pedidos/`
- `GET /api/pedidos/{id}/`
- `PATCH /api/pedidos/{id}/status/`
- `POST /api/pedidos/{id}/cancelamento/`
- `GET /api/pagamentos/pedidos/{pedido_id}/`
- `GET /api/fidelidade/saldo/`
- `PATCH /api/fidelidade/saldo/`
- `GET /api/fidelidade/historico/`
- `POST /api/fidelidade/resgates/`
- `GET /api/promocoes/`
