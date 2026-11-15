from django.db import models
from django.db.models import Q


class Supplier(models.Model):
    supplier_code = models.CharField(max_length=30, unique=True)
    supplier_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")

    class Meta:
        ordering = ["supplier_name"]
        constraints = [
            models.CheckConstraint(
                condition=~(Q(email="") & Q(phone="")),
                name="supplier_has_contact",
            ),
        ]

    def __str__(self):
        return self.supplier_name