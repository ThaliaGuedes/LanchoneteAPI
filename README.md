# Para ver a documentação com os requisitos faça o download do html que esta em docs
## No HTML possui uma representação visual do diagrama e DRE, além de um detalhamento de como foi implementato o backend do sistema.
<img width="1456" height="716" alt="image" src="https://github.com/user-attachments/assets/68e33103-25fe-4400-953b-948aa9a920b8" />


### Para facilitar os testes no sistema, desenvolvi um Front end simples que está nesse repositorio
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
cd NOME_DA_PASTA
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
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

Bibliotecas usadas por este backend:

- `django`
- `djangorestframework`
- `djangorestframework-simplejwt`
- `django-cors-headers`

Opcionalmente, voce pode atualizar o `pip` antes:

```powershell
python -m pip install --upgrade pip
```

## Preparacao do banco

O projeto usa SQLite e o banco esta configurado em `lanchonete/settings.py`.

Rode as migrations:

```powershell
python manage.py migrate
```

Observacao:

- a migration `core/migrations/0002_seed_unidade.py` cria uma unidade padrao chamada `Loja Lulu-Burguer`
- o banco local sera criado automaticamente como `db.sqlite3`, se necessario


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

#### Perfis de Usuarios
<img width="903" height="144" alt="image" src="https://github.com/user-attachments/assets/069888ca-c48f-455e-a49f-eef8a72d9463" />

