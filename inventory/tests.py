from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from inventory.models import Category, Product, InventoryTransaction
from inventory.views import (
    ReceiveStockView,
    IssueStockView,
    LowStockView,
)
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

class InventoryBusinessRuleTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = get_user_model().objects.create_user(
            username="inventory_tester",
            password="TestPassword123!",
            role="STAFF",
        )

        self.category = Category.objects.create(
            category_name="Test Category"
        )

        self.product = Product.objects.create(
            category=self.category,
            sku="UNIT-001",
            product_name="Test Product",
            price="100.00",
            stock_quantity=10,
            reorder_level=5,
        )

        self.supplier = Supplier.objects.create(
            supplier_code="UNIT-SUP-001",
            supplier_name="Test Supplier",
            email="supplier@example.com",
        )

    def set_stock(self, quantity):
        self.product.stock_quantity = quantity
        self.product.save(update_fields=["stock_quantity"])

    def submit_stock(self, operation, quantity):
        data = {
            "product": self.product.pk,
            "quantity": quantity,
        }

        if operation == "receive":
            data["supplier"] = self.supplier.pk
            view = ReceiveStockView
        else:
            view = IssueStockView

        request = self.factory.post(
            f"/api/stock/{operation}/",
            data,
            format="json",
        )
        force_authenticate(request, user=self.user)

        return view.as_view()(request)

    def assert_stock(self, expected):
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, expected)

    def assert_transaction(self, response, kind, quantity, supplier_id):
        records = InventoryTransaction.objects.filter(
            product=self.product
        )
        self.assertEqual(records.count(), 1)

        record = records.get()
        self.assertEqual(record.pk, response.data["id"])
        self.assertEqual(record.transaction_type, kind)
        self.assertEqual(record.quantity, quantity)
        self.assertEqual(record.user_id, self.user.pk)
        self.assertEqual(record.supplier_id, supplier_id)
        self.assertIsNotNone(record.transaction_date)

    def test_ut01_receive_stock(self):
        response = self.submit_stock("receive", 5)

        self.assertEqual(response.status_code, 201)
        self.assert_stock(15)
        self.assert_transaction(
            response, "RECEIVE", 5, self.supplier.pk
        )

    def test_ut02_issue_stock(self):
        response = self.submit_stock("issue", 3)

        self.assertEqual(response.status_code, 201)
        self.assert_stock(7)
        self.assert_transaction(response, "ISSUE", 3, None)

    def test_ut03_insufficient_stock(self):
        self.set_stock(5)

        response = self.submit_stock("issue", 6)

        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.data)
        self.assert_stock(5)
        self.assertEqual(InventoryTransaction.objects.count(), 0)

    def test_ut04_issue_exact_stock(self):
        self.set_stock(5)

        response = self.submit_stock("issue", 5)

        self.assertEqual(response.status_code, 201)
        self.assert_stock(0)
        self.assert_transaction(response, "ISSUE", 5, None)

    def test_ut05_quantity_validation(self):
        for operation in ("receive", "issue"):
            for quantity in (0, -1, 1.5):
                with self.subTest(
                    operation=operation, quantity=quantity
                ):
                    response = self.submit_stock(operation, quantity)

                    self.assertEqual(response.status_code, 400)
                    self.assertIn("quantity", response.data)
                    self.assert_stock(10)
                    self.assertEqual(
                        InventoryTransaction.objects.count(), 0
                    )

        # Check the smallest valid quantity for both operations.
        for operation in ("receive", "issue"):
            with self.subTest(operation=operation, quantity=1):
                self.set_stock(10)
                before_count = InventoryTransaction.objects.count()

                response = self.submit_stock(operation, 1)

                self.assertEqual(response.status_code, 201)
                expected_stock = 11 if operation == "receive" else 9
                self.assert_stock(expected_stock)
                self.assertEqual(
                    InventoryTransaction.objects.count(),
                    before_count + 1,
                )

                record = InventoryTransaction.objects.get(
                    pk=response.data["id"]
                )
                self.assertEqual(record.quantity, 1)
                self.assertEqual(
                    record.transaction_type, operation.upper()
                )

    def test_ut06_low_stock_boundary(self):
        for quantity in (4, 5, 6):
            with self.subTest(stock_quantity=quantity):
                self.set_stock(quantity)

                request = self.factory.get(
                    "/api/products/low-stock/"
                )
                force_authenticate(request, user=self.user)
                response = LowStockView.as_view()(request)

                self.assertEqual(response.status_code, 200)

                returned_ids = {
                    product["id"] for product in response.data
                }
                expected_ids = (
                    {self.product.pk} if quantity <= 5 else set()
                )
                self.assertEqual(returned_ids, expected_ids)