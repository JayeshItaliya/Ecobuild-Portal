from rest_framework.serializers import ModelSerializer

from cms.models.product import ProductCategory


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"
