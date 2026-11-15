from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    ProductDetailView,
    ProductListCreateView,
    ReceiveStockView,
    IssueStockView,
    LowStockView,
    InventoryTransactionListView,
    InventoryTransactionDetailView,
)

urlpatterns = [
    path(
        "stock/receive/",
        ReceiveStockView.as_view(),
        name="receive-stock",
    ),
    path(
        "stock/issue/",
        IssueStockView.as_view(),
        name="issue-stock",
    ),
    path(
        "products/low-stock/",
        LowStockView.as_view(),
        name="low-stock",
    ),
    path(
       "categories/",
       CategoryListCreateView.as_view(),
       name="category-list-create",
    ),
    path(
       "categories/<int:pk>/",
       CategoryDetailView.as_view(),
       name="category-detail",
    ),
    path(
    "products/",
    ProductListCreateView.as_view(),
    name="product-list-create",
    ),  
    path(
    "products/<int:pk>/",
    ProductDetailView.as_view(),
    name="product-detail",
    ),

    path(
    "transactions/",
    InventoryTransactionListView.as_view(),
    name="transaction-list",
     )    ,
     path(
    "transactions/<int:pk>/",
    InventoryTransactionDetailView.as_view(),
    name="transaction-detail",
    ),
]