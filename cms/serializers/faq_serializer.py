from rest_framework import serializers
from cms.models.faq import FAQ

class FAQSerializer(serializers.ModelSerializer):
    """
    Serializer for the FAQ model.
    Handles serialization and deserialization of FAQ instances.
    """

    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "is_active",
            "order",
        ]
        read_only_fields = ["id", "created_at"]


class FAQListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing FAQ instances.
    Used for read-only operations when listing FAQs.
    """

    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "is_active",
            "order",
        ]
