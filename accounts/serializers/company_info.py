from rest_framework import serializers

from accounts.models import CompanyInfo
from accounts.models import SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        required=False
    )  # for future use if we want id-based updates

    class Meta:
        model = SocialLink
        fields = ["id", "platform", "url", "icon", "is_active", "order"]


class CompanyInfoSerializer(serializers.ModelSerializer):
    social_links = SocialLinkSerializer(many=True, required=False)

    class Meta:
        model = CompanyInfo
        fields = [
            "id",
            "name",
            "address",
            "phone",
            "email",
            "description",
            "weekday_hours",
            "weekend_hours",
            "logo",
            "updated_at",
            "social_links",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")
        lang_code = None
        if request:
            lang_code = request.headers.get("Accept-Language", "en")

        # If translated instance already injected by mixin, keep values
        for field in CompanyInfo.TRANSLATABLE_FIELDS:
            value = getattr(instance, field, None)
            if isinstance(value, dict):  # still JSON (not replaced)
                data[field] = value.get(lang_code, value.get("en", ""))

        return data

    def create(self, validated_data):
        social_links_data = validated_data.pop("social_links", [])
        company_info = CompanyInfo.objects.create(**validated_data)

        for link_data in social_links_data:
            SocialLink.objects.create(company=company_info, **link_data)

        return company_info

    def update(self, instance, validated_data):
        social_links_data = validated_data.pop("social_links", None)

        # update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if social_links_data is not None:  # update only if passed
            instance.social_links.all().delete()
            for link_data in social_links_data:
                SocialLink.objects.create(company=instance, **link_data)

        return instance
