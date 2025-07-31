from rest_framework import serializers

from cms.models.module import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the ContactMessage model.
    Handles serialization and deserialization of ContactMessage instances.
    """

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "subject",
            "message",
            "created_at",
            "is_read",
        ]
        read_only_fields = ["id", "created_at", "is_read"]


class ContactMessageListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing ContactMessage instances.
    Used for read-only operations when listing contact messages.
    """

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "name",
            "email",
            "subject",
            "created_at",
            "is_read",
        ]
