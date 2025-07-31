from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models.module import BlogPost
from cms.models.module import Category
from cms.models.module import Tag


class TagResponseSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class CategoryResponseSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class BlogManagementSerializer(ModelSerializer):
    category = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

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
        category_name = validated_data.pop("category", None)
        tag_names = validated_data.pop("tags", [])

        # Handle category
        category_instance = None
        if category_name:
            category_instance, _ = Category.objects.get_or_create(
                name=category_name, defaults={"slug": slugify(category_name)}
            )

        # Create blog post without tags first
        blog_post = BlogPost.objects.create(**validated_data)
        blog_post.category = category_instance
        blog_post.save()

        # Handle tags
        tags = []
        for tag_name in tag_names:
            tag_instance, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"slug": slugify(tag_name)}
            )
            tags.append(tag_instance)

        blog_post.tags.set(tags)
        return blog_post

    def update(self, instance, validated_data):
        category_name = validated_data.pop("category", None)
        tags_list = validated_data.pop("tags", None)  # May be None for partial update

        # Update category if provided
        if category_name is not None:
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"slug": slugify(category_name)}
            )
            instance.category = category

        # Update tags if provided
        if tags_list is not None:
            tags = []
            for tag_name in tags_list:
                tag, _ = Tag.objects.get_or_create(
                    name=tag_name, defaults={"slug": slugify(tag_name)}
                )
                tags.append(tag)
            instance.tags.set(tags)

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BlogResponseSerializer(ModelSerializer):
    category = CategoryResponseSerializer()
    tags = TagResponseSerializer(many=True)

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
