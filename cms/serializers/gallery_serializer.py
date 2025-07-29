from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField

from cms.models.gallery import Gallery
from cms.models.gallery import GalleryCategory


class GalleryCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for GalleryCategory model.
    """

    name = serializers.JSONField()
    description = serializers.JSONField(required=False)

    class Meta:
        model = GalleryCategory
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]


class GalleryCategoryResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer for GalleryCategory model with translated fields.
    """

    name = serializers.CharField()
    description = serializers.CharField(required=False)

    class Meta:
        model = GalleryCategory
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]


class GallerySerializer(serializers.ModelSerializer):
    """
    Serializer for Gallery model.
    """

    name = serializers.JSONField()
    description = serializers.JSONField(required=False)
    category = PrimaryKeyRelatedField(queryset=GalleryCategory.objects.all())

    class Meta:
        model = Gallery
        fields = [
            "id",
            "name",
            "description",
            "category",
            "image",
            "gallery_type",
            "created_at",
            "updated_at",
        ]


class GalleryResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer for Gallery model with translated fields.
    """

    name = serializers.CharField()
    description = serializers.CharField(required=False)
    category = GalleryCategoryResponseSerializer()

    class Meta:
        model = Gallery
        fields = [
            "id",
            "name",
            "description",
            "category",
            "image",
            "gallery_type",
            "created_at",
            "updated_at",
        ]
