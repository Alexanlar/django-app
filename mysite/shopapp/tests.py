import json

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Order, Product


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="Tester", password="qwerty")
        cls.user.user_permissions.add(
            Permission.objects.get(codename="view_order")
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(delivery_address="Test address",
                                          promocode="",
                                          user_id=self.user.id)

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:order_details", kwargs={"pk": self.order.pk}))
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "user-fixture.json",
        "products-fixture.json",
        "order-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_superuser(username="Tester", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_order_export(self):
        response = self.client.get(reverse("shopapp:order_export"))
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "orders": [{"pk": 2, "delivery_address": "Lenina 5", "promocode": "qwe", "user_id": 1, "products": [5, 9]},
                       {"pk": 3, "delivery_address": "Lenina 1", "promocode": "qwert", "user_id": 1, "products": [6, 7]},
                       {"pk": 4, "delivery_address": "Pushkina 134", "promocode": "", "user_id": 1, "products": [3, 4]}]
        }
        received_data = json.loads(response.content)
        self.assertEqual(received_data, expected_data)
