from django.urls import path

from .views import SupplierListCreateView, SupplierDetailView

urlpatterns = [
    path(
        "suppliers/",
        SupplierListCreateView.as_view(),
        name="supplier-list-create",
    ),
    path(
        "suppliers/<int:pk>/",
        SupplierDetailView.as_view(),
        name="supplier-detail",
    ),
]
