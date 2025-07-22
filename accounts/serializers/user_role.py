from rest_framework.serializers import ModelSerializer

from accounts.models import Role


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class RoleResponseSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]
