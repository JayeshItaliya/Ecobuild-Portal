from rest_framework.serializers import ModelSerializer

from cms.models.gallery import GalleryCategory


class GalleryCategorySerializer(ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = "__all__"


class GalleryCategoryResponseSerializer(ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = ["id", "name", "type", "description"]


class GalleryCategoryListSerializer(ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = ["id", "name", "type"]
