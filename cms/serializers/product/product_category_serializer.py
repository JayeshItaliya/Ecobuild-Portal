from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models.product import ProductCategory


class ProductCategoryChildSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ["id", "name"]

    def get_name(self, obj):
        # Get language code from parent serializer context
        lang_code = self.context.get("lang_code", "en")
        return obj.name.get(lang_code, next(iter(obj.name.values())))


class ProductCategorySerializer(ModelSerializer):
    """For creating/updating categories"""

    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductCategoryResponseSerializer(ModelSerializer):
    parent = ProductCategoryChildSerializer()

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "parent"]


class ProductCategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = ProductCategoryChildSerializer()

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "parent", "children"]

    def get_children(self, obj):
        # Pass lang_code from context to each child for translation
        lang_code = self.context.get("lang_code", "en")
        children = obj.children.all()
        serializer = ProductCategoryChildSerializer(
            children, many=True, context={"lang_code": lang_code}
        )
        return serializer.data
