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
    # category = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ["id", "image", "category", "video"]

    # def get_category(self, obj):
    #     # Pass lang_code from context to each child for translation
    #     lang_code = self.context.get("lang_code", "en")
    #     category = obj.category.all()
    #     serializer = GalleryCategoryListSerializer(
    #         category, many=True, context={"lang_code": lang_code}
    #     )
    #     return serializer.data
