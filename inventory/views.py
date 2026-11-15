from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema 
from rest_framework.exceptions import ValidationError
from django.db.models import F
from accounts.permissions import (
    IsInventoryUser,
    IsManagerOrReadOnly,
)
from django.shortcuts import get_object_or_404
from django.db.models.deletion import ProtectedError

from .models import Category, Product, InventoryTransaction
from .serializers import (
    ProductSerializer,
    ReceiveStockSerializer,
    IssueStockSerializer,
    InventoryTransactionSerializer,
    CategorySerializer,
)


class ReceiveStockView(APIView):
    permission_classes = [IsInventoryUser]

    @extend_schema(
        request=ReceiveStockSerializer,
        responses={201: InventoryTransactionSerializer},
    )
    def post(self, request):
        serializer = ReceiveStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        supplier = serializer.validated_data["supplier"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            product = Product.objects.select_for_update().get(
                pk=product.pk
            )

            product.stock_quantity += quantity
            product.save(update_fields=["stock_quantity"])

            stock_transaction = InventoryTransaction.objects.create(
                product=product,
                supplier=supplier,
                user=request.user,
                transaction_type=InventoryTransaction.TransactionType.RECEIVE,
                quantity=quantity,
            )

        result = InventoryTransactionSerializer(stock_transaction)

        return Response(result.data, status=status.HTTP_201_CREATED)

class IssueStockView(APIView):
    permission_classes = [IsInventoryUser]

    @extend_schema(
        request=IssueStockSerializer,
        responses={201: InventoryTransactionSerializer},
    )
    def post(self, request):
        serializer = IssueStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            product = Product.objects.select_for_update().get(
                pk=product.pk
            )

            if quantity > product.stock_quantity:
                raise ValidationError({
                    "quantity": (
                        "Insufficient stock. "
                        f"Available quantity: {product.stock_quantity}."
                    )
                })

            product.stock_quantity -= quantity
            product.save(update_fields=["stock_quantity"])

            stock_transaction = InventoryTransaction.objects.create(
                product=product,
                supplier=None,
                user=request.user,
                transaction_type=InventoryTransaction.TransactionType.ISSUE,
                quantity=quantity,
            )

        result = InventoryTransactionSerializer(stock_transaction)

        return Response(result.data, status=status.HTTP_201_CREATED)

class LowStockView(APIView):
    permission_classes = [IsInventoryUser]

    @extend_schema(
        responses={200: ProductSerializer(many=True)},
    )
    def get(self, request):
        products = Product.objects.select_related("category").filter(
            stock_quantity__lte=F("reorder_level")
        )

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

class CategoryListCreateView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    @extend_schema(
        responses={200: CategorySerializer(many=True)},
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={201: CategorySerializer},
    )
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

class CategoryDetailView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    @extend_schema(responses={200: CategorySerializer})
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)

        return Response(serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={200: CategorySerializer},
    )
    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)

        serializer = CategorySerializer(
            category,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={200: CategorySerializer},
    )
    def patch(self, request, pk):
        category = get_object_or_404(Category, pk=pk)

        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)

        try:
            category.delete()
        except ProtectedError:
            raise ValidationError({
                "detail": (
                    "This category cannot be deleted because "
                    "products are linked to it."
                )
            })

        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductListCreateView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    @extend_schema(
        responses={200: ProductSerializer(many=True)},
    )
    def get(self, request):
        products = Product.objects.select_related("category").all()
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

    @extend_schema(
        request=ProductSerializer,
        responses={201: ProductSerializer},
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

class ProductDetailView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    @extend_schema(responses={200: ProductSerializer})
    def get(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related("category"),
            pk=pk,
        )
        serializer = ProductSerializer(product)

        return Response(serializer.data)

    @extend_schema(
        request=ProductSerializer,
        responses={200: ProductSerializer},
    )
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(
        request=ProductSerializer,
        responses={200: ProductSerializer},
    )
    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        try:
            product.delete()
        except ProtectedError:
            raise ValidationError({
                "detail": (
                    "This product cannot be deleted because "
                    "it has inventory transactions."
                )
            })

        return Response(status=status.HTTP_204_NO_CONTENT)

class InventoryTransactionListView(APIView):
    permission_classes = [IsInventoryUser]

    @extend_schema(
        responses={200: InventoryTransactionSerializer(many=True)},
    )
    def get(self, request):
        transactions = InventoryTransaction.objects.select_related(
            "product",
            "user",
            "supplier",
        ).all()

        serializer = InventoryTransactionSerializer(
            transactions,
            many=True,
        )

        return Response(serializer.data)


class InventoryTransactionDetailView(APIView):
    permission_classes = [IsInventoryUser]

    @extend_schema(
        responses={200: InventoryTransactionSerializer},
    )
    def get(self, request, pk):
        stock_transaction = get_object_or_404(
            InventoryTransaction.objects.select_related(
                "product",
                "user",
                "supplier",
            ),
            pk=pk,
        )

        serializer = InventoryTransactionSerializer(
            stock_transaction
        )

        return Response(serializer.data)