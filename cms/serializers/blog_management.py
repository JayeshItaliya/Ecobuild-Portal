import json

from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cms.models.blog import BlogPost
from cms.models.blog import Category
from cms.models.blog import Tag


class TagResponseSerializer(ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["name"] = parse_json_string(data.get("name"))
        return data

    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class CategoryResponseSerializer(ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["name"] = parse_json_string(data.get("name"))
        return data

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


def parse_json_string(value):
    if not isinstance(value, str):
        return value

    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return value

    if isinstance(parsed, (dict, list)):
        return parsed
    return value


class BlogManagementSerializer(ModelSerializer):
    category = serializers.CharField(required=False)
    tags = serializers.SerializerMethodField()

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

    def get_tags(self, obj):
        return [
            parse_json_string(tag_name)
            for tag_name in obj.tags.values_list("name", flat=True)
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["title"] = parse_json_string(data.get("title"))
        data["content"] = parse_json_string(data.get("content"))
        data["meta_title"] = parse_json_string(data.get("meta_title"))
        data["meta_description"] = parse_json_string(data.get("meta_description"))

        # Properly serialize category name
        if instance.category:
            data["category"] = parse_json_string(instance.category.name)
        else:
            data["category"] = None

        # Properly serialize tags list
        # data["tags"] = list(instance.tags.values_list("name", flat=True))

        return data


class BlogResponseSerializer(ModelSerializer):
    category = CategoryResponseSerializer()
    tags = TagResponseSerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["title"] = parse_json_string(data.get("title"))
        data["content"] = parse_json_string(data.get("content"))
        data["meta_title"] = parse_json_string(data.get("meta_title"))
        data["meta_description"] = parse_json_string(data.get("meta_description"))
        return data

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
