from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from accounts.mixins import TranslatedField
from cms.models.product import Product
from cms.models.product import ProductCategory
from cms.models.product import ProductGalleryImage
from cms.models.product import ProductSection
from cms.serializers.product.product_category_serializer import (
    ProductCategoryChildSerializer,
)


class ProductListSerializer(ModelSerializer):
    title = TranslatedField()

    class Meta:
        model = Product
        fields = ["id", "title"]


class ProductSectionSerializer(ModelSerializer):
    class Meta:
        model = ProductSection
        fields = "__all__"


class ProductSectionResponseSerializer(ModelSerializer):
    content_text = TranslatedField()
    product = ProductListSerializer()

    class Meta:
        model = ProductSection
        fields = [
            "id",
            "product",
            "order",
            "section_type",
            "content_text",
            "content_image",
            "content_file",
            "image_position",
        ]


class ProductGallerySerializer(ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = "__all__"


class ProductGalleryResponseSerializer(ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = ["id", "section", "image", "caption"]


class ProductSerializer(ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        error_messages={
            "does_not_exist": "Product category with id {pk_value} does not exist.",
            "incorrect_type": "Category must be a valid UUID.",
        },
    )

    class Meta:
        model = Product
        fields = ["title", "subtitle", "category"]


class ProductResponseSerializer(ModelSerializer):
    title = TranslatedField()
    subtitle = TranslatedField()
    sections = ProductSectionResponseSerializer(many=True, read_only=True, default=[])
    category = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "subtitle",
            "category",
            "parent_category",
            "sections",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        """Get category with proper translation using nested serializer"""
        if not obj.category:
            return None
        request = self.context.get("request")
        lang_code = "en"
        if request:
            lang_code = request.headers.get("Accept-Language", "en").lower()
        serializer = ProductCategoryChildSerializer(
            obj.category, context={"lang_code": lang_code}
        )
        return serializer.data

    def get_parent_category(self, obj):
        """Get parent category if category is a subcategory"""
        if not obj.category or not obj.category.parent:
            return None
        request = self.context.get("request")
        lang_code = "en"
        if request:
            lang_code = request.headers.get("Accept-Language", "en").lower()
        serializer = ProductCategoryChildSerializer(
            obj.category.parent, context={"lang_code": lang_code}
        )
        return serializer.data
