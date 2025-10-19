from rest_framework.serializers import ModelSerializer

from accounts.mixins import TranslatedField
from cms.models.product import Product, ProductGalleryImage, ProductSection
from cms.serializers.product.product_category_serializer import ProductCategoryChildSerializer

class ProductListSerializer(ModelSerializer):
    title = TranslatedField()
    class Meta:
        model = Product
        fields = ['id', 'title']
class ProductSectionSerializer(ModelSerializer):
    class Meta:
        model = ProductSection
        fields = "__all__"
        
class ProductSectionResponseSerializer(ModelSerializer):
    content_text = TranslatedField()
    product = ProductListSerializer()
    
    class Meta:
        model = ProductSection
        fields = ['id', 'product', 'order', 'section_type', 'content_text', 'content_image', 'content_file', 'image_position']
        
class ProductGallerySerializer(ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = "__all__"
        
class ProductGalleryResponseSerializer(ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = ['id', 'section', 'image', 'caption']
class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class ProductResponseSerializer(ModelSerializer):
    title =TranslatedField()
    subtitle = TranslatedField()
    sections = ProductSectionResponseSerializer(many=True, read_only=True,default=[])
    category = ProductCategoryChildSerializer()
    class Meta:
        model = Product
        fields = ['id', 'title', 'subtitle', 'category', 'sections']


