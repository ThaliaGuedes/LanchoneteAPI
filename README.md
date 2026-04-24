# Lanchonete API

# Para ver a documentacao com os requisitos faça o download do HTML que esta em `docs`
## No HTML existe uma representacao visual do diagrama e do DER, alem de um detalhamento de como foi implementado o backend do sistema.
<img width="1456" height="716" alt="image" src="https://github.com/user-attachments/assets/68e33103-25fe-4400-953b-948aa9a920b8" />

### Para facilitar os testes no sistema, desenvolvi um front-end simples que esta neste repositorio
https://github.com/ThaliaGuedes/LanchoneteAPI
<img width="1832" height="910" alt="image" src="https://github.com/user-attachments/assets/250c24f3-9018-4216-aa0f-2833761a5b10" />

## Visao geral

Este backend foi construido com:

- Django
- Django REST Framework
- JWT com `djangorestframework-simplejwt`
- SQLite
- `django-cors-headers`

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
- Git instalado

## Como clonar o repositorio

Se voce ainda nao baixou o projeto, use:

```powershell
git clone https://github.com/ThaliaGuedes/LanchoneteAPI.git
cd LanchoneteAPI
```

Se o repositorio ja estiver baixado, entre na pasta raiz do projeto:

```powershell
cd c:\caminho\para\o\projeto
```

Observacao:

- a pasta raiz eh a mesma que contem o arquivo `manage.py`

## Como criar e ativar o ambiente virtual

Na raiz do projeto, execute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativacao do ambiente virtual, rode:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

Quando o ambiente estiver ativo, o terminal geralmente passa a mostrar algo como:

```powershell
(.venv) PS C:\caminho\do\projeto>
```

## Como instalar as bibliotecas

Com o ambiente virtual ativado:

```powershell
python -m pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

Bibliotecas usadas por este backend:

- `django`
- `djangorestframework`
- `djangorestframework-simplejwt`
- `django-cors-headers`

## Preparacao do banco

O projeto usa SQLite e o banco esta configurado em `lanchonete/settings.py`.

Rode as migrations:

```powershell
python manage.py migrate
```

Observacoes:

- a migration `core/migrations/0002_seed_unidade.py` cria uma unidade padrao chamada `Loja Lulu-Burguer`
- o banco local sera criado automaticamente como `db.sqlite3`, se necessario

## Como subir o backend

Com o ambiente virtual ativado:

```powershell
python manage.py runserver
```

A API ficara disponivel em:

- `http://127.0.0.1:8000/`

Schema da API:

- `GET /api/schema/`

## Como rodar os testes automatizados

```powershell
python manage.py test
```

## Sequencia recomendada para testar a API

Esta e a ordem mais segura para validar o backend:

1. subir a API com `python manage.py runserver`
2. registrar um usuario em `/api/auth/register/`
3. fazer login em `/api/auth/token/`
4. copiar o token `access`
5. configurar o token nas requisicoes protegidas
6. consultar `/api/usuarios/me/`
7. consultar unidades e cardapio
8. criar produto e estoque, se necessario
9. criar pedido
10. consultar o pagamento do pedido
11. testar fidelidade
12. testar alteracao de status e cancelamento

#### Perfis de usuarios
<img width="903" height="144" alt="image" src="https://github.com/user-attachments/assets/069888ca-c48f-455e-a49f-eef8a72d9463" />

## Importante sobre autenticacao por token

Algumas rotas sao publicas, mas varias acoes exigem autenticacao com JWT.

Sempre que uma rota exigir autenticacao, envie o header:

```http
Authorization: Bearer SEU_ACCESS_TOKEN
```

Sem esse token, a API retornara `401 Unauthorized`.

Rotas que normalmente exigem token:

- `GET /api/usuarios/me/`
- `GET /api/pedidos/`
- `POST /api/pedidos/`
- `GET /api/pedidos/{id}/`
- `POST /api/pedidos/{id}/cancelamento/`
- `GET /api/pagamentos/pedidos/{pedido_id}/`
- `GET /api/fidelidade/saldo/`
- `PATCH /api/fidelidade/saldo/`
- `GET /api/fidelidade/historico/`
- `POST /api/fidelidade/resgates/`

Algumas rotas alem de token tambem exigem perfil especifico:

- `POST /api/produtos/`: `ADMIN` ou `GERENTE`
- `GET /api/estoques/`: `ADMIN`, `GERENTE` ou `ATENDENTE`
- `POST /api/estoques/movimentacoes/`: `ADMIN`, `GERENTE` ou `ATENDENTE`
- `PATCH /api/pedidos/{id}/status/`: `ADMIN`, `GERENTE` ou `COZINHA`

## Curls para testar na ordem correta

### 1. Registrar usuario

```powershell
curl -X POST http://127.0.0.1:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"cliente1\",\"email\":\"cliente1@teste.com\",\"password\":\"senha123\"}"
```

### 2. Fazer login e gerar token

Este passo eh o login da API. Ele devolve `access` e `refresh`.

```powershell
curl -X POST http://127.0.0.1:8000/api/auth/token/ `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"cliente1\",\"password\":\"senha123\"}"
```

Depois da resposta, copie o valor de `access` e salve em uma variavel:

```powershell
$TOKEN="COLE_AQUI_O_ACCESS_TOKEN"
```

### 3. Consultar usuario autenticado

```powershell
curl http://127.0.0.1:8000/api/usuarios/me/ `
  -H "Authorization: Bearer $TOKEN"
```

### 4. Listar unidades

```powershell
curl http://127.0.0.1:8000/api/unidades/
```

### 5. Ver cardapio da unidade

```powershell
curl http://127.0.0.1:8000/api/unidades/1/cardapio/
```

### 6. Listar produtos

```powershell
curl http://127.0.0.1:8000/api/produtos/
```

### 7. Criar produto

Esta rota exige token e perfil de gestao.

```powershell
curl -X POST http://127.0.0.1:8000/api/produtos/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"nome\":\"Hamburguer Artesanal\",\"descricao\":\"Pao brioche, carne e queijo\",\"preco\":\"29.90\",\"ativo\":true}"
```

### 8. Criar movimentacao de estoque

Esta rota exige token e perfil operacional.

```powershell
curl -X POST http://127.0.0.1:8000/api/estoques/movimentacoes/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"produto_id\":1,\"unidade_id\":1,\"tipo\":\"ENTRADA\",\"quantidade\":20,\"motivo\":\"Reposicao inicial\"}"
```

### 9. Consultar estoque da unidade

Esta rota exige token e perfil operacional.

```powershell
curl http://127.0.0.1:8000/api/estoques/?unidadeId=1 `
  -H "Authorization: Bearer $TOKEN"
```

### 10. Criar pedido

Esta rota exige token.

```powershell
curl -X POST http://127.0.0.1:8000/api/pedidos/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"unidadeId\":1,\"canalPedido\":\"APP\",\"itens\":[{\"produtoId\":1,\"quantidade\":2}]}"
```

### 11. Listar pedidos

Esta rota exige token.

```powershell
curl http://127.0.0.1:8000/api/pedidos/ `
  -H "Authorization: Bearer $TOKEN"
```

### 12. Filtrar pedidos

```powershell
curl "http://127.0.0.1:8000/api/pedidos/?canalPedido=APP&status=PRONTO" `
  -H "Authorization: Bearer $TOKEN"
```

### 13. Consultar detalhe de um pedido

```powershell
curl http://127.0.0.1:8000/api/pedidos/1/ `
  -H "Authorization: Bearer $TOKEN"
```

### 14. Consultar pagamento do pedido

```powershell
curl http://127.0.0.1:8000/api/pagamentos/pedidos/1/ `
  -H "Authorization: Bearer $TOKEN"
```

### 15. Consultar saldo de fidelidade

```powershell
curl http://127.0.0.1:8000/api/fidelidade/saldo/ `
  -H "Authorization: Bearer $TOKEN"
```

### 16. Ativar consentimento de fidelidade

```powershell
curl -X PATCH http://127.0.0.1:8000/api/fidelidade/saldo/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"consentimento\":true}"
```

### 17. Ver historico de fidelidade

```powershell
curl http://127.0.0.1:8000/api/fidelidade/historico/ `
  -H "Authorization: Bearer $TOKEN"
```

### 18. Resgatar pontos

```powershell
curl -X POST http://127.0.0.1:8000/api/fidelidade/resgates/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"pontos\":20,\"descricao\":\"Cupom simples\"}"
```

### 19. Atualizar status do pedido

Esta rota exige token e perfil de cozinha ou gestao.

```powershell
curl -X PATCH http://127.0.0.1:8000/api/pedidos/1/status/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"status\":\"PRONTO\"}"
```

### 20. Cancelar pedido

Esta rota exige token.

```powershell
curl -X POST http://127.0.0.1:8000/api/pedidos/1/cancelamento/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -d "{\"motivo\":\"Cliente desistiu da compra\"}"
```

### 21. Listar promocoes

```powershell
curl http://127.0.0.1:8000/api/promocoes/
```

## Rotas publicas

Estas rotas podem ser testadas sem token:

- `GET /api/unidades/`
- `GET /api/unidades/{id}/cardapio/`
- `GET /api/produtos/`
- `GET /api/promocoes/`
- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`

## Dicas importantes

- use sempre a barra no final da URL, por exemplo: `/api/auth/register/`
- para `POST`, `PATCH` e outras chamadas com body, envie `Content-Type: application/json`
- copie o `access` retornado no login e use nas chamadas protegidas
- se estiver usando Insomnia ou Postman, configure o header `Authorization` com `Bearer SEU_TOKEN`

## Resumo rapido de comandos

```powershell
git clone https://github.com/ThaliaGuedes/LanchoneteAPI.git
cd LanchoneteAPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
python manage.py migrate
python manage.py runserver
python manage.py test
```
