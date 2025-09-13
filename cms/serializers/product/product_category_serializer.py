from rest_framework import serializers

from cms.models.product import ProductCategory


class ProductCategoryChildSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ["id", "name"]

    def get_name(self, obj):
        # Get language code from parent serializer context
        lang_code = self.context.get("lang_code", "en")
        return obj.name.get(lang_code, next(iter(obj.name.values())))


class ProductCategoryChildWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name"]


class ProductCategorySerializer(serializers.ModelSerializer):
    """For creating/updating categories with nested children"""

    children = ProductCategoryChildWriteSerializer(many=True, required=False)

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "parent", "category_type", "children"]

    def create(self, validated_data):
        children_data = validated_data.pop("children", [])
        parent_category = ProductCategory.objects.create(**validated_data)

        for child_data in children_data:
            ProductCategory.objects.create(parent=parent_category, **child_data)

        return parent_category

    def update(self, instance, validated_data):
        children_data = validated_data.pop("children", [])

        # update parent fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # handle children update (simple strategy: update if id exists, else create)
        for child_data in children_data:
            child_id = child_data.get("id", None)
            if child_id:
                try:
                    child_instance = instance.children.get(id=child_id)
                    for attr, value in child_data.items():
                        setattr(child_instance, attr, value)
                    child_instance.save()
                except ProductCategory.DoesNotExist:
                    continue
            else:
                ProductCategory.objects.create(parent=instance, **child_data)

        return instance


class ProductCategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = ProductCategoryChildSerializer(allow_null=True)

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "parent", "category_type", "children"]

    def get_children(self, obj):
        # Pass lang_code from context to each child for translation
        lang_code = self.context.get("lang_code", "en")
        children = obj.children.all()
        serializer = ProductCategoryChildSerializer(
            children, many=True, context={"lang_code": lang_code}
        )
        return serializer.data
