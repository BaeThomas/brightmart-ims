from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from inventory.models import Category, Product, InventoryTransaction
from inventory.views import ReceiveStockView
from suppliers.models import Supplier


class StockRollbackTest(TestCase):
    def test_receive_rolls_back_when_history_fails(self):
        user = get_user_model().objects.create_user(
            username="rollback_tester",
            password="TestPassword123!",
            role="STAFF",
        )

        category = Category.objects.create(
            category_name="Test Category"
        )

        product = Product.objects.create(
            category=category,
            sku="TEST-001",
            product_name="Test Product",
            price="100.00",
            stock_quantity=5,
            reorder_level=2,
        )

        supplier = Supplier.objects.create(
            supplier_code="TEST-SUP-001",
            supplier_name="Test Supplier",
            email="supplier@example.com",
        )

        factory = APIRequestFactory()
        request = factory.post(
            "/api/stock/receive/",
            {
                "product": product.pk,
                "supplier": supplier.pk,
                "quantity": 10,
            },
            format="json",
        )
        force_authenticate(request, user=user)

        def fail_history_save(*args, **kwargs):
            current_stock = Product.objects.get(
                pk=product.pk
            ).stock_quantity

            self.assertEqual(current_stock, 15)
            raise RuntimeError("Simulated history save failure")

        with patch(
            "inventory.views.InventoryTransaction.objects.create",
            side_effect=fail_history_save,
        ):
            with self.assertRaisesMessage(
                RuntimeError,
                "Simulated history save failure",
            ):
                ReceiveStockView.as_view()(request)

        product.refresh_from_db()

        self.assertEqual(product.stock_quantity, 5)
        self.assertEqual(
            InventoryTransaction.objects.filter(
                product=product
            ).count(),
            0,
        )