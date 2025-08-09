from rest_framework.serializers import ModelSerializer

from cms.models.product import ProductCategory


class ProductCategoryChildSerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name"]


class ProductCategorySerializer(ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductCategoryResponseSerializer(ModelSerializer):
    parent = ProductCategoryChildSerializer()

    class Meta:
        model = ProductCategory
        fields = ["id", "parent", "name"]

    def get_parent(self, obj):
        return obj.parent.name if obj.parent else None


class ProductCategoryListSerializer(ModelSerializer):
    children = ProductCategoryChildSerializer(many=True, read_only=True)
    parent = ProductCategoryChildSerializer()

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "parent", "children"]
