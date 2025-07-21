from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models import BlogPost
from cms.models import Category
from cms.models import Tag


class BlogManagementSerializer(ModelSerializer):
    category = serializers.CharField(required=False)
    tags = serializers.ListField(
        child=serializers.CharField(), required=False
    )  # tags as a list of strings

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "tags",
            "content",
            "featured_image",
            "meta_title",
            "meta_description",
            "status",
            "views_count",
            "reading_time",
        ]

    def create(self, validated_data):
        # Handle category
        category_name = validated_data.pop("category", None)
        if category_name:
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"slug": slugify(category_name)}
            )
            validated_data["category"] = category

        # Handle tags
        tags = validated_data.pop("tags", [])
        blog_post = super().create(validated_data)
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"slug": slugify(tag_name)}
            )
            blog_post.tags.add(tag)

        return blog_post

    def update(self, instance, validated_data):
        # Handle category
        category_name = validated_data.pop("category", None)
        if category_name:
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"slug": slugify(category_name)}
            )
            validated_data["category"] = category

        # Handle tags
        tags = validated_data.pop("tags", None)
        blog_post = super().update(instance, validated_data)
        if tags is not None:
            blog_post.tags.clear()
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_name, defaults={"slug": slugify(tag_name)}
                )
                blog_post.tags.add(tag)

        return blog_post
