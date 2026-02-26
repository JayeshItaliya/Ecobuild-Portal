from django.db import transaction
from rest_framework import serializers

from accounts.enums import PlatformChoices
from accounts.models import CompanyInfo
from accounts.models import SocialLink


class SocialLinkSerializer(serializers.ModelSerializer):
    platform = serializers.CharField()
    id = serializers.IntegerField(
        required=False
    )  # for future use if we want id-based updates

    class Meta:
        model = SocialLink
        fields = ["id", "platform", "url", "icon", "is_active"]

    def validate_platform(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Platform must be a string.")

        normalized = value.strip().strip('"').strip("'")
        for choice in PlatformChoices.values:
            if normalized.lower() == choice.lower():
                return choice
        raise serializers.ValidationError(f'"{normalized}" is not a valid choice.')


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

    @transaction.atomic
    def create(self, validated_data):
        social_links_data = validated_data.pop("social_links", [])
        company_info = CompanyInfo.objects.create(**validated_data)

        for link_data in social_links_data:
            link_data.pop("id", None)
            SocialLink.objects.create(company=company_info, **link_data)

        return company_info

    @transaction.atomic
    def update(self, instance, validated_data):
        social_links_data = validated_data.pop("social_links", None)

        # update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if social_links_data is not None:
            existing_links = {
                str(link.id): link for link in instance.social_links.all()
            }
            processed_ids = set()

            for link_data in social_links_data:
                link_id = link_data.pop("id", None)

                if link_id and str(link_id) in existing_links:
                    social_link = existing_links[str(link_id)]
                    for attr, value in link_data.items():
                        setattr(social_link, attr, value)
                    social_link.save()
                    processed_ids.add(str(social_link.id))
                else:
                    new_link = SocialLink.objects.create(company=instance, **link_data)
                    processed_ids.add(str(new_link.id))

            stale_ids = set(existing_links.keys()) - processed_ids
            if stale_ids:
                instance.social_links.filter(id__in=stale_ids).delete()

        return instance
