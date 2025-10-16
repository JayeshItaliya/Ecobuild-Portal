from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models.gallery import Gallery
from cms.serializers.gallery_category_serializer import GalleryCategoryListSerializer
from utils.storage import get_file_url
from utils.storage import validate_file


class GallerySerializer(ModelSerializer):
    """
    Serializer for creating/updating Gallery items.
    Includes validation for image and video files.
    """

    class Meta:
        model = Gallery
        fields = "__all__"

    def validate_image(self, value):
        """Validate image file type and size"""
        if value:
            is_valid, error_msg = validate_file(value, file_type="image")
            if not is_valid:
                raise serializers.ValidationError(error_msg)
        return value

    def validate_video(self, value):
        """Validate video file type and size"""
        if value:
            is_valid, error_msg = validate_file(value, file_type="video")
            if not is_valid:
                raise serializers.ValidationError(error_msg)
        return value


class GalleryResponseSerializer(ModelSerializer):
    """
    Serializer for Gallery responses with full URLs for media files.
    """

    category = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ["id", "image", "image_url", "category", "video", "video_url"]

    def get_category(self, obj):
        lang_code = self.context.get("lang_code", "en")
        serializer = GalleryCategoryListSerializer(
            obj.category, context={"lang_code": lang_code}
        )
        return serializer.data

    def get_image_url(self, obj):
        """Get full URL for image (works for both local and S3)"""
        if obj.image:
            return get_file_url(obj.image.name)
        return None

    def get_video_url(self, obj):
        """Get full URL for video (works for both local and S3)"""
        if obj.video:
            return get_file_url(obj.video.name)
        return None


class GalleryListSerializer(ModelSerializer):
    """
    Serializer for listing Gallery items with full media URLs.
    """

    category = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = ["id", "image", "image_url", "category", "video", "video_url"]

    def get_category(self, obj):
        # Pass lang_code from parent serializer context!
        lang_code = self.context.get("lang_code", "en")
        serializer = GalleryCategoryListSerializer(
            obj.category, context={"lang_code": lang_code}
        )
        return serializer.data

    def get_image_url(self, obj):
        """Get full URL for image (works for both local and S3)"""
        if obj.image:
            return get_file_url(obj.image.name)
        return None

    def get_video_url(self, obj):
        """Get full URL for video (works for both local and S3)"""
        if obj.video:
            return get_file_url(obj.video.name)
        return None
