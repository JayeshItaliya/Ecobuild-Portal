from rest_framework.serializers import ModelSerializer

from cms.models.broadcast_news import BroadcastNews
from cms.models.broadcast_news import BroadcastNewsDetail


class BroadcastNewsDetailSerializer(ModelSerializer):
    """
    Serializer for BroadcastNewsDetail - interview content line by line
    """

    class Meta:
        model = BroadcastNewsDetail
        fields = [
            "id",
            "speaker",
            "content",
            "timestamp",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BroadcastNewsListSerializer(ModelSerializer):
    """
    Serializer for listing broadcast news (summary view)
    """

    class Meta:
        model = BroadcastNews
        fields = [
            "id",
            "title",
            "slug",
            "channel_name",
            "interviewer_name",
            "interviewee_name",
            "interview_date",
            "broadcast_date",
            "description",
            "thumbnail_image",
            "status",
            "views_count",
            "duration",
            "is_featured",
            "display_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "views_count", "created_at", "updated_at"]


class BroadcastNewsDetailedSerializer(ModelSerializer):
    """
    Serializer for detailed broadcast news view with interview details
    """

    details = BroadcastNewsDetailSerializer(many=True, read_only=True)

    class Meta:
        model = BroadcastNews
        fields = [
            "id",
            "title",
            "slug",
            "channel_name",
            "interviewer_name",
            "interviewee_name",
            "interview_date",
            "broadcast_date",
            "description",
            "thumbnail_image",
            "video_url",
            "video_file",
            "status",
            "views_count",
            "duration",
            "meta_title",
            "meta_description",
            "is_featured",
            "display_order",
            "details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "views_count", "created_at", "updated_at"]


class BroadcastNewsCreateUpdateSerializer(ModelSerializer):
    """
    Serializer for creating and updating broadcast news
    """

    details = BroadcastNewsDetailSerializer(many=True, required=False)

    class Meta:
        model = BroadcastNews
        fields = [
            "id",
            "title",
            "slug",
            "channel_name",
            "interviewer_name",
            "interviewee_name",
            "interview_date",
            "broadcast_date",
            "description",
            "thumbnail_image",
            "video_url",
            "video_file",
            "status",
            "duration",
            "meta_title",
            "meta_description",
            "is_featured",
            "display_order",
            "details",
        ]
        read_only_fields = ["id", "slug"]

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])
        broadcast_news = BroadcastNews.objects.create(**validated_data)

        # Create interview details line by line
        for detail_data in details_data:
            BroadcastNewsDetail.objects.create(
                broadcast_news=broadcast_news, **detail_data
            )

        return broadcast_news

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        # Update broadcast news fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update details if provided
        if details_data is not None:
            # Delete existing details and create new ones
            instance.details.all().delete()
            for detail_data in details_data:
                BroadcastNewsDetail.objects.create(
                    broadcast_news=instance, **detail_data
                )

        return instance


class BroadcastNewsFeaturedSerializer(ModelSerializer):
    """
    Serializer for featured broadcast news (minimal fields)
    """

    class Meta:
        model = BroadcastNews
        fields = [
            "id",
            "title",
            "slug",
            "channel_name",
            "broadcast_date",
            "thumbnail_image",
            "description",
            "duration",
            "views_count",
        ]
        read_only_fields = ["id", "slug", "views_count"]
