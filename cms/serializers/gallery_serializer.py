from rest_framework.serializers import ModelSerializer

from cms.models.gallery import Gallery
from cms.serializers.gallery_category_serializer import GalleryCategoryListSerializer


class GallerySerializer(ModelSerializer):
    class Meta:
        model = Gallery
        fields = "__all__"


class GalleryResponseSerializer(ModelSerializer):
    category = GalleryCategoryListSerializer()

    class Meta:
        model = Gallery
        fields = ["id", "image", "category", "video"]


class GalleryListSerializer(ModelSerializer):
    category = GalleryCategoryListSerializer()

    class Meta:
        model = Gallery
        fields = ["id", "image", "category", "video"]
