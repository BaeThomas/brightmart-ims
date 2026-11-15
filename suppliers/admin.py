from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "supplier_code",
        "supplier_name",
        "email",
        "phone",
    )
    search_fields = ("supplier_code", "supplier_name")