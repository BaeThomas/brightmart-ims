from rest_framework import serializers

from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "supplier_code",
            "supplier_name",
            "email",
            "phone",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        email = attrs.get(
            "email",
            getattr(self.instance, "email", ""),
        )
        phone = attrs.get(
            "phone",
            getattr(self.instance, "phone", ""),
        )

        if not email.strip() and not phone.strip():
            raise serializers.ValidationError(
                "Provide at least an email address or a phone number."
            )

        return attrs