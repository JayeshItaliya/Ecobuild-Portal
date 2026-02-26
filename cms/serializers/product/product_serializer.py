from django.db import transaction
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
    """Serializer for reading ProductSection data."""

    class Meta:
        model = ProductSection
        fields = "__all__"


class ProductGallerySerializer(ModelSerializer):
    """Serializer for creating/updating ProductGalleryImage."""

    class Meta:
        model = ProductGalleryImage
        fields = ["image", "caption"]
        extra_kwargs = {
            "image": {"required": True},
            "caption": {"required": False, "allow_blank": True},
        }


class ProductGalleryResponseSerializer(ModelSerializer):
    class Meta:
        model = ProductGalleryImage
        fields = ["id", "section", "image", "caption"]


class ProductSectionWriteSerializer(ModelSerializer):
    """Serializer for creating/updating ProductSection with nested gallery images."""

    gallery_images = ProductGallerySerializer(
        many=True, required=False, allow_empty=True
    )

    class Meta:
        model = ProductSection
        fields = [
            "order",
            "section_type",
            "content_text",
            "content_image",
            "content_file",
            "image_position",
            "gallery_images",
        ]
        extra_kwargs = {
            "content_image": {"required": False, "allow_null": True},
            "content_file": {"required": False, "allow_null": True},
            "content_text": {"required": False, "allow_null": True},
            "image_position": {"required": False},
        }


class ProductSectionResponseSerializer(ModelSerializer):
    content_text = TranslatedField()
    product = ProductListSerializer()
    gallery_images = ProductGalleryResponseSerializer(many=True, read_only=True)

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
            "gallery_images",
        ]


class ProductSerializer(ModelSerializer):
    """Serializer for creating/updating Product with nested sections."""

    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        error_messages={
            "does_not_exist": "Product category with id {pk_value} does not exist.",
            "incorrect_type": "Category must be a valid UUID.",
        },
    )
    sections = ProductSectionWriteSerializer(
        many=True, required=False, allow_empty=True
    )

    class Meta:
        model = Product
        fields = ["title", "subtitle", "category", "sections"]
        extra_kwargs = {
            "title": {"required": True},
            "subtitle": {"required": False},
            "category": {"required": True},
        }

    @transaction.atomic
    def create(self, validated_data):
        """
        Create Product with all related sections in one transaction.
        Supports nested section creation with images, files, and gallery images.
        """
        try:
            # Extract nested sections data
            sections_data = validated_data.pop("sections", [])

            # Create Product
            product = Product.objects.create(**validated_data)

            # Create sections with their order
            for index, section_data in enumerate(sections_data):
                # Extract gallery images if present
                gallery_images_data = section_data.pop("gallery_images", [])

                # Set order if not provided (use index + 1)
                if "order" not in section_data or section_data["order"] is None:
                    section_data["order"] = index + 1

                # Create section
                section = ProductSection.objects.create(product=product, **section_data)

                # Create gallery images if provided
                if gallery_images_data:
                    for gallery_image_data in gallery_images_data:
                        ProductGalleryImage.objects.create(
                            section=section, **gallery_image_data
                        )

            return product

        except Exception as e:
            # Transaction will be rolled back automatically
            raise serializers.ValidationError(
                f"Error creating product with sections: {str(e)}"
            )

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update Product with all related sections in one transaction.
        Supports nested section updates with images, files, and gallery images.
        """
        try:
            # Extract nested sections data
            sections_data = validated_data.pop("sections", None)

            # Update basic product fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Handle sections update if provided
            if sections_data is not None:
                # Create mappings for existing sections by ID and order
                existing_sections_by_id = {
                    str(section.id): section for section in instance.sections.all()
                }
                existing_sections_by_order = {
                    section.order: section for section in instance.sections.all()
                }

                # Track processed sections to know which ones to delete
                processed_section_ids = set()
                processed_orders = set()

                # Update or create sections
                for index, section_data in enumerate(sections_data):
                    # Extract fields that shouldn't be set directly
                    section_id = section_data.pop("id", None)
                    section_data.pop("product", None)  # Remove nested product object

                    # Extract gallery images if present
                    gallery_images_data = section_data.pop("gallery_images", None)

                    # Get order, defaulting to index + 1 if not provided
                    order = section_data.pop("order", index + 1)
                    processed_orders.add(order)

                    # Try to find existing section by ID first, then by order
                    existing_section = None
                    if section_id:
                        existing_section = existing_sections_by_id.get(str(section_id))
                        if existing_section:
                            processed_section_ids.add(str(existing_section.id))

                    if not existing_section:
                        # Fall back to matching by order
                        existing_section = existing_sections_by_order.get(order)
                        if existing_section:
                            processed_section_ids.add(str(existing_section.id))

                    if existing_section:
                        existing_section.order = order
                        # Update existing section
                        for attr, value in section_data.items():
                            # Skip id and other read-only fields
                            if attr not in ["id", "product"]:
                                setattr(existing_section, attr, value)
                        existing_section.save()
                        section = existing_section
                    else:
                        # Create new section
                        section = ProductSection.objects.create(
                            product=instance, order=order, **section_data
                        )

                    # Handle gallery images if provided
                    if gallery_images_data is not None:
                        # Clear existing gallery images for this section
                        section.gallery_images.all().delete()

                        # Create new gallery images
                        for gallery_image_data in gallery_images_data:
                            ProductGalleryImage.objects.create(
                                section=section, **gallery_image_data
                            )

                # Delete sections that weren't in the update data
                all_existing_sections = set(existing_sections_by_id.values())
                sections_to_delete = [
                    section
                    for section in all_existing_sections
                    if str(section.id) not in processed_section_ids
                ]
                for section in sections_to_delete:
                    section.delete()

            return instance

        except Exception as e:
            # Transaction will be rolled back automatically
            raise serializers.ValidationError(
                f"Error updating product with sections: {str(e)}"
            )


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
