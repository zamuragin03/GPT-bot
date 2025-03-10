import uuid
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class PromocodeDTO(serializers.Serializer):
    external_id = serializers.CharField()
    promocode_text = serializers.CharField()
    def validate_promocode_text(self, value):
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValidationError("Invalid code")
        return value