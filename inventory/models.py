from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["category_name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    sku = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=150)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        editable=False,
    )
    reorder_level = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["product_name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="product_price_nonnegative",
            ),
        ]

    def __str__(self):
        return f"{self.sku} - {self.product_name}"



class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        RECEIVE = "RECEIVE", "Stock Received"
        ISSUE = "ISSUE", "Stock Issued"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(
        max_length=7,
        choices=TransactionType.choices,
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="inventory_transaction_quantity_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        transaction_type="RECEIVE",
                        supplier__isnull=False,
                    )
                    | Q(
                        transaction_type="ISSUE",
                        supplier__isnull=True,
                    )
                ),
                name="inventory_transaction_supplier_matches_type",
            ),
        ]

    def __str__(self):
        return (
            f"{self.transaction_type} - "
            f"{self.product.sku} - {self.quantity}"
        )