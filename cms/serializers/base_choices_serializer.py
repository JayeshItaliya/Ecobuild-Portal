from rest_framework.serializers import ModelSerializer

class BaseTemplateSerializer(ModelSerializer):
    class Meta:
        model = None


class BaseChoicesListSerializer(BaseTemplateSerializer):
    class Meta(BaseTemplateSerializer.Meta):
        fields = ["id", "name"]