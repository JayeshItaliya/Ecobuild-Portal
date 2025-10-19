from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models.gallery import GalleryCategory
from cms.serializers.base_choices_serializer import BaseChoicesListSerializer


class GalleryCategorySerializer(ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = "__all__"


class GalleryCategoryResponseSerializer(ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = ["id", "name", "type", "description"]


class GalleryCategoryListSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = GalleryCategory
        fields = ["id", "name", "type", "description"]

    def get_name(self, obj):
        lang_code = self.context.get("lang_code", "en")
        if isinstance(obj.name, dict):
            return obj.name.get(lang_code, next(iter(obj.name.values())))
        return obj.name

    def get_description(self, obj):
        lang_code = self.context.get("lang_code", "en")
        if isinstance(obj.description, dict):
            return obj.description.get(lang_code, next(iter(obj.description.values())))
        return obj.description


class GalleryCategoryChoicesSerializer(BaseChoicesListSerializer):

    class Meta(BaseChoicesListSerializer.Meta):
        model = GalleryCategory
