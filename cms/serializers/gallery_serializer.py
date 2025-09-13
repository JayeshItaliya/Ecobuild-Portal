from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models.gallery import Gallery
from cms.serializers.gallery_category_serializer import GalleryCategoryListSerializer


class GallerySerializer(ModelSerializer):
    class Meta:
        model = Gallery
        fields = "__all__"


class GalleryResponseSerializer(ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ["id", "image", "category", "video"]

    def get_category(self, obj):
        lang_code = self.context.get("lang_code", "en")
        serializer = GalleryCategoryListSerializer(
            obj.category, context={"lang_code": lang_code}
        )
        return serializer.data


class GalleryListSerializer(ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ["id", "image", "category", "video"]

    def get_category(self, obj):
        # Pass lang_code from parent serializer context!
        lang_code = self.context.get("lang_code", "en")
        serializer = GalleryCategoryListSerializer(
            obj.category, context={"lang_code": lang_code}
        )
        return serializer.data
