from rest_framework import serializers

from cms.models.module import Document
from cms.models.module import DocumentAccess


class DocumentSerializer(serializers.ModelSerializer):
    name = serializers.JSONField()

    class Meta:
        model = Document
        fields = [
            "id",
            "name",
            "file",
            "file_type",
            "category",
            "file_url",
            "created_at",
            "updated_at",
        ]


class DocumentAccessSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    document_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentAccess
        fields = [
            "id",
            "user",
            "user_email",
            "document",
            "document_name",
            "access_level",
        ]

    def get_user_email(self, obj):
        return obj.user.email

    def get_document_name(self, obj):
        return obj.document.name.get("en", "Unnamed")
