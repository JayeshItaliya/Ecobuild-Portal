import json
import logging
import re

from django.core.files.uploadedfile import UploadedFile
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
from backend.utils import generic_response
from cms.models.product import Product
from cms.serializers.product.product_serializer import ProductResponseSerializer
from cms.serializers.product.product_serializer import ProductSerializer


class BaseProductAPIView(TranslatedResponseMixin):
    """
    Base API view for Product with queryset, serializers, and filters.
    """

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = ProductSerializer
    response_serializer_class = ProductResponseSerializer
    queryset = (
        Product.objects.select_related("category", "category__parent")
        .prefetch_related("sections", "sections__gallery_images")
        .all()
        .order_by("-created_at")
    )
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]


def parse_form_data_for_product(data):
    """
    Parse FormData to handle JSON strings for nested fields and file uploads.

    Supports file upload naming convention:
    - sections_{index}_content_image (for section's main image)
    - sections_{index}_content_file (for section's file)
    - sections_{index}_gallery_images_{gallery_index}_image (for gallery images)
    - sections_{index}_gallery_images_{gallery_index}_caption (for gallery image captions)

    Where {index} is the array position (0, 1, 2, etc.)
    """
    if not isinstance(data, dict):
        logging.error(
            f"Expected dict but got {type(data)} in parse_form_data_for_product"
        )
        return data

    parsed_data = {}
    separate_files = {}  # Store separate file uploads for later mapping

    # Fields that should be parsed as JSON (translatable fields and nested lists)
    json_fields = ["title", "subtitle", "sections"]

    for key, value in data.items():
        try:
            # Ensure key is a string
            if not isinstance(key, str):
                key = str(key)

            # Check if this is a file object
            if isinstance(value, (UploadedFile, bytes)) or hasattr(value, "read"):
                # Check if this is a separate file upload with naming convention
                # Supports both underscore and bracket notation
                if key.startswith("sections_") or key.startswith("sections["):
                    separate_files[key] = value
                else:
                    parsed_data[key] = value
            elif key in json_fields and isinstance(value, str):
                # Parse JSON strings for nested/translatable fields
                try:
                    value_str = value.strip()
                    if value_str.startswith(("{", "[")):
                        parsed_value = json.loads(value)
                        parsed_data[key] = parsed_value
                    else:
                        parsed_data[key] = value
                except (json.JSONDecodeError, AttributeError, UnicodeDecodeError) as e:
                    logging.warning(f"Failed to parse JSON for field {key}: {e}")
                    parsed_data[key] = value
            else:
                parsed_data[key] = value
        except Exception as e:
            logging.error(f"Error processing field {key}: {e}")
            parsed_data[key] = value

    # Map separate file uploads to nested sections array
    if separate_files:
        parsed_data = _map_files_to_sections(parsed_data, separate_files)

    return parsed_data


def _map_files_to_sections(parsed_data, separate_files):
    """
    Map separate file uploads to the sections array using naming convention.

    Supports both formats:
    - Underscore format: sections_{section_index}_{field_name}
      Example: sections_0_content_image, sections_0_content_file
    - Bracket format: sections[{section_index}][{field_name}]
      Example: sections[0][content_image], sections[1][content_image]
    """
    # Ensure sections array exists
    if "sections" not in parsed_data:
        parsed_data["sections"] = []

    for key, file_value in separate_files.items():
        section_index = None
        field_name = None
        is_gallery = False
        gallery_index = None
        gallery_field = None

        # Try bracket notation first: sections[0][content_image] or sections[0][gallery_images][0][image]
        if key.startswith("sections[") and "]" in key:
            try:
                # Match sections[index][field] or sections[index][gallery_images][gallery_index][field]
                # Pattern 1: sections[0][gallery_images][0][image]
                gallery_pattern = r'sections\[(\d+)\]\[gallery_images\]\[(\d+)\]\[([^\]]+)\]'
                gallery_match = re.match(gallery_pattern, key)
                if gallery_match:
                    section_index = int(gallery_match.group(1))
                    gallery_index = int(gallery_match.group(2))
                    gallery_field = gallery_match.group(3)
                    is_gallery = True
                else:
                    # Pattern 2: sections[0][content_image] or sections[0][content_file]
                    simple_pattern = r'sections\[(\d+)\]\[([^\]]+)\]'
                    simple_match = re.match(simple_pattern, key)
                    if simple_match:
                        section_index = int(simple_match.group(1))
                        field_name = simple_match.group(2)
            except (ValueError, IndexError, AttributeError) as e:
                logging.warning(f"Could not parse bracket notation for field {key}: {e}")
                # Fall through to try underscore notation

        # Try underscore notation: sections_0_content_image
        if section_index is None:
            parts = key.split("_")
            if len(parts) >= 3 and parts[0] == "sections":
                try:
                    section_index = int(parts[1])
                    field_name = "_".join(parts[2:])

                    # Handle gallery images: sections_0_gallery_images_0_image
                    if "gallery_images" in field_name and len(parts) >= 5:
                        is_gallery = True
                        gallery_index = int(parts[3])
                        gallery_field = parts[4]  # 'image' or 'caption'
                        field_name = None  # Clear field_name since it's a gallery image
                except (ValueError, IndexError) as e:
                    logging.warning(f"Could not parse underscore notation for field {key}: {e}")
                    continue

        # Process the file if we successfully parsed the key
        if section_index is not None:
            try:
                # Ensure we have enough sections in the list
                while len(parsed_data["sections"]) <= section_index:
                    parsed_data["sections"].append({})

                if is_gallery and gallery_index is not None and gallery_field:
                    # Handle gallery images
                    if "gallery_images" not in parsed_data["sections"][section_index]:
                        parsed_data["sections"][section_index]["gallery_images"] = []

                    while (
                        len(parsed_data["sections"][section_index]["gallery_images"])
                        <= gallery_index
                    ):
                        parsed_data["sections"][section_index]["gallery_images"].append(
                            {}
                        )

                    parsed_data["sections"][section_index]["gallery_images"][
                        gallery_index
                    ][gallery_field] = file_value
                elif field_name:
                    # Regular section field (content_image, content_file, etc.)
                    parsed_data["sections"][section_index][field_name] = file_value
            except (ValueError, IndexError) as e:
                logging.warning(f"Could not map file field {key} to sections: {e}")
                continue

    return parsed_data


class ProductListCreateAPIView(BaseProductAPIView, ListCreateAPIView):
    """API view to list and create products."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        """
        List products with optional filtering by category and subcategory.

        Query Parameters:
            - category: Filter by category ID (can be parent category or subcategory)
            - parent_category: Filter by parent category ID only
            - subcategory: Filter by subcategory ID only (category with a parent)
        """
        queryset = self.get_queryset()

        # Filter by category (handles both parent and subcategory)
        category_id = request.query_params.get("category")
        if category_id:
            try:
                queryset = queryset.filter(category_id=category_id)
            except ValueError:
                return generic_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_message="Invalid category ID format.",
                    data={},
                )

        # Filter by parent category only
        parent_category_id = request.query_params.get("parent_category")
        if parent_category_id:
            try:
                queryset = queryset.filter(category__parent_id=parent_category_id)
            except ValueError:
                return generic_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_message="Invalid parent category ID format.",
                    data={},
                )

        # Filter by subcategory only (category with a parent)
        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            try:
                queryset = queryset.filter(
                    category_id=subcategory_id, category__parent__isnull=False
                )
            except ValueError:
                return generic_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_message="Invalid subcategory ID format.",
                    data={},
                )

        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset) or queryset
        products = self.translate_queryset(queryset, lang_code)

        serializer = self.response_serializer_class(
            products, many=True, context={"request": request}
        )
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Products fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        """
        Create a new product with sections in one API call.

        Supports both JSON and FormData:
        - JSON: Send Content-Type: application/json with JSON payload
        - FormData: Send Content-Type: multipart/form-data with JSON strings for nested fields

        For FormData, send JSON strings for nested/translatable fields:
        - title='{"en": "Product Title", "ar": "عنوان المنتج"}'
        - subtitle='{"en": "Subtitle", "ar": "العنوان الفرعي"}'
        - sections='[{"order": 1, "section_type": "Text", "content_text": {"en": "..."}}]'
        - category=<category_id>

        File uploads for sections use naming convention:
        - sections_0_content_image (for first section's main image)
        - sections_0_content_file (for first section's file)
        - sections_0_gallery_images_0_image (for first section's first gallery image)
        - sections_0_gallery_images_0_caption (for first section's first gallery image caption)
        """
        data = request.data
        content_type = getattr(request, "content_type", "") or request.META.get(
            "CONTENT_TYPE", ""
        )

        # Check if this is FormData and needs parsing
        is_form_data = "multipart/form-data" in content_type

        if is_form_data:
            try:
                data = parse_form_data_for_product(data)
            except Exception as e:
                logging.error(f"Error parsing form data: {e}")
                return generic_response(
                    message="Error parsing form data",
                    data={"error": str(e)},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Translate instance based on user's language preference
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(instance, lang_code)

        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Product created successfully with sections.",
            data=response_data,
        )


class ProductRetrieveUpdateDestroyAPIView(
    BaseProductAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific product."""

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific product."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update a specific product."""
        instance = self.get_object()

        # Parse form data if it's multipart/form-data
        data = request.data
        content_type = getattr(request, "content_type", "") or request.META.get(
            "CONTENT_TYPE", ""
        )

        if "multipart/form-data" in content_type:
            try:
                data = parse_form_data_for_product(data)
            except Exception as e:
                logging.error(f"Error parsing form data: {e}")
                return generic_response(
                    message="Error parsing form data",
                    data={"error": str(e)},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Translate instance based on user's language preference
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(instance, lang_code)

        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific product."""
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Product deleted successfully.",
        )
