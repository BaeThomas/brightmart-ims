from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsManagerOrReadOnly
from .models import Supplier
from .serializers import SupplierSerializer


class SupplierListCreateView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    @extend_schema(
        responses={200: SupplierSerializer(many=True)},
    )
    def get(self, request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)

        return Response(serializer.data)

    @extend_schema(
        request=SupplierSerializer,
        responses={201: SupplierSerializer},
    )
    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class SupplierDetailView(APIView):
    permission_classes = [IsManagerOrReadOnly]

    @extend_schema(responses={200: SupplierSerializer})
    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(supplier)

        return Response(serializer.data)

    @extend_schema(
        request=SupplierSerializer,
        responses={200: SupplierSerializer},
    )
    def put(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)

        serializer = SupplierSerializer(
            supplier,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(
        request=SupplierSerializer,
        responses={200: SupplierSerializer},
    )
    def patch(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)

        serializer = SupplierSerializer(
            supplier,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)

        try:
            supplier.delete()
        except ProtectedError:
            raise ValidationError({
                "detail": (
                    "This supplier cannot be deleted because "
                    "it has inventory transactions."
                )
            })

        return Response(status=status.HTTP_204_NO_CONTENT)