from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Estoque, Fidelidade, Pedido, Produto, Unidade, Usuario


class RegistroUsuarioApiTests(APITestCase):
    def test_registra_cliente_e_cria_fidelidade(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "cliente_novo",
                "email": "cliente@teste.com",
                "password": "senha123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username="cliente_novo")
        self.assertEqual(usuario.role, Usuario.Roles.CLIENTE)
        self.assertTrue(Fidelidade.objects.filter(usuario=usuario).exists())


class PedidoApiTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="cliente",
            password="senha123",
            role=Usuario.Roles.CLIENTE,
        )
        self.unidade = Unidade.objects.create(nome="Centro", endereco="Rua 1")
        self.produto = Produto.objects.create(nome="Hamburguer", preco="25.00", ativo=True)
        Estoque.objects.create(produto=self.produto, unidade=self.unidade, quantidade=10)

        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "cliente", "password": "senha123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

    def test_cria_pedido_com_canal_e_baixa_estoque(self):
        response = self.client.post(
            "/api/pedidos/",
            {
                "unidadeId": self.unidade.id,
                "canalPedido": "APP",
                "itens": [{"produtoId": self.produto.id, "quantidade": 2}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(Estoque.objects.get(produto=self.produto, unidade=self.unidade).quantidade, 8)

    def test_lista_pedidos_filtrando_por_canal(self):
        self.client.post(
            "/api/pedidos/",
            {
                "unidadeId": self.unidade.id,
                "canalPedido": "TOTEM",
                "itens": [{"produtoId": self.produto.id, "quantidade": 1}],
            },
            format="json",
        )

        response = self.client.get("/api/pedidos/?canalPedido=TOTEM")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class FidelidadeApiTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="fiel",
            password="senha123",
            role=Usuario.Roles.CLIENTE,
        )
        self.fidelidade = Fidelidade.objects.create(usuario=self.user, consentimento=True, pontos=50)
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "fiel", "password": "senha123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

    def test_resgata_pontos(self):
        response = self.client.post(
            "/api/fidelidade/resgates/",
            {"pontos": 20, "descricao": "Cupom simples"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.fidelidade.refresh_from_db()
        self.assertEqual(self.fidelidade.pontos, 30)
