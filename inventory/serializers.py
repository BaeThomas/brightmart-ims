from rest_framework import serializers

from .models import Category, Product ,InventoryTransaction
from suppliers.models import Supplier



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category_name"]
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.category_name",
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "sku",
            "product_name",
            "price",
            "stock_quantity",
            "reorder_level",
        ]
        read_only_fields = [
            "id",
            "stock_quantity",
        ]
        extra_kwargs = {
            "price": {"min_value": 0},
            "reorder_level": {"min_value": 0},
        }

class ReceiveStockSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
    )
    quantity = serializers.IntegerField(min_value=1)


class IssueStockSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )
    quantity = serializers.IntegerField(min_value=1)

class InventoryTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.product_name",
        read_only=True,
    )
    sku = serializers.CharField(
        source="product.sku",
        read_only=True,
    )
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    supplier_name = serializers.CharField(
        source="supplier.supplier_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "product",
            "product_name",
            "sku",
            "user",
            "username",
            "supplier",
            "supplier_name",
            "transaction_type",
            "quantity",
            "transaction_date",
        ]
        read_only_fields = fields