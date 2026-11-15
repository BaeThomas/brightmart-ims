from django.contrib import admin

from .models import Category, Product, InventoryTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name")
    search_fields = ("category_name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
         "id",
        "sku",
        "product_name",
        "category",
        "price",
        "stock_quantity",
        "reorder_level",
    )
    list_filter = ("category",)
    search_fields = ("sku", "product_name")
    readonly_fields = ("stock_quantity",)


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "transaction_type",
        "quantity",
        "supplier",
        "user",
        "transaction_date",
    )
    list_filter = ("transaction_type",)
    search_fields = ("product__sku", "product__product_name")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False