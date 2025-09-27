from rest_framework.response import Response
from rest_framework import status
from accounts.mixins import TranslatedResponseMixin
from cms.models.product import Product
from cms.serializers.product.product_serializer import ProductSerializer, ProductSectionSerializer, ProductGallerySerializer, ProductResponseSerializer, ProductSectionResponseSerializer, ProductGalleryResponseSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from backend.utils import generic_response

class BaseProductAPIView(TranslatedResponseMixin):
    serializer_class = ProductSerializer
    response_serializer_class = ProductResponseSerializer
    queryset = Product.objects.all()
    
    
    
class ProductListCreateAPIView(BaseProductAPIView,ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        products = self.get_queryset()
        serializer = self.response_serializer_class(products, many=True, context={"request": request})
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Products fetched successfully",
            data=serializer.data,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = self.response_serializer_class(product)
        
            return generic_response(
                status_code=status.HTTP_201_CREATED,
                message="Product created successfully.",
                data=response_serializer.data,
            )
        
        return generic_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_message="Product creation failed.",
            data=serializer.errors,
        )                 
 
class ProductRetrieveUpdateDestroyAPIView(BaseProductAPIView, RetrieveUpdateDestroyAPIView):
    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        product = self.get_object()
        instance = self.translate_instance(product, lang_code)

        response_data = self.response_serializer_class(instance, context={"request": request}).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product fetched successfully",
            data=response_data,
        )

    def put(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.serializer_class(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            response_serializer = self.response_serializer_class(updated_product)
            return generic_response(
                status_code=status.HTTP_200_OK,
                message="Product updated successfully.",
                data=response_serializer.data,
            )
        return generic_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_message="Product update failed.",
            data=serializer.errors,
        )

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Product deleted successfully.",
        )
        
        
[
    {"id","name"},
]